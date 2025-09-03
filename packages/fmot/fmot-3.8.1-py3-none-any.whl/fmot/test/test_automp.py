"""Test the automatic mixed precision abilities of the converter"""
import torch
from torch import nn
import fmot


def test_auto_mixedprecision():
    r"""Test that the automatic mix-precision api does not break"""
    model = nn.Sequential(
        nn.Linear(32, 256),
        nn.ReLU(),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Linear(128, 128),
        nn.ReLU(),
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Linear(128, 32),
    )

    inputs = [torch.randn(10, 32) for _ in range(10)]
    targets = [model(x) for x in inputs]

    def objective(y, target):
        return (y - target).pow(2).mean() / (target.pow(2).mean())

    qmodel = fmot.ConvertedModel(model, precision="double", interpolate=False)
    qmodel.quantize(inputs)

    fmot.beta.optimize_mixed_precision(qmodel, objective, 0.4, inputs, targets)
