import torch
from torch import nn, Tensor
import fmot
from fmot.nn.special_rnn import DilatedLSTM
import pytest
from typing import *


class DLSTMArch(nn.Module):
    def __init__(self, hidden_size, dilation, num_layers=1):
        super().__init__()
        self.dlstm = nn.Sequential()
        for _ in range(num_layers):
            self.dlstm.append(DilatedLSTM(hidden_size, hidden_size, dilation))

    def forward(self, x: Tensor):
        x = self.dlstm(x)
        return x


@pytest.mark.parametrize("num_layers", [1, 2])
@pytest.mark.parametrize("dilation", [1, 2, 8])
@pytest.mark.parametrize("hidden_size", [16])
@torch.no_grad
def test_dLSTM(hidden_size, dilation, num_layers):
    torch.manual_seed(0)

    fmot.CONFIG.fast_ilut = True

    model = DLSTMArch(hidden_size, dilation, num_layers)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

    x = torch.randn(8, dilation * 4, hidden_size)

    y0 = model(x)
    y1 = cmodel(x)

    mse = (y0 - y1).pow(2).mean() / y0.pow(2).mean()

    assert mse <= 1e-10
    print(f"F.P. nMSE: {mse}")

    cmodel.quantize([torch.randn(8, dilation * 4, hidden_size) for _ in range(5)])

    y2 = cmodel(x)

    mse = (y0 - y2).pow(2).mean() / y0.pow(2).mean()

    assert mse <= 5e-4
    print(f"QAT nMSE: {mse}")


if __name__ == "__main__":
    test_dLSTM(32, 8, 3)
