import torch
from torch import nn, Tensor
import math
from .sequencer import Sequencer
from .super_structures import SuperStructure
from .atomics import Identity
from ..utils.typing import SubstDict
from typing import *


class DilatedLSTM(nn.Module):
    """Apply a single-layer dilated long short-term memory (dLSTM) RNN to an input sequence.

    For dilation D, maintains D sets of hidden-states, and alternates between them on each time-step.
    Equivalent to D parallel LSTMs, each run a strided slice of the input sequence. The output states are
    interleaved.

    Arguments:
        input_size (int): Number of input channels
        hidden_size (int): Number of hidden channels
        dilation (int): LSTM dilation
        bias (bool): Whether to use bias in the LSTM (default True)

    .. note::

        :class:`DilatedLSTM` must be run on input sequences of shape :attr:`(batch, sequence_length, input_size)`.
        It returns a single output sequence of shape :attr:`(batch, sequence_length, hidden_size)`.

    """

    def __init__(self, input_size: int, hidden_size: int, dilation: int, bias=True):
        super().__init__()
        self.dilation = dilation
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True, bias=bias)

    def forward(self, x):
        # NOTE: Currently ignores state-inheritance / is incompatible with it.

        B, T, C = x.shape

        # pad T to be a multiple of self.dilation
        Tp = int(math.ceil(T / self.dilation)) * self.dilation
        x = torch.nn.functional.pad(x, (0, 0, 0, Tp - T))

        # break into "self.dilation" dilated bits
        x = x.reshape(B, Tp // self.dilation, self.dilation, C)
        x = x.permute(0, 2, 1, 3)  # (batch, dilation, T/dilation, channels)

        # fold dilation into batchdim
        x = x.reshape(B * self.dilation, Tp // self.dilation, C)

        # run lstm
        y, state = self.lstm(x)

        # reshape y back to (B, Tp, C)
        y = y.reshape(B, self.dilation, Tp // self.dilation, self.hidden_size)
        y = y.permute(0, 2, 1, 3)
        y = y.reshape(B, Tp, self.hidden_size)

        # assert y.shape[-1] == self.hidden_size

        # cut out excess temporal length
        y = y[:, :T, :]
        return y


class Add(nn.Module):
    def forward(self, x, y):
        return x + y


class Mul(nn.Module):
    def forward(self, x, y):
        return x * y


class Chunk4(nn.Module):
    def forward(self, x):
        return x.chunk(4, -1)


class _DilatedLSTMLayer(Sequencer, SuperStructure):
    def __init__(self, input_size, hidden_size, dilation, bias=True):
        super().__init__([[hidden_size]] * 2 * dilation, batch_dim=0, seq_dim=1)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.dilation = dilation
        self.weight_ih = nn.Linear(input_size, 4 * hidden_size, bias=bias)
        self.weight_hh = nn.Linear(hidden_size, 4 * hidden_size, bias=bias)

        self.add0 = Add()
        self.add1 = Add()
        self.mul0 = Mul()
        self.mul1 = Mul()
        self.mul2 = Mul()
        self.mul3 = Mul()

        self.sigmoid = nn.Sigmoid()
        self.tanh0 = nn.Tanh()
        self.tanh1 = nn.Tanh()

        self.chunk = Chunk4()

    @torch.jit.export
    def step(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        hidden_buffer = state[: self.dilation]
        cell_buffer = state[self.dilation :]

        h_t = hidden_buffer[0]
        c_t = cell_buffer[0]

        u_ih = self.weight_ih(x)
        u_hh = self.weight_hh(h_t)
        u = self.add0(u_ih, u_hh)

        i_t, f_t, g_t, o_t = self.chunk(u)
        i_t = self.sigmoid(i_t)
        f_t = self.sigmoid(f_t)
        g_t = self.tanh0(g_t)
        o_t = self.sigmoid(o_t)

        c_t = self.add1(self.mul1(f_t, c_t), self.mul2(i_t, g_t))
        h_t = self.mul3(o_t, self.tanh1(c_t))

        hidden_buffer = state[1 : self.dilation] + [h_t]
        cell_buffer = state[self.dilation + 1 :] + [c_t]

        state = hidden_buffer + cell_buffer

        return h_t, state


class ConvertedDilatedLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, dilation, bias=True):
        super().__init__()
        self.layer = _DilatedLSTMLayer(input_size, hidden_size, dilation, bias=bias)

    def forward(self, x):
        x, _ = self.layer(x)
        return x

    @classmethod
    def _from_torchmodule(
        cls,
        parent: DilatedLSTM,
        toplevel=None,
        inherited_name="",
        inherited_dict: SubstDict = dict(),
    ):
        """Implements substitution-style conversion. NOTE: Currently leads to torchscript error
        if this method is used for conversion..."""
        input_size = parent.input_size
        hidden_size = parent.hidden_size
        dilation = parent.dilation
        bias = parent.bias

        child = cls(
            input_size=input_size, hidden_size=hidden_size, dilation=dilation, bias=bias
        )

        weight_ih = getattr(parent.lstm, f"weight_ih_l0")
        weight_hh = getattr(parent.lstm, f"weight_hh_l0")

        new_layer: _DilatedLSTMLayer = child.layer
        new_layer.weight_hh.weight.data = weight_hh.data
        new_layer.weight_ih.weight.data = weight_ih.data

        inherited_dict[inherited_name + f"weight_ih_l0"] = (
            inherited_name + f"layer.weight_ih.weight",
            None,
        )
        inherited_dict[inherited_name + f"weight_hh_l0"] = (
            inherited_name + f"layer.weight_hh.weight",
            None,
        )

        if bias:
            bias_ih = getattr(parent.lstm, f"bias_ih_l0")
            bias_hh = getattr(parent.lstm, f"bias_hh_l0")

            new_layer.weight_hh.bias.data = bias_hh.data
            new_layer.weight_ih.bias.data = bias_ih.data

            inherited_dict[inherited_name + f"bias_hh_l0"] = (
                inherited_name + f"layer.weight_hh.bias",
                None,
            )
            inherited_dict[inherited_name + f"bias_ih_l0"] = (
                inherited_name + f"layer.weight_ih.bias",
                None,
            )

        return child


#     @classmethod
#     def from_fp(cls, parent: DilatedLSTM):
#         """Simpler conversion classmethod"""

#         input_size = parent.input_size
#         hidden_size = parent.hidden_size
#         dilation = parent.dilation
#         num_layers = parent.num_layers
#         bias = True

#         child = cls(input_size=input_size, hidden_size=hidden_size, dilation=dilation, num_layers=num_layers,
#                     bias=bias)

#         for i in range(num_layers):
#             weight_ih = getattr(parent.lstm, f"weight_ih_l{i}")
#             weight_hh = getattr(parent.lstm, f"weight_hh_l{i}")

#             new_layer: _DilatedLSTMLayer = child.layers[i]
#             new_layer.weight_hh.weight.data = weight_hh.data
#             new_layer.weight_ih.weight.data = weight_ih.data

#             if bias:
#                 bias_ih = getattr(parent.lstm, f"bias_ih_l{i}")
#                 bias_hh = getattr(parent.lstm, f"bias_hh_l{i}")

#                 new_layer.weight_hh.bias.data = bias_hh.data
#                 new_layer.weight_ih.bias.data = bias_ih.data

#         return child

# def convert_dilated_lstm(model: nn.Module):
#     for name, child in model.named_children():
#         if isinstance(child, DilatedLSTM):
#             new_child = ConvertedDilatedLSTM.from_fp(child)
#             setattr(model, name, new_child)
#             if hasattr(child, 'observer_class'):
#                 setattr(new_child, 'observer_class', child.observer_class)

#         else:
#             convert_dilated_lstm(child)

#     return model

# @classmethod
# def from_fp(cls, parent: DilatedLSTM):
#     input_size = parent.input_size
#     hidden_size = parent.hidden_size
#     dilation = parent.dilation
#     num_layers = parent.num_layers
#     bias = True

#     child = cls(input_size=input_size, hidden_size=hidden_size, dilation=dilation, num_layers=num_layers,
#                 bias=bias)

#     for i in range(num_layers):
#         weight_ih = getattr(parent.lstm, f"weight_ih_l{i}")
#         weight_hh = getattr(parent.lstm, f"weight_hh_l{i}")

#         new_layer: _DilatedLSTMLayer = child.layers[i]
#         new_layer.weight_hh.weight.data = weight_hh.data
#         new_layer.weight_ih.weight.data = weight_ih.data

#         if bias:
#             bias_ih = getattr(parent.lstm, f"bias_ih_l{i}")
#             bias_hh = getattr(parent.lstm, f"bias_hh_l{i}")

#             new_layer.weight_hh.bias.data = bias_hh.data
#             new_layer.weight_ih.bias.data = bias_ih.data

#     return child
