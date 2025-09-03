import torch
from torch import nn
import fmot


class LayerReuse(nn.Module):
    def __init__(self, layer: nn.Module):
        super().__init__()
        self.layer = layer

    def forward(self, x):
        x = self.layer(x)
        x = self.layer(x)
        return x


class WrappedRNN(nn.Module):
    def __init__(self, rnn: nn.Module):
        super().__init__()
        self.rnn = rnn

    def forward(self, x):
        x, __ = self.rnn(x)
        return x


def _get_param_count(model: nn.Module, shape: tuple, batch_dim=0, seq_dim=None):
    cmodel = fmot.ConvertedModel(model, batch_dim=batch_dim, seq_dim=seq_dim)
    cmodel.quantize([torch.randn(*shape) for _ in range(4)])
    graph = cmodel.trace()
    return sum([p.numel() for p in graph.subgraphs["ARITH"].parameters])


def apply_base_test(base_layer, shape, batch_dim=0, seq_dim=None):
    # get number of params for base layer
    n_base = _get_param_count(base_layer, shape, batch_dim, seq_dim)

    # get number of params when reusing the base layer
    n_reuse = _get_param_count(LayerReuse(base_layer), shape, batch_dim, seq_dim)

    if n_base != n_reuse:
        raise ValueError(f"Got {n_reuse} != {n_base} when reusing {base_layer}")

    else:
        print(f"Success! Had {n_reuse} params before/after reusing {base_layer}")


def test_gru_reuse():
    apply_base_test(WrappedRNN(nn.GRU(32, 32, batch_first=True)), (8, 8, 32), 0, 1)


def test_lstm_reuse():
    apply_base_test(WrappedRNN(nn.LSTM(32, 32, batch_first=True)), (8, 8, 32), 0, 1)


def test_linear_reuse():
    apply_base_test(nn.Linear(32, 32), (8, 32), 0, None)


def test_multilinear_reuse():
    model = nn.Sequential(nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 32))
    apply_base_test(model, (8, 32), 0, None)


if __name__ == "__main__":
    import logging

    # logging.basicConfig(level=logging.DEBUG)
    test_gru_reuse()
    test_lstm_reuse()
    test_linear_reuse()
    test_multilinear_reuse()
