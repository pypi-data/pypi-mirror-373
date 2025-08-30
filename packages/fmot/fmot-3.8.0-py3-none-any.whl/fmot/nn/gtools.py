import torch
import math
from torch import nn, Tensor
from typing import Callable
from fmot.nn import SuperStructure
from . import atomics
from fmot.precisions import Precision, int16, int24


class GReduceSum(SuperStructure):
    """Perform sum reduction on higher-precision variables, using GMAC.

    After quantization, the operation will:
    1. Break the input into low/high bits (using PrecisionSplit)
    2. Perform a sum on each
    3. Add the individual sums together with a GMAC

    If input precision is i16, revert to a standard sum

    Arguments:
        prec_in (int | Precision): input vector precision, int24 or int16
        prec_out (int | Precision): output vector precision, int24 or int16
        dim (int, optional): dimension to perform reduction on. Default -1
        keepdim (bool, optional): if true, keep the reduced dimension. Default True
    """

    def __init__(
        self, prec_in: Precision, prec_out: Precision, dim: int = -1, keepdim=True
    ):
        super().__init__()
        self.prec_in = prec_in
        self.prec_out = prec_out
        self.dim = dim
        self.keepdim = keepdim

        if prec_in == int16:
            self.sum = atomics.Sum(keepdim=keepdim, dim=dim)
            if prec_out == int24:
                self.cast = atomics.GMACv2(prec_out, torch.tensor([1]))

        elif prec_in == int24:
            self.prec_split = atomics.PrecisionSplit([13, 12], [16, 16])
            self.sum_lo = atomics.Sum(keepdim=keepdim, dim=dim)
            self.sum_hi = atomics.Sum(keepdim=keepdim, dim=dim)
            self.sum_mix = atomics.GMACv2(prec_out, torch.tensor([1, 1]))

    @torch.jit.ignore
    def forward(self, x):
        if self.prec_in == int16:
            sum_x = self.sum(x)
            if self.prec_out == int24:
                sum_x = self.cast([], [], [sum_x])
            return sum_x
        elif self.prec_in == int24:
            x_lo, x_hi = self.prec_split(x)
            sum_lo = self.sum_lo(x_lo)
            sum_hi = self.sum_hi(x_hi)
            sum_x = self.sum_mix([], [], [sum_lo, sum_hi])
            return sum_x
        else:
            raise NotImplementedError(f"{self.prec_in=} not supported")


class GGreaterThan(nn.Module):
    """
    After quantization, will compare an int24 variable to a scalar,
    returning a boolean vector representing x > theta, stored in an i16 vector.

    Arguments:
        theta (float): scalar to compare with
    """

    def __init__(self, theta: float):
        super().__init__()
        self.theta = theta
        self.prec_split = atomics.PrecisionSplit([13, 12], [16, 16])
        self.gt0_hi = atomics.Gt0()
        self.gt0_lo = atomics.Gt0()
        self.gt0_or = atomics.Gt0()

    def forward(self, x):
        x_lo, x_hi = self.prec_split(x)
        cmp_lo = x_lo - self.theta
        cmp_hi = x_hi - self.theta
        # cmp_lo OR cmp_hi
        res = self.gt0_or(cmp_lo + cmp_hi)
        return res


class GTelescopeLogIdentity(nn.Module):
    """Performs a telescoping logarithm-like nonlinearity on int24 variables by evaluating:

        f(x) = { f(x);                      x >= theta
               { f(beta * x) - f(beta);     x < theta

    Arguments:
        theta (float): cross-over threshold, should be a rough factor of 2**8 to 2**16 lower than
            the max expected input value (there is wide tolerance for different values of theta).
        func (callable): torch function (e.g. torch.log). User is responsible for ensuring that
            func(a * b) = func(a) + func(b)
        beta (float, optional): amplifier for low-magnitude signals. Default 2**14
    """

    def __init__(
        self, theta: float, func: Callable[[Tensor], Tensor], beta: float = 2**12
    ):
        super().__init__()
        self.gt_theta = GGreaterThan(theta)
        self.beta = beta
        self.beta_minus_1 = beta - 1
        self.func = func

        self.mul_amplify = atomics.GMACv2(int16)

        self.f_beta = func(torch.tensor(beta)).item()

        self.sub_y = atomics.GMACv2(int24, torch.tensor([1, -1]))

    def forward(self, x):
        above = self.gt_theta(x)
        below = 1 - above

        # amplify small signals by beta
        # x = x * [(beta - 1) * below + 1] --> cast i16
        amp = self.beta_minus_1 * below + 1
        x_amp = self.mul_amplify([x], [amp], [])  # i16

        y_amp = self.func(x_amp)

        # y = y_amp - below * func(beta)
        # use GMAC for this subtraction to cast back to i24
        to_subtract = self.f_beta * below
        y = self.sub_y([], [], [y_amp, to_subtract])

        return y


class GTelescopePowIdentity(nn.Module):
    """Performs a telescoping monomial-like nonlinearity on int24 variables by evaluating:

        f(x) = { f(x);                      x >= theta
               { f(beta * x) / f(beta);     x < theta

    Arguments:
        theta (float): cross-over threshold, should be a rough factor of 2**8 to 2**16 lower than
            the max expected input value (there is wide tolerance for different values of theta).
        func (callable): torch function (e.g. torch.log). User is responsible for ensuring that
            func(a * b) = func(a) * func(b)
        beta (float, optional): amplifier for low-magnitude signals. Default 2**14
    """

    def __init__(
        self, theta: float, func: Callable[[Tensor], Tensor], beta: float = 2**14
    ):
        super().__init__()
        self.gt_theta = GGreaterThan(theta)
        self.beta = beta
        self.beta_minus_1 = beta - 1
        self.func = func

        self.mul_amplify = atomics.GMACv2(int16)

        self.inv_f_beta_min_1 = 1 / func(torch.tensor(beta)).item() - 1

        self.mul_y = atomics.GMACv2(int24)

    def forward(self, x):
        above = self.gt_theta(x)
        below = 1 - above

        # amplify small signals by beta
        # x = x * [(beta - 1) * below + 1] --> cast i16
        amp = self.beta_minus_1 * below + 1
        x_amp = self.mul_amplify([x], [amp], [])  # i16

        y_amp = self.func(x_amp)

        # y = y_amp * (below * [1/func(beta) - 1] + 1)
        # use GMAC for this multiplication to cast back to i24
        multiplier = below * self.inv_f_beta_min_1 + 1
        y = self.mul_y([y_amp], [multiplier], [])

        return y
