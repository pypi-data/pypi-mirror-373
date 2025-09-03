import torch
from torch import nn
import fmot
import matplotlib.pyplot as plt


class LogModel(nn.Module):
    def forward(self, x):
        return torch.log(x)


@torch.no_grad()
def test_tilut_log(show=False):
    model = LogModel()
    fmot.CONFIG.telescope_interpolate = False
    cmodel_tlut = fmot.ConvertedModel(model, batch_dim=0)
    fmot.CONFIG.telescope_interpolate = True
    cmodel_tilut = fmot.ConvertedModel(model, batch_dim=0)

    x = 2 ** torch.linspace(-13, 0, 1000).reshape(100, -1)

    for cmodel in [cmodel_tlut, cmodel_tilut]:
        cmodel.quantize([x for _ in range(4)])

    y = model(x)
    y_tlut = cmodel_tlut(x)
    y_tilut = cmodel_tilut(x)

    mse_tlut = (y - y_tlut).pow(2).mean()
    mse_tilut = (y - y_tilut).pow(2).mean()

    print(f"{mse_tlut=:.3E} {mse_tilut=:.3E}")

    if show:
        plt.plot(x.flatten(), y.flatten(), "k:")
        plt.plot(x.flatten(), y_tlut.flatten(), label="tlut")
        plt.plot(x.flatten(), y_tilut.flatten(), label="tilut")
        plt.legend()
        plt.xscale("log", base=2)
        plt.xlabel("x")
        plt.ylabel("log(x)")
        plt.grid()
        plt.show()

    assert mse_tilut < mse_tlut


if __name__ == "__main__":
    test_tilut_log(show=True)
