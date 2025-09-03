import unittest
import torch
from torch import nn
import fmot

from fmot.nn import TemporalConv1d
from fmot.nn import rgetattr
from fmot import qat as Q
from fmot import ConvertedModel
from fmot.convert import generate_param2quantizer
from fmot.convert.default_substitutions import DEFAULT_SUBSTITUTIONS, follows_template


class TestFeatures(unittest.TestCase):
    def test_substitutions_dict(self):
        """Check that the subsitutions dict allows
        to access quant model params as expected
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

        qmodel, __ = fmot.convert.convert(
            model,
            precision="double",
            interpolate=True,
            verbose=False,
            dimensions=["B", "F", "T"],
        )
        inputs = [torch.randn(batch_size, n_features, timesteps) for _ in range(5)]
        qmodel = fmot.qat.control.quantize(qmodel, inputs, ["B", "F", "T"])

        for name, param in model.named_parameters():
            if name in qmodel.substitutions_dict:
                new_pname, F_transfo = qmodel.substitutions_dict[name]
                try:
                    _ = rgetattr(qmodel.model, new_pname)
                except AttributeError:
                    raise Exception(
                        "Could not find the converted model substituted parameter."
                    )

        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.lin = nn.Linear(8, 6)
                self.rnn = torch.nn.RNN(6, 4, batch_first=True)
                self.gru = torch.nn.GRU(4, 4, batch_first=True)
                self.lstm = torch.nn.LSTM(4, 4, batch_first=True)

            def forward(self, x):
                y = self.lin(x)
                y, _ = self.rnn(y)
                y, _ = self.gru(y)
                y, _ = self.lstm(y)

                return y

        model = Net()
        batch_size = 5
        timesteps = 10
        n_features = 8

        qmodel, __ = fmot.convert.convert(
            model,
            precision="double",
            interpolate=True,
            verbose=False,
            dimensions=["B", "T", "F"],
        )
        inputs = [torch.randn(batch_size, timesteps, n_features) for _ in range(5)]
        qmodel = Q.control.quantize(qmodel, inputs, dimensions=["B", "T", "F"])

        for name, param in model.named_parameters():
            if name in qmodel.substitutions_dict:
                new_pname, F_transfo = qmodel.substitutions_dict[name]
                try:
                    _ = rgetattr(qmodel.model, new_pname)
                except AttributeError:
                    raise Exception(
                        "Could not find the converted model substituted parameter."
                    )

    def test_converter_check(self):
        """Check that the errors are correclty raised when
        we convert sequential models without feeding
        a seq_dim to the converter
        """
        model = torch.nn.Sequential(TemporalConv1d(8, 8, 4), torch.nn.Linear(8, 4))
        with self.assertRaises(Exception):
            ConvertedModel(model, batch_dim=0, seq_dim=None)
        ConvertedModel(model, batch_dim=0, seq_dim=1)

        model = torch.nn.Sequential(model, torch.nn.Linear(4, 4))
        with self.assertRaises(Exception):
            ConvertedModel(model, batch_dim=0, seq_dim=None)

        ConvertedModel(model, batch_dim=0, seq_dim=1)

        model = torch.nn.Linear(4, 4)
        ConvertedModel(model, batch_dim=0, seq_dim=None)

    def test_param2quant(self):
        model = torch.nn.Sequential(torch.nn.ReLU(), torch.nn.Linear(4, 2))
        inputs = [torch.randn(4, 4) for __ in range(10)]
        cmodel = ConvertedModel(
            model, precision="double", batch_dim=0, interpolate=False
        )
        cmodel.quantize(inputs)
        _ = generate_param2quantizer(cmodel, inputs[0])

    def test_tuneps_eval(self):
        """Tests that TuningEpsilon running_mean only gets updated during training."""
        tuneps = fmot.nn.TuningEpsilon(eps=0.25)
        input = torch.tensor([8, 8, 8])
        _ = tuneps(input)
        assert tuneps.epsilon() == 2.0
        tuneps.eval()
        _ = tuneps(torch.tensor([10, 10, 10]))
        assert tuneps.epsilon() == 2.0

    def test_tuneps_inherit(self):
        """Tests that TuningEpsilon epsilon is the same before and after mapping."""
        torch.manual_seed(0)
        tuneps = fmot.nn.TuningEpsilon(eps=0.25)
        input = torch.tensor([8, 8, 8])
        _ = tuneps(input)
        tuneps.eval()
        c_tuneps = ConvertedModel(tuneps)
        x = torch.tensor([10, 10, 10])
        with torch.no_grad():
            out = tuneps(x)
            c_out = c_tuneps(x)

        assert tuneps.epsilon() == c_tuneps.model.model.epsilon()
        assert (c_out - out).abs().sum() < 1e-4

    def test_substitution_dict_template(self):
        """Tests that all the entries in the"""
        for subst_class in DEFAULT_SUBSTITUTIONS.values():
            follows_template(subst_class._from_torchmodule)

    def test_eval_mode_transfer(self):
        """Tests that a converted model inherits the train/eval mode of the original model"""
        model = nn.Linear(8, 8)
        model.eval()
        cmodel = ConvertedModel(model)
        assert model.training == cmodel.training


if __name__ == "__main__":
    test = TestFeatures()
    test.test_logic_param2quant()
