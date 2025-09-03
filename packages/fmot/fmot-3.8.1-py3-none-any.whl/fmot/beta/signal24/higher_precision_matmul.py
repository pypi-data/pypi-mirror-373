import torch
from torch import nn, Tensor
from typing import Literal, Union
from fmot.nn import GMACv2, PrecisionSplit
from fmot.precisions import int8, int16, int24, Precision


def quant8(x: torch.Tensor) -> torch.Tensor:
    """fake-quantize a float tensor to int8 with power-of-2 scale"""
    mv = x.abs().max()
    q = mv.log2().ceil() - 6
    xq = (x / 2**q).round()
    x_fq = xq * 2**q
    return x_fq


class Virtual16bMatmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False):
        super().__init__()
        assert not requires_grad

        w_upper = quant8(weight)
        w_lower = weight - w_upper

        self.weight_upper = nn.Parameter(w_upper, requires_grad=requires_grad)
        self.weight_lower = nn.Parameter(w_lower, requires_grad=requires_grad)

    def forward(self, x):
        y_upper = torch.matmul(x, self.weight_upper.T)
        y_lower = torch.matmul(x, self.weight_lower.T)
        y = y_upper + y_lower
        return y


class SimpleMatmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False):
        super().__init__()
        self.weight = nn.Parameter(weight, requires_grad=requires_grad)

    def forward(self, x):
        y = torch.matmul(x, self.weight.T)
        return y


class Act16Weight16Matmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False, bits_headroom=0):
        super().__init__()
        w_hi = quant8(weight)
        w_lo = weight - w_hi

        self.weight_hi = nn.Parameter(w_hi, requires_grad=requires_grad)
        self.weight_lo = nn.Parameter(w_lo, requires_grad=requires_grad)

        self.weight = nn.Parameter(weight, requires_grad=requires_grad)
        self.cast = GMACv2(16, torch.tensor([1, 1]), bits_headroom=bits_headroom)

    def forward(self, x):
        y_lo = torch.matmul(x, self.weight_lo.T)
        y_hi = torch.matmul(x, self.weight_hi.T)

        y = self.cast([], [], [y_lo, y_hi])
        return y


class Act24Weight8Matmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False, bits_headroom=0):
        super().__init__()
        self.prec_split = PrecisionSplit([13, 12], [16, 16])
        self.weight = nn.Parameter(weight, requires_grad=requires_grad)
        self.cast = GMACv2(24, torch.tensor([1, 1]), bits_headroom=bits_headroom)

    def forward(self, x):
        x_lo, x_hi = self.prec_split(x)
        y_lo = torch.matmul(x_lo, self.weight.T)
        y_hi = torch.matmul(x_hi, self.weight.T)

        y = self.cast([], [], [y_lo, y_hi])
        return y


class Act24Weight16Matmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False, bits_headroom=9):
        super().__init__()
        assert not requires_grad
        self.prec_split = PrecisionSplit([13, 12], [16, 16])

        w_hi = quant8(weight)
        w_lo = weight - w_hi

        self.weight_hi = nn.Parameter(w_hi, requires_grad=requires_grad)
        self.weight_lo = nn.Parameter(w_lo, requires_grad=requires_grad)

        self.cast = GMACv2(24, torch.tensor([1, 1, 1, 1]), bits_headroom=bits_headroom)

    def forward(self, x):
        x_lo, x_hi = self.prec_split(x)
        y_lo_lo = torch.matmul(x_lo, self.weight_lo.T)
        y_lo_hi = torch.matmul(x_lo, self.weight_hi.T)
        y_hi_lo = torch.matmul(x_hi, self.weight_lo.T)
        y_hi_hi = torch.matmul(x_hi, self.weight_hi.T)

        y = self.cast([], [], [y_lo_lo, y_lo_hi, y_hi_lo, y_hi_hi])
        return y


def get_higher_precision_matmul(
    weight: Tensor,
    act_precision: Union[Precision, Literal[16, 24]],
    weight_precision: Union[Precision, Literal[8, 16]],
    requires_grad: bool = False,
    bits_headroom: int = 0,
):
    if requires_grad:
        raise RuntimeError(
            "higher-precision matmul layers currently do not support requires_grad=True"
        )

    if act_precision == int16:
        if weight_precision == int8:
            return SimpleMatmul(weight, requires_grad=False)
        elif weight_precision == int16:
            return Act16Weight16Matmul(weight, requires_grad=False)
        else:
            raise ValueError(f"Got {weight_precision=}, must be one of [int8, int16]")
    elif act_precision == int24:
        if weight_precision == int8:
            return Act24Weight8Matmul(
                weight, requires_grad=False, bits_headroom=bits_headroom
            )
        elif weight_precision == int16:
            return Act24Weight16Matmul(
                weight, requires_grad=False, bits_headroom=bits_headroom
            )
        else:
            raise ValueError(f"Got {weight_precision=}, must be one of [int8, int16]")

    else:
        raise ValueError(f"Got {act_precision=}, must be one of [int16, int24]")
