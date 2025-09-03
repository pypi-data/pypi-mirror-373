import torch.nn as nn
from torch import Tensor
import fmot
import torch
from typing import *


class Packer(nn.Module):
    def forward(self, a: Tensor, b: Tensor, c: Tensor, d: Tensor) -> List[List[Tensor]]:
        a00 = a * b
        a01 = b * c
        a10 = c * d
        a11 = d * a

        res = [[a00, a01], [a10, a11]]
        return res


def test_packer():
    model = Packer()
    B, S, D = 1, 20, 40

    a, b, c, d = (
        torch.randn(B, S, D),
        torch.randn(B, S, D),
        torch.randn(B, S, D),
        torch.randn(B, S, D),
    )

    # normal fwds
    packed_list = model(a, b, c, d)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    calib_data = [(a, b, c, d), (a, b, c, d)]

    cmodel.quantize(calib_data)

    out_q = cmodel(*calib_data[0])
    out_fp = model(*calib_data[0])

    pass


if __name__ == "__main__":
    test_packer()
