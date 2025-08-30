import torch
from torch import nn
import fmot
import time

from fmot.nn import (
    RNNCell,
    LSTMCell,
    GRUCell,
    RNN,
    LSTM,
    GRU,
    MultiLayerRNN,
    Sequential,
)
from fmot.nn import TemporalConv1d, SuperStructure, Sequencer
from fmot.nn import rsetattr, map_param_name
from fmot import ConvertedModel
from fmot import qat as Q
from torch import Tensor
from fmot import CONFIG


# this is a simple module defined only for internal testing purposes
class _BasicRNN(Sequencer):
    def __init__(self, input_size, hidden_size, batch_first=True):
        # state_shapes is a list of hidden-state shapes
        state_shapes = [[hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim=batch_dim, seq_dim=seq_dim)

        self.linear_ih = nn.Linear(input_size, hidden_size)
        self.linear_hh = nn.Linear(hidden_size, hidden_size)
        self.relu = nn.ReLU()

    @torch.jit.export
    def step(self, x_t: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        (h,) = state
        n = self.linear_ih(x_t) + self.linear_hh(h)
        h = torch.tanh(n)
        h = self.relu(h)

        return h, [h]


# This is a dummy class used for testing purposes
class _SuperBasic(SuperStructure):
    def __init__(self, input_size, hidden_size):
        super().__init__()

        self.layer = _BasicRNN(input_size, hidden_size)

    @torch.jit.export
    def forward(self, x):
        if x.sum(0) > 0:
            return x, [x]
        # x = torch.tanh(x)
        return self.layer(x)


class TestSequencers:
    def test_cell_running(self):
        r"""This tests if the step methods for cell unit
        Sequncers are running, and if the shape is correct.
        This does not check if the logic structure is correct
        """
        batch_size = 5
        input_size = 3
        hidden_size = 4
        x = torch.randn(batch_size, input_size)
        h = torch.randn(batch_size, hidden_size)
        c = torch.randn(batch_size, hidden_size)

        # Chekc if rnn cell is running
        my_rnn = RNNCell(input_size, hidden_size)
        output, h_list = my_rnn.step(x, [h])
        assert output.shape == h.shape

        # Check if lstm cell is running
        my_lstm = LSTMCell(input_size, hidden_size)
        output, h_list = my_lstm.step(x, [h, c])
        assert output.shape == h.shape

        # Check if gru step is running
        my_gru = GRUCell(input_size, hidden_size)
        output, h_list = my_gru.step(x, [h])
        assert output.shape == h.shape

    def test_seq_running(self):
        r"""This tests if the step methods for basic Sequencers
        are running, and if the shape is correct.
        This does not check if the logic structure is correct
        """
        batch_size = 5
        input_size = 3
        hidden_size = 4
        time_steps = 2
        h = torch.randn(batch_size, hidden_size)
        c = torch.randn(batch_size, hidden_size)
        num_layers = 2

        for batch_first in [True, False]:
            if batch_first:
                x = torch.randn(batch_size, time_steps, input_size)
            else:
                x = torch.randn(time_steps, batch_size, input_size)
            # Chekc if rnn is running
            my_rnn = RNN(input_size, hidden_size, num_layers, batch_first=batch_first)
            output, h_list = my_rnn(x, [h, h])
            assert h_list[0].shape == h.shape
            assert len(h_list) == num_layers

            # Check if lstm is running
            my_lstm = LSTM(
                input_size, hidden_size, num_layers, bias=True, batch_first=batch_first
            )
            output, h_list = my_lstm(x, [h, c, h, c])
            assert h_list[0].shape == h.shape
            assert len(h_list) == 2 * num_layers

            # Check if gru cell is running
            my_gru = GRU(
                input_size, hidden_size, num_layers, bias=True, batch_first=batch_first
            )
            output, h_list = my_gru(x, [h, h])
            assert h_list[0].shape == h.shape
            assert len(h_list) == num_layers

    def test_unit_logic_rnn(self):
        r"""This tests if the cells' logics are the same
        as in PyTorch
        """
        batch_size = 5
        input_size = 3
        hidden_size = 4
        time_steps = 2
        h = torch.randn(batch_size, hidden_size)
        c = torch.randn(batch_size, hidden_size)
        torch.manual_seed(0)

        epsilon = 10e-6
        # Check if RNN logic is correct
        num_layers_list = [1, 3]
        bias_list = [True, False]
        for num_layers in num_layers_list:
            for bias in bias_list:
                for batch_first in [True, False]:
                    if batch_first:
                        x = torch.randn(batch_size, time_steps, input_size)
                    else:
                        x = torch.randn(time_steps, batch_size, input_size)

                    torch_net = torch.nn.RNN(
                        input_size,
                        hidden_size,
                        num_layers=num_layers,
                        bias=True,
                        batch_first=batch_first,
                    )
                    dict = {}  # we can store the weights in this dict for convenience
                    for name, param in torch_net.named_parameters():
                        nn.init.normal_(param)
                        dict[name] = param

                    torch_output, h_n = torch_net(
                        x, torch.cat([h.unsqueeze(0)] * num_layers, 0)
                    )
                    torch_output = torch_output.squeeze(1)
                    my_net = RNN(
                        input_size,
                        hidden_size,
                        num_layers,
                        bias=True,
                        batch_first=batch_first,
                    )
                    # print(list(torch_rnn.named_parameters()))
                    for name, tensor in torch_net.named_parameters():
                        rsetattr(my_net, map_param_name(name), dict[name])

                    output, h_list = my_net(x, [h for _ in range(num_layers)])
                    assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

    def test_unit_logic_gru(self):
        batch_size = 5
        input_size = 3
        hidden_size = 4
        time_steps = 2
        x = torch.randn(batch_size, time_steps, input_size)
        h = torch.randn(batch_size, hidden_size)
        c = torch.randn(batch_size, hidden_size)
        torch.manual_seed(0)

        epsilon = 10e-6
        # Check if GRU logic is correct
        num_layers_list = [1, 3]
        bias_list = [True, False]

        for num_layers in num_layers_list:
            for bias in bias_list:
                for batch_first in [True, False]:
                    if batch_first:
                        x = torch.randn(batch_size, time_steps, input_size)
                    else:
                        x = torch.randn(time_steps, batch_size, input_size)
                    torch_net = torch.nn.GRU(
                        input_size,
                        hidden_size,
                        num_layers=num_layers,
                        bias=True,
                        batch_first=batch_first,
                    )
                    dict = {}  # we can store the weights in this dict for convenience
                    for name, param in torch_net.named_parameters():
                        nn.init.normal_(param)
                        dict[name] = param

                    torch_output, h_n = torch_net(
                        x, torch.cat([h.unsqueeze(0)] * num_layers, 0)
                    )
                    torch_output = torch_output.squeeze(1)
                    my_net = GRU(
                        input_size,
                        hidden_size,
                        num_layers,
                        bias=True,
                        batch_first=batch_first,
                    )
                    # print(list(torch_rnn.named_parameters()))
                    for name, tensor in torch_net.named_parameters():
                        rsetattr(my_net, map_param_name(name), dict[name])

                    output, h_list = my_net(x, [h for _ in range(num_layers)])
                    assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

    def test_seq_forward(self):
        r"""Checks if the sequencer are running in normal and
        streaming modes
        """
        batch_size = 5
        input_size = 8
        hidden_size = 4
        num_layers = 2
        time_steps = 10

        #########
        # Check if output is as expected (= torch models)
        def run_model_streaming(model, x, batch_first=True):
            # init hidden states, set execution mode to streaming
            for module in [model] + list(model.modules()):
                if isinstance(module, fmot.nn.Sequencer):
                    module.state = module.get_init_state(
                        x
                    )  # pass in input so that we can match the device
                    module._streaming = True  # set execution mode to streaming

            # run input through the model one time-step at a time
            outputs = []
            unbind_dim = 1 if batch_first else 0
            for x_t in torch.unbind(x, unbind_dim):
                outputs.append(model(x_t)[0])
            output = torch.stack(outputs, unbind_dim)

            # reset model
            for module in [model] + list(model.modules()):
                if isinstance(module, fmot.nn.Sequencer):
                    module.state = None
                    module._streaming = False

            return output

        model = RNN(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        x = torch.randn(
            batch_size, time_steps, input_size
        )  # 5 batches 10 time steps 8 input_size
        y0, _ = model(x)
        y1 = run_model_streaming(model, x)
        # These two should be exactly the same
        assert torch.abs(y1 - y0).sum() == 0

        model = LSTM(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        x = torch.randn(
            batch_size, time_steps, input_size
        )  # 5 batches 10 time steps 8 input_size
        y0, _ = model(x)
        y1 = run_model_streaming(model, x)
        # These two should be exactly the same
        assert torch.abs(y1 - y0).sum() == 0

        model = GRU(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        x = torch.randn(
            batch_size, time_steps, input_size
        )  # 5 batches 10 time steps 8 input_size
        y0, _ = model(x)
        y1 = run_model_streaming(model, x)
        # These two should be exactly the same
        assert torch.abs(y1 - y0).sum() == 0

    def test_jit_cell(self):
        r"""Checks if we can get a jit script out of our sequencers"""
        input_size = 8
        hidden_size = 4
        num_layers = 2
        model = RNNCell(input_size, hidden_size, batch_first=True, bias=True)
        script_model = torch.jit.script(model)
        model = LSTMCell(input_size, hidden_size, batch_first=True, bias=True)
        script_model = torch.jit.script(model)
        model = GRUCell(input_size, hidden_size, batch_first=True, bias=True)
        script_model = torch.jit.script(model)

        assert True

    def test_convert2qat_cell(self):
        input_size = 8
        hidden_size = 4
        num_layers = 2
        model = RNNCell(input_size, hidden_size, batch_first=True, bias=True)
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
        model = LSTMCell(input_size, hidden_size, batch_first=True, bias=True)
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
        model = GRUCell(input_size, hidden_size, batch_first=True, bias=True)
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

        assert True

    def test_jit(self):
        r"""Checks if we can get a jit script out of our sequencers"""
        input_size = 8
        hidden_size = 4
        num_layers = 2
        model = RNN(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        script_model = torch.jit.script(model)
        model = LSTM(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        script_model = torch.jit.script(model)
        model = GRU(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        script_model = torch.jit.script(model)

        assert True

    def test_convert2qat(self):
        r"""Checks if we can getconvert to qat from our sequencer models"""
        input_size = 8
        hidden_size = 4
        num_layers = 2
        model = RNN(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
        model = LSTM(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
        model = GRU(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

        assert True

    def test_torch2seq(self):
        r"""Checks if the conversion from torch to sequencer works properly"""
        batch_size = 5
        input_size = 3
        hidden_size = 4
        num_layers = 2
        time_steps = 2
        x = torch.randn(batch_size, time_steps, input_size)
        h = torch.randn(batch_size, hidden_size)
        c = torch.randn(batch_size, hidden_size)
        epsilon = 10e-6
        torch.manual_seed(0)

        torch_net = torch.nn.RNN(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        my_net = RNN._from_torchmodule(torch_net)
        torch_output, h_n = torch_net(x, torch.cat([h.unsqueeze(0)] * num_layers, 0))
        torch_output = torch_output.squeeze(1)
        output, h_list = my_net(x, [h for _ in range(num_layers)])
        assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

        torch_net = torch.nn.LSTM(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        my_net = LSTM._from_torchmodule(torch_net)
        torch_output, h_n = torch_net(
            x,
            (
                torch.cat([h.unsqueeze(0)] * num_layers, 0),
                torch.cat([h.unsqueeze(0)] * num_layers, 0),
            ),
        )
        torch_output = torch_output.squeeze(1)
        output, h_list = my_net(x, [h for _ in range(2 * num_layers)])
        assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

        torch_net = torch.nn.GRU(
            input_size, hidden_size, num_layers=num_layers, batch_first=True, bias=True
        )
        my_net = GRU._from_torchmodule(torch_net)
        torch_output, h_n = torch_net(x, torch.cat([h.unsqueeze(0)] * num_layers, 0))
        torch_output = torch_output.squeeze(1)
        output, h_list = my_net(x, [h for _ in range(num_layers)])
        assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

    def test_multilayer(self):
        layers = [RNNCell(4, 4), RNNCell(4, 4)]
        model = MultiLayerRNN(layers)
        x = torch.randn(5, 8, 4)
        y = model(x)
        torch.jit.script(model)

        model = Sequential(RNNCell(4, 4), RNNCell(4, 4))
        torch.jit.script(model)

    def test_superstruct(self):
        model = _SuperBasic(128, 256)
        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
        assert True

    def test_fqir(self):
        input_size = 128
        hidden_size = 256
        for layer_type in [RNN, LSTM, GRU]:
            model = layer_type(input_size, hidden_size, num_layers=2, batch_first=True)
            cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
            cmodel.quantize([torch.randn(2, 10, 128) for __ in range(5)])
            fqir_graph = cmodel.trace()
            assert True

    def test_conv1d_stack(self):
        in_channels = 8
        out_channels = 8
        kernel_size = 3

        batch_size = 5
        time_steps = 10

        model = TemporalConv1d(in_channels, out_channels, kernel_size)

        qmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
        inputs = [torch.randn(batch_size, in_channels, time_steps) for __ in range(5)]
        qmodel.quantize(inputs)

        fqir_graph = qmodel.trace()
        assert True

    def test_conv1d_logic(self):
        in_channels = 8
        out_channels = 8
        kernel_size = 4

        batch_size = 5
        time_steps = 9
        x = torch.randn(batch_size, in_channels, time_steps)

        epsilon = 10e-6
        torch.manual_seed(0)
        torch_net = TemporalConv1d(in_channels, out_channels, kernel_size, bias=True)
        my_net = ConvertedModel(torch_net, seq_dim=-1)
        torch_output = torch_net(x)

        output = my_net(x)
        assert torch.sum(torch.abs(torch_output - output)).item() < epsilon

    def test_dimension_switch(self):
        r"""Checks if we can pass through the stack a network
        that is at some points swapping time and feature dimensions
        """

        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.tcn = TemporalConv1d(8, 8, 4)  # output: B*6
                self.linear = nn.Linear(8, 3)

            def forward(self, x):
                y = self.tcn(x)
                y = torch.transpose(y, 1, 2)
                output = self.linear(y)

                return output

        model = Net()
        batch_size = 5
        timesteps = 10
        n_features = 8

        # Verify that the network is working
        x = torch.randn(batch_size, n_features, timesteps)
        output = model(x)
        assert True

        cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
        inputs = [torch.randn(batch_size, n_features, timesteps) for _ in range(5)]
        cmodel.quantize(inputs)
        graph = cmodel.trace()
        assert True

    def test_DWConv1d_quant_logic(self):
        r"""Check that the quantized version of DWConv1d is matching
        the original model
        """
        epsilon = 10e-6
        torch.manual_seed(0)
        model = fmot.nn.TemporalConv1d(
            in_channels=8, out_channels=8, groups=8, kernel_size=4, bias=True
        )
        inputs = [torch.randn(3, 8, 5) for _ in range(10)]
        cmodel = ConvertedModel(model, batch_dim=0, seq_dim=-1)
        x = inputs[0]

        with torch.no_grad():
            x = inputs[0]
            y0 = model(x)
            y1 = cmodel(x)
            assert torch.sum(y0 - y1) < epsilon
