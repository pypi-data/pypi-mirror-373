import math
from functools import partial

import torch
from torch import nn
from fmot import CONFIG
from . import atomics, quantizers
from .density_matmul import AddMM, Matmul
from ..annotated_tensors import set_dim_annotations, check_for_annotations


class Linear(torch.nn.Module):
    def __init__(
        self,
        in_features,
        out_features,
        act_bitwidth,
        par_bitwidth,
        bias=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        mm_limits=None,
    ):
        super().__init__()

        self.q_group = quantizers.PrecisionConstraint()

        self.in_features = in_features
        self.out_features = out_features

        self.requant_in = atomics.Requantize(act_bitwidth, observer)
        self.q_group.recursively_add(self.requant_in)
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        self.weight_quant = quantizers.ParameterQuantizer(
            par_bitwidth, observer=quantizers.DEFAULT_OBSERVERS["param"]
        )
        self.q_group.add(self.weight_quant)
        self.weight_transpose = atomics.Transpose()

        if mm_limits is None:
            mm_observer = observer
        else:
            mm_observer = partial(quantizers.FixedRangeObserver, limits=mm_limits)

        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
            set_dim_annotations(["F"], self.bias)
            self.multiplier = AddMM(act_bitwidth, observer=mm_observer)
            self.bias_quant = quantizers.ParameterQuantizer(
                act_bitwidth, observer=quantizers.DEFAULT_OBSERVERS["param"]
            )
        else:
            self.register_parameter("bias", None)
            self.multiplier = Matmul(act_bitwidth, observer=mm_observer)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)

    @check_for_annotations
    def forward(self, x):
        x = self.requant_in(x)
        set_dim_annotations(["F", "F"], self.weight)
        weight = self.weight_quant(self.weight)
        weight = self.weight_transpose(weight)
        set_dim_annotations(["F", "F"], weight)
        if self.bias is not None:
            bias = self.bias_quant(self.bias)
            set_dim_annotations(["F"], bias)
            return self.multiplier(bias, x, weight)
        else:
            return self.multiplier(x, weight)

    def __repr__(self):
        return "QuantLinear(in_features={}, out_features={}, bias={}, act_bw={}, par_bw={})".format(
            self.in_features,
            self.out_features,
            self.bias is not None,
            self.multiplier.quantizer.bitwidth,
            self.weight_quant.bitwidth,
        )

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs
    ):
        observer = partial(observer, **kwargs)
        limits = None
        if hasattr(parent, "limits"):
            limits = parent.limits
        kwargs = dict(
            in_features=parent.in_features,
            out_features=parent.out_features,
            act_bitwidth=bw_conf.activations,
            par_bitwidth=bw_conf.weights,
            bias=parent.bias is not None,
            observer=observer,
            mm_limits=limits,
        )
        if CONFIG.pow2_linear_scale:
            model = cls(**kwargs)
        else:
            if not CONFIG.perchannel_linear:
                model = AffineLinear(**kwargs)
            else:
                model = PerChannelAffineLinear(**kwargs)
        model.weight.data = parent.weight.data
        if model.bias is not None:
            model.bias.data = parent.bias.data
        return model


