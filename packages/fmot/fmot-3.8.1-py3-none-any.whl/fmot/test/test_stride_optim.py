import torch
import fmot
import numpy as np
from torch import nn
import pytest


class TposeRNN(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)

    def forward(self, x):
        x = x.transpose(1, 2)
        x, _ = self.lstm(x)
        x = x.transpose(1, 2)
        return x


@pytest.mark.xfail
@pytest.mark.parametrize("depth", [1, 2, 4], ids=["depth1", "depth2", "depth4"])
@pytest.mark.parametrize("rnn", [True, False])
@pytest.mark.parametrize(
    ["kernel_size", "stride"], [[4, 2], [4, 4], [3, 1]], ids=["k4_s2", "k4_s4", "k3_s1"]
)
@torch.no_grad()
def test_simple_unet(
    depth: int, kernel_size: int, stride: int, rnn: bool, hidden_size=16, plot=False
):
    encoder = []
    decoder = []
    for _ in range(depth):
        encoder.append(
            fmot.nn.TemporalConv1d(
                in_channels=hidden_size,
                out_channels=hidden_size,
                kernel_size=kernel_size,
                stride=stride,
            )
        )
        decoder.append(
            fmot.nn.TemporalConvTranspose1d(
                in_channels=hidden_size,
                out_channels=hidden_size,
                kernel_size=kernel_size,
                stride=stride,
            )
        )
        if rnn:
            encoder.append(TposeRNN(hidden_size))
            decoder.append(TposeRNN(hidden_size))

    layers = encoder + decoder

    model = nn.Sequential(*layers)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
    cmodel.quantize(
        [torch.randn(8, hidden_size, stride**depth * 4) for _ in range(4)]
    )
    graph = cmodel.trace()

    iospec = cmodel.get_iospec()

    x = torch.randn(1, hidden_size, stride**depth * 4)
    y0 = cmodel(x)[0].numpy()

    try:
        y1 = iospec.run_graph(graph, [x[0].numpy()], dequant=True)
    except:
        print(graph)
        raise

    if plot:
        import matplotlib.pyplot as plt

        plt.plot(y0.flatten(), y1.flatten(), ".")
        plt.show()

    print(graph)


if __name__ == "__main__":
    test_simple_unet(
        depth=1, hidden_size=16, stride=4, kernel_size=8, rnn=True, plot=True
    )
