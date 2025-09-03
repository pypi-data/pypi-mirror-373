import torch
from torch import nn, Tensor
from . import quantizers
from functools import partial
from ..bitwidths import fqint4, fqint8, fqint16
from typing import *

# from fmot.nn import MultiDerivedParameter

BWS = {"int4": fqint4, "int8": fqint8, "int16": fqint16}


class QDerivedParameter(nn.Module):
    def __init__(
        self,
        bitwidth,
        parent: nn.Module,
        dimensions=None,
        observer=quantizers.DEFAULT_OBSERVERS["param"],
    ):
        super().__init__()
        self.weight_quant = quantizers.ParameterQuantizer(
            bitwidth, observer=observer, dimensions=dimensions
        )
        self.parent = parent

    def forward(self):
        x_deriv = self.parent.derive(self.parent.weight)
        y = self.weight_quant(x_deriv)
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["param"],
        **kwargs
    ):
        observer = partial(observer, **kwargs)
        if parent.is_weight:
            bw = bw_conf.weights
            dimensions = ["F", "F"]
        else:
            bw = bw_conf.activations
            dimensions = ["F"]
        return cls(bitwidth=bw, dimensions=dimensions, observer=observer, parent=parent)


class QMultiDerivedParameter(nn.Module):
    def __init__(self, param_bw, act_bw, parent):
        super().__init__()
        self.weight_quants = nn.ModuleList()
        for iw in parent.is_weight:
            if iw:
                obs = quantizers.DEFAULT_OBSERVERS["param"]
                bw = param_bw
            else:
                obs = quantizers.DEFAULT_OBSERVERS["default"]
                bw = act_bw
            self.weight_quants.append(
                quantizers.ParameterQuantizer(bitwidth=bw, observer=obs)
            )
        self.parent = parent

    def forward(self) -> List[Tensor]:
        x = [w for w in self.parent.weights]
        y_deriv = self.parent.derive(x)
        y_quant = [q(y) for q, y in zip(self.weight_quants, y_deriv)]
        return y_quant

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["param"],
        **kwargs
    ):
        observer = partial(observer, **kwargs)

        if parent.precision is not None:
            prec = BWS[parent.precision]
            param_bw = prec
            act_bw = prec
        else:
            param_bw = bw_conf.weights
            act_bw = bw_conf.activations

        return cls(param_bw=param_bw, act_bw=act_bw, parent=parent)
