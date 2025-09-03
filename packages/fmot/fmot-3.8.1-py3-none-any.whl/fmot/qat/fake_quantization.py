import torch
from torch import nn, Tensor
import math
from fmot import CONFIG


def get_fixed_range_quanta(maxabs: float, bits: int) -> int:
    """
    Returns optimal quanta to quantize a tensor over the range [-maxabs, +maxabs]
    with a given number of bits
    """
    if maxabs == 0:
        return 0
    else:
        return math.ceil(math.log2(maxabs) - bits + 1)


@torch.jit.ignore
def fixed_range_fake_quantize(
    x: Tensor, quanta: int, bits: int, quantize: bool, rounded: bool = False
) -> Tensor:
    """
    If quantize = True, simulates quantization on given tensor.
    If quantize = False, saturates the tensor (but no rounding error)
    """
    if quantize:
        return fake_quantize(x, quanta, bits, rounded=rounded)
    else:
        lims = (-(2 ** (bits + quanta - 1)), (2 ** (bits - 1) - 1) * 2**quanta)
        return x.clamp(*lims)


class _fake_quantize_floor(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, quanta, bits):
        scale = 2.0**quanta
        edge = 2.0 ** (bits - 1)
        R = torch.floor(x / scale)
        ctx.save_for_backward(torch.logical_or(R < -edge, R > edge - 1))
        return scale * torch.clamp(R, -edge, edge - 1)

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            (mask,) = ctx.saved_tensors
            grad = grad.masked_fill(mask, 0)
            return grad, None, None
        else:
            return None, None, None


class _fake_quantize_round(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, quanta, bits):
        scale = 2.0**quanta
        edge = 2.0 ** (bits - 1)

        x = torch.floor(x / scale + 0.5)
        ctx.save_for_backward(torch.logical_or(x < -edge, x > edge - 1))
        return scale * torch.clamp(x, -edge, edge - 1)

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            (mask,) = ctx.saved_tensors
            grad = grad.masked_fill(mask, 0)
            return grad, None, None
        else:
            return None, None, None


def fake_quantize(x, quanta, bits, rounded=False):
    """
    Fake-quantize an activation or parameter tensor.

    scale = 2**quanta
    xfq = 2**quanta * Clamp(Round_fn(x/(2**quanta)), -2**(bits-1), 2**(bits-1)-1)

    By default, Round_fn(x) = Floor(x)
    However, for parameter tensors, it may be preferred for Round_fn(x) = Round(x)
    """
    if rounded or CONFIG.quant_round_all:
        return _fake_quantize_round.apply(x, quanta, bits)
    else:
        return _fake_quantize_floor.apply(x, quanta, bits)
