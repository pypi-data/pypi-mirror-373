import torch
from torch import nn
from . import atomics, quantizers
from .density_matmul import Matmul, NoShiftMM
import numpy as np
from .quantizers import FixedRangeObserver
from ._utils import intitem
from fmot.nn import LUT as LUT_FP
from .luts import LUT, AddIdentityTLUT, ILUT
import fmot
from functools import partial
from .linear import Linear


class Div(nn.Module):
    def __init__(self, bitwidth, lut_bitwidth, bw_conf, interpolate):
        super().__init__()
        parent = LUT_FP(fmot.LUT_REGISTRY["aten::reciprocal"])
        self.recip = LUT._from_float(parent, bw_conf, interpolate)
        self.mul = atomics.VVMul(bitwidth)

    def forward(self, x, y):
        return self.mul(x, self.recip(y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        return cls(
            bitwidth=bw_conf.activations,
            lut_bitwidth=bw_conf.lut,
            bw_conf=bw_conf,
            interpolate=interpolate,
        )


class Mean(nn.Module):
    def __init__(self, dim, keepdim, bitwidth, biased):
        super().__init__()
        self.sum = atomics.Sum(dim, keepdim, bitwidth)
        self.muli = None
        self.N = None
        if isinstance(dim, int):
            dim = [dim]
        self.dim = dim
        self.bitwidth = bitwidth
        self.biased = biased

    def get_numel(self, x):
        shape = x.shape
        return np.prod([shape[d] for d in self.dim])

    def _init_muli(self, N):
        imm = 1 / N if self.biased else 1 / (N - 1)
        self.muli = atomics.VIMul(imm, self.bitwidth)
        self.N = N

    def forward(self, x):
        N = self.get_numel(x)
        if self.muli is None:
            self._init_muli(N)
        assert (
            N == self.N
        ), f"Mean expected to be taken over {self.N} elements, saw {N} instead"
        return self.muli(self.sum(x))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        return cls(
            dim=parent.dim,
            keepdim=parent.keepdim,
            bitwidth=bw_conf.activations,
            biased=parent.biased,
        )


class DepthWiseConvSummer(nn.Module):
    def __init__(self, in_channels, kernel_size, lin_list, bias, bitwidth):
        super().__init__()
        self.in_channels = in_channels
        self.kernel_size = kernel_size
        self.q_group = quantizers.PrecisionConstraint()
        self.weight_list = nn.ParameterList()
        self.bias = bias
        # self.weight_quant = [quantizers.ParameterQuantizer(bitwidth)
        #                         for _ in range(len(lin_list))]
        self.weight_quant = torch.nn.ModuleList(
            quantizers.ParameterQuantizer(bitwidth) for _ in range(len(lin_list))
        )
        for weight_q in self.weight_quant:
            self.q_group.add(weight_q)
        if self.bias:
            self.bias_list = nn.ParameterList()
            # self.bias_quant = [quantizers.ParameterQuantizer(bitwidth)
            #                     for i in range(len(lin_list))
            #                     if (i % self.kernel_size) == 0 ]
            self.bias_quant = torch.nn.ModuleList(
                quantizers.ParameterQuantizer(bitwidth)
                for i in range(len(lin_list))
                if (i % self.kernel_size) == 0
            )
            for bias_q in self.bias_quant:
                self.q_group.add(bias_q)

        for i, lin in enumerate(lin_list):
            self.weight_list.append(nn.Parameter(lin.weight.squeeze()))
            if (i % self.kernel_size) == 0 and self.bias:
                self.bias_list.append(lin.bias)

        self.add = atomics.VVAdd(bitwidth)
        self.mul = atomics.VVMul(bitwidth)

    def forward(self, x_list):
        output = []
        for i, weight in enumerate(self.weight_list):
            if i % self.kernel_size == 0:
                y = self.mul(x_list[i % self.kernel_size], self.weight_quant[i](weight))
                if self.bias:
                    bias_index = i // self.kernel_size
                    y = self.add(
                        y, self.bias_quant[bias_index](self.bias_list[bias_index])
                    )
            else:
                y = self.add(
                    y,
                    self.mul(
                        x_list[i % self.kernel_size], self.weight_quant[i](weight)
                    ),
                )
            if (i + 1) % self.kernel_size == 0:
                output.append(y)

        return y, output

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        return cls(
            in_channels=parent.in_channels,
            kernel_size=parent.kernel_size,
            lin_list=parent.lin_list,
            bias=parent.bias,
            bitwidth=bw_conf.activations,
        )


class LogMM(nn.Module):
    def __init__(
        self, act_bw, lut_bw, observer=quantizers.DEFAULT_OBSERVERS["default"]
    ):
        super().__init__()
        self.mm_big = Matmul(act_bw, observer=observer)
        self.mm_small = NoShiftMM(act_bw)
        self.lut_big = AddIdentityTLUT(torch.log, lut_bw, act_bw, observer=observer)
        self.lut_small = AddIdentityTLUT(torch.log, lut_bw, act_bw, observer=observer)
        self.gt0 = atomics.Gt0(act_bw)
        self.neg = atomics.Neg()
        self.oplus = atomics.VIAdd(1, act_bw, observer=observer)
        self.mul_big = atomics.VVMul(act_bw, observer=observer)
        self.mul_small = atomics.VVMul(act_bw, observer=observer)
        self.add_output = atomics.VVAdd(act_bw, observer=observer)

    def forward(self, x, matrix):
        y_big = self.mm_big(x, matrix)
        big = self.gt0(y_big)
        small = self.oplus(self.neg(big))
        y_small = self.mm_small(x, matrix)
        z_big = self.lut_big(y_big)
        z_big = self.mul_big(z_big, big)
        z_small = self.lut_small(y_small)
        z_small = self.mul_small(z_small, small)
        return self.add_output(z_big, z_small)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        observer = partial(observer, **observer_kwargs)
        return cls(bw_conf.activations, bw_conf.lut, observer=observer)


class LogEpsMM(nn.Module):
    def __init__(
        self, epsilon, act_bw, lut_bw, observer=quantizers.DEFAULT_OBSERVERS["default"]
    ):
        super().__init__()
        self.mm_big = Matmul(act_bw, observer=observer)
        self.mm_small = NoShiftMM(act_bw)
        self.lut_big = AddIdentityTLUT(torch.log, lut_bw, act_bw, observer=observer)
        self.lut_small = AddIdentityTLUT(torch.log, lut_bw, act_bw, observer=observer)
        self.gt0 = atomics.Gt0(act_bw)
        self.neg = atomics.Neg()
        self.add_eps_big = atomics.VIAdd(epsilon, act_bw, observer=observer)
        self.add_eps_small = atomics.VIAdd(epsilon, act_bw, observer=observer)
        self.oplus = atomics.VIAdd(1, act_bw, observer=observer)
        self.mul_big = atomics.VVMul(act_bw, observer=observer)
        self.mul_small = atomics.VVMul(act_bw, observer=observer)
        self.add_output = atomics.VVAdd(act_bw, observer=observer)

    def forward(self, x, matrix):
        y_big = self.mm_big(x, matrix)
        big = self.gt0(y_big)
        y_big = self.add_eps_big(y_big)
        small = self.oplus(self.neg(big))
        y_small = self.mm_small(x, matrix)
        y_small = self.add_eps_small(y_small)
        z_big = self.lut_big(y_big)
        z_big = self.mul_big(z_big, big)
        z_small = self.lut_small(y_small)
        z_small = self.mul_small(z_small, small)
        return self.add_output(z_big, z_small)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        observer = partial(observer, **observer_kwargs)
        return cls(parent.epsilon, bw_conf.activations, bw_conf.lut, observer=observer)


class TuningEpsilon(nn.Module):
    def __init__(
        self,
        bitwidth,
        running_max=0,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        eps=2**-14,
        alpha=0.99,
    ):
        super().__init__()
        self.eps = eps
        self.alpha = alpha
        if isinstance(running_max, torch.Tensor):
            running_max = running_max.clone().detach()
        else:
            running_max = torch.tensor(running_max)
        self.register_buffer("running_max", running_max)
        self.add = atomics.VIAdd(self.epsilon(), bitwidth, observer=observer)

    @torch.jit.ignore()
    def epsilon(self):
        return self.running_max * self.eps

    @torch.jit.ignore()
    @torch.no_grad()
    def update(self, x):
        """Updates the running max during training"""
        if self.training:
            xmax = torch.max(x).detach()
            if self.running_max == 0:
                self.running_max = xmax
            else:
                self.running_max = (
                    self.alpha * self.running_max + (1 - self.alpha) * xmax
                )

    def forward(self, x):
        self.update(x)
        self.add.imm.data = torch.ones_like(self.add.imm.data) * self.epsilon()
        return self.add(x)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        observer = partial(observer, **observer_kwargs)
        return cls(
            bw_conf.activations,
            running_max=parent.running_max,
            observer=observer,
            eps=parent.eps,
            alpha=parent.alpha,
        )
