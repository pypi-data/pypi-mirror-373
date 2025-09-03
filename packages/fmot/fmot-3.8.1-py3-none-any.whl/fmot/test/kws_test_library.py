from .unittest_objects import UTM, SUTM, TestSet, TestLibrary
import torch
from torch import nn
from itertools import product as iterprod
import fmot
import functools

kws_library = TestLibrary("Keyword Spotting Architectures")

rnn_dict = {
    "gru": (torch.nn.GRU, {}),
    "lstm": (torch.nn.LSTM, {}),
    "femtogru": (fmot.nn.FemtoGRU, dict(num_blocks=8)),
    "adaptivefemtogru": (fmot.nn.AdaptiveFemtoGRU, dict(num_blocks=8)),
    "femtolstm": (fmot.nn.FemtoLSTM, dict(num_blocks=8)),
    "adaptivefemtolstm": (fmot.nn.AdaptiveFemtoLSTM, dict(num_blocks=8)),
}

Din = 131
Dout = 10


def rgetattr(obj, attr, *args):
    if attr == "":
        return obj

    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


class RNNArch(nn.Module):
    """
    Linear -> AdaptiveSparsifier -> RNN(s) -> Linear
    """

    def __init__(self, layer_type, num_layers, hidden_size, prune_amount):
        super().__init__()
        self.input_size = Din
        self.output_size = Dout
        self.hidden_size = hidden_size

        self.lin_in = nn.Linear(self.input_size, hidden_size)
        self.sp = fmot.nn.AdaptiveSparsifier(hidden_size, batch_first=True)
        self.rnn_layers = nn.ModuleList()
        for i in range(num_layers):
            layer_class, config = rnn_dict[layer_type]
            layer = layer_class(
                input_size=hidden_size,
                hidden_size=hidden_size,
                batch_first=True,
                **config,
            )
            self.rnn_layers.append(layer)
        self.lin_out = nn.Linear(hidden_size, self.output_size)
        self.prune(prune_amount)

    def prune(self, amount):
        for n, p in list(self.named_parameters()):
            if p.dim() == 2 and p.numel() > 2000 and ("block" not in n):
                parent, pname = n.rsplit(".", 1)
                layer = rgetattr(self, parent)
                fmot.utils.pencil_pruning(layer, pname, amount, 8)
                print(f"Pruned {n}")

    @fmot.utils.reset_counters
    def forward(self, x):
        x = self.lin_in(x)
        x, __ = self.sp(x)
        for l in self.rnn_layers:
            x, __ = l(x)
        x = self.lin_out(x)
        return x


class RNNArchUTM(SUTM):
    def __init__(self, layer_type, num_layers, hidden_size, prune_amount):
        super().__init__()
        self.nb_timesteps = 10
        self.input_size = Din
        self.output_size = Dout
        self.hidden_size = hidden_size

        self.net = RNNArch(layer_type, num_layers, hidden_size, prune_amount)

    def forward(self, x):
        return self.net(x)


for layer_type in rnn_dict.keys():
    kws_library[f"kws_{layer_type}"] = TestSet(
        utm=RNNArchUTM,
        par_sets=[
            dict(layer_type=layer_type, num_layers=L, hidden_size=H, prune_amount=P)
            for L, H, P in iterprod([1, 2], [64, 128], [0.1, 0.8, 0.9])
        ],
    )
