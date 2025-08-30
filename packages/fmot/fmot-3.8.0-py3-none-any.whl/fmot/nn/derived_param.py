import torch
from torch import nn, Tensor
from fmot.nn import SuperStructure
from typing import *


class DerivedParameter(SuperStructure):
    """A parameter that is statically transformed before being used.
    Static transformation usually used to enforce a constraint.

    Overwrite the "derive" method for specific instantiations
    """

    def __init__(self, weight: Tensor, requires_grad=True):
        super().__init__()
        self.weight = nn.Parameter(weight, requires_grad=requires_grad)
        self.is_weight = False
        self.requires_grad = requires_grad

    def derive(self, x: Tensor) -> Tensor:
        raise NotImplementedError

    @torch.jit.ignore
    def forward(self):
        x = self.weight
        self.is_weight = x.ndim == 2
        return self.derive(x)


class SigmoidConstraintParameter(DerivedParameter):
    def derive(self, x: Tensor) -> Tensor:
        return x.sigmoid()


class MultiDerivedParameter(SuperStructure):
    def __init__(self, *weights: List[Tensor], requires_grad=True, precision=None):
        super().__init__()
        self.weights = nn.ParameterList()
        for w in weights:
            self.weights.append(nn.Parameter(w, requires_grad=requires_grad))
        self.requires_grad = requires_grad
        self.is_weight = [True] * len(self.weights)
        self.precision = precision

    def derive(self, x: List[Tensor]) -> List[Tensor]:
        raise NotImplementedError

    def forward(self) -> List[Tensor]:
        x = [w for w in self.weights]
        out = self.derive(x)
        self.is_weight = [y.ndim == 2 for y in out]
        return out