class AffineLinear(Linear):
    def __init__(
        self,
        in_features,
        out_features,
        act_bitwidth,
        par_bitwidth,
        bias=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        mm_limits=None,
    ):
        if mm_limits is not None:
            mul_limits = tuple(
                map(lambda x: 2 * x if x is not None else None, mm_limits)
            )
            vimul_obs = partial(quantizers.FixedRangeObserver, limits=mm_limits)
        else:
            mul_limits = None
            vimul_obs = observer
        super().__init__(
            in_features,
            out_features,
            act_bitwidth,
            par_bitwidth,
            bias,
            observer,
            mm_limits=mul_limits,
        )
        self.vimul = atomics.VIMul(1, act_bitwidth, vimul_obs)

        bw = par_bitwidth.bitwidth
        self.factor = (2 ** (bw - 1) - 1) / 2 ** (bw - 1)

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, x):
        x = self.requant_in(x)

        wmax = torch.max(torch.abs(self.weight)) / self.factor
        with torch.no_grad():
            p2fact = torch.ceil(torch.log2(wmax))
        wmax = wmax / 2 ** (p2fact)
        w_normed = self.weight / wmax
        set_dim_annotations(["F", "F"], w_normed)
        w_normed = self.weight_quant(w_normed)
        set_dim_annotations(["F", "F"], w_normed)
        w_normed = self.weight_transpose(w_normed)
        if self.bias is not None:
            b_normed = self.bias / wmax
            set_dim_annotations(["F"], b_normed)
            b_normed = self.bias_quant(b_normed)
            set_dim_annotations(["F"], b_normed)

            out_normed = self.multiplier(b_normed, x, w_normed)

        else:
            out_normed = self.multiplier(x, w_normed)

        self.vimul.imm.data = wmax
        out = self.vimul(out_normed)
        return out

    def __repr__(self):
        return "QuantAffineLinear(in_features={}, out_features={}, bias={}, act_bw={}, par_bw={})".format(
            self.in_features,
            self.out_features,
            self.bias is not None,
            self.multiplier.quantizer.bitwidth,
            self.weight_quant.bitwidth,
        )


class PerChannelAffineLinear(Linear):
    def __init__(
        self,
        in_features,
        out_features,
        act_bitwidth,
        par_bitwidth,
        bias=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        mm_limits=None,
    ):
        if mm_limits is not None:
            mul_limits = tuple(
                map(lambda x: 2 * x if x is not None else None, mm_limits)
            )
            vvmul_obs = partial(quantizers.FixedRangeObserver, limits=mm_limits)
        else:
            mul_limits = None
            vvmul_obs = observer
        super().__init__(
            in_features,
            out_features,
            act_bitwidth,
            par_bitwidth,
            bias,
            observer,
            mm_limits=mul_limits,
        )

        self.norm_quant = quantizers.ParameterQuantizer(act_bitwidth, observer=observer)
        self.renorm = atomics.VVMul(act_bitwidth, vvmul_obs)

        bw = par_bitwidth.bitwidth
        self.factor = (2 ** (bw - 1) - 1) / 2 ** (bw - 1)

    def forward(self, x):
        x = self.requant_in(x)

        max_per_chan, __ = torch.abs(self.weight).max(dim=-1)
        max_per_chan = max_per_chan / self.factor + 1e-6

        with torch.no_grad():
            p2fact = torch.ceil(torch.log2(max_per_chan.max()))
        max_per_chan = max_per_chan / 2 ** (p2fact)

        w_normed = self.weight / max_per_chan.unsqueeze(-1)
        set_dim_annotations(["F", "F"], w_normed)
        w_normed = self.weight_quant(w_normed)
        set_dim_annotations(["F", "F"], w_normed)
        w_normed = self.weight_transpose(w_normed)
        if self.bias is not None:
            b_normed = self.bias / max_per_chan
            set_dim_annotations(["F"], b_normed)
            b_normed = self.bias_quant(b_normed)
            set_dim_annotations(["F"], b_normed)

            out_normed = self.multiplier(b_normed, x, w_normed)

        else:
            out_normed = self.multiplier(x, w_normed)

        norm = self.norm_quant(max_per_chan)
        out = self.renorm(out_normed, norm)
        return out

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs
    ):
        observer = partial(observer, **kwargs)
        model = cls(
            in_features=parent.in_features,
            out_features=parent.out_features,
            act_bitwidth=bw_conf.activations,
            par_bitwidth=bw_conf.weights,
            bias=parent.bias is not None,
            observer=observer,
        )
        model.weight.data = parent.weight.data
        if model.bias is not None:
            model.bias.data = parent.bias.data
        return model

    def __repr__(self):
        return "QuantPerChannelAffineLinear(in_features={}, out_features={}, bias={}, act_bw={}, par_bw={})".format(
            self.in_features,
            self.out_features,
            self.bias is not None,
            self.multiplier.quantizer.bitwidth,
            self.weight_quant.bitwidth,
        )
