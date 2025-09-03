import torch
from torch import nn
import fmot
from typing import *
import pytest


class LUTGradTester(nn.Module):
    def __init__(self, function, limits: Tuple[float, float]):
        super().__init__()
        self.function = function
        self.limits = limits

    def forward(self, x):
        return self.function(x)

    def get_input(self):
        return torch.linspace(*self.limits, 10000).reshape(10, -1)

    def sniff_grads(self):
        x = self.get_input()
        x.requires_grad = True

        y = self(x)
        loss = y.mean()
        loss.backward()

        return x.detach().flatten(), x.grad.flatten()

    def sniff_qgrads(self):
        cmodel = fmot.ConvertedModel(self)
        cmodel.quantize([self.get_input() for _ in range(3)])

        x = self.get_input()
        x.requires_grad = True

        y = self(x)
        loss = y.mean()
        loss.backward()

        return x.detach().flatten(), x.grad.flatten()


class Log(nn.Module):
    def forward(self, x):
        return x.log()


FNS = {
    "sigmoid": (nn.Sigmoid, (-8, 8)),
    "tanh": (nn.Tanh, (-4, 4)),
    "log": (Log, (2 ** (-14), 1)),
}


@pytest.mark.parametrize("function", FNS.keys())
def test_lut_gradients(function: str):
    fn, limits = FNS[function]
    tester = LUTGradTester(fn(), limits)

    x, g_fp = tester.sniff_grads()
    x, g_q = tester.sniff_qgrads()

    assert torch.all(g_fp == g_q)
