import torch
from torch import nn
import fmot
from fmot import set_sequencer_p_inherit
import pytest


class MyModel(nn.Module):
    def __init__(self, hidden_size: int = 32, rnn_class=nn.GRU):
        super().__init__()
        self.rnn = rnn_class(hidden_size, hidden_size, batch_first=True)

    def forward(self, x):
        x, _ = self.rnn(x)
        return x


class MySTFTModel(nn.Module):
    def __init__(self, hidden_size: int = 32):
        super().__init__()
        self.stft = fmot.nn.STFT(2 * hidden_size, hidden_size, n_stages="auto")
        self.mag = fmot.nn.signal_processing.Magnitude()

    def forward(self, x):
        re, im = self.stft(x)
        mag = self.mag(re, im)
        return mag


def get_model(hidden_size, model_type="lstm"):
    if model_type == "stft":
        model = MySTFTModel(hidden_size=hidden_size)
    elif model_type == "lstm":
        model = MyModel(hidden_size, rnn_class=nn.LSTM)
    elif model_type == "gru":
        model = MyModel(hidden_size, rnn_class=nn.GRU)
    else:
        raise NotImplementedError(f"{model_type} not defined")

    return model


@pytest.mark.parametrize("model_type", ["lstm", "gru", "stft"])
def test_state_inherit(model_type):
    H = 32
    model = get_model(H, model_type)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

    # check 1: output same each time if passing the same input
    x = torch.randn(8, 16, H)
    y0 = cmodel(x)
    y1 = cmodel(x)

    assert torch.all(y0 == y1)
    print("check 1 succeeded")

    # check 2: with p_inherit enabled, output should change even if we call the model
    # on the same input multiple times
    set_sequencer_p_inherit(cmodel, 0.5)
    y2 = cmodel(x)
    y3 = cmodel(x)

    assert torch.all(y0 == y2)
    assert not torch.all(y3 == y2)
    print("check 2 succeeded")

    # check 3: can still quantize and export w/ state-inheritance enabled
    cmodel.quantize([torch.randn(8, 16, H) for _ in range(4)])
    graph = cmodel.trace()
    print("got graph")
    print(graph.subgraphs["ARITH"])


@pytest.mark.parametrize("model_type", ["lstm", "gru", "stft"])
def test_multi_batchsize(model_type):
    H = 32
    model = get_model(H, model_type)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    # cmodel.quantize([torch.randn()])

    # with p_inherit enabled, we should be able to run with various batch-sizes
    set_sequencer_p_inherit(cmodel, 0.5)
    batch_sizes = [8, 16, 4, 9]
    for B in batch_sizes:
        print(f"batch-size: {B}")
        x = torch.randn(B, 10, H)
        _ = cmodel(x)
        print("  success...")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    test_state_inherit("lstm")
    test_state_inherit("gru")
    test_state_inherit("stft")
    test_multi_batchsize("lstm")
    test_multi_batchsize("gru")
    test_multi_batchsize("stft")
