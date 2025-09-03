import torch
from torch import nn
import fmot
import pytest


class MyModel(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.lin = fmot.nn.TemporalConv1d(hidden_size, hidden_size, 3)
        self.bnorm = nn.BatchNorm1d(hidden_size)

    def forward(self, x):
        x = self.lin(x)
        x = self.bnorm(x)
        return x


@pytest.mark.parametrize("gain", [1, 2, 5, 0.1])
def test_batchnorm(gain):
    H = 32
    model = MyModel(H)

    # update batchnorm stats
    for _ in range(10):
        _ = model(torch.randn(8, H, 20) * gain)

    model.eval()

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
    cmodel.quantize([torch.randn(8, H, 20) * gain for _ in range(3)])

    x = torch.randn(8, H, 20) * gain
    y0 = model(x)
    y1 = cmodel(x)

    err = (y0 - y1).pow(2).mean()
    assert err < 1e-4 * gain


if __name__ == "__main__":
    test_batchnorm(1)
    test_batchnorm(10)
