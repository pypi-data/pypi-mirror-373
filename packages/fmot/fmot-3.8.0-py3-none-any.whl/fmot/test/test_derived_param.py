import torch
from torch import nn
import fmot
import numpy as np
from torch import Tensor
import pytest
from typing import *


def base_test_run(
    model: nn.Module, shape: Tuple[int], batch_dim=0, seq_dim=None, fp_tol=1e-6
):
    cmodel = fmot.ConvertedModel(model, batch_dim=batch_dim, seq_dim=seq_dim)

    # check that converted model matches f.p.
    with torch.no_grad():
        x = torch.randn(*shape)
        y0 = model(x)
        y1 = cmodel(x)

    diff = torch.mean((y0 - y1) ** 2)
    if diff > fp_tol:
        raise ValueError(
            f"Full-precision diff {diff:.3E} was above tolerance {fp_tol:.3E}"
        )

    # check that the model can quantize
    cmodel.quantize([torch.randn(*shape) for _ in range(4)])
    graph = cmodel.trace()

    # check that the FQIR matches the quantized model
    q_shape = (1, *shape[1:])
    x = torch.randn(q_shape)
    with torch.no_grad():
        y0 = cmodel(x).squeeze(0).numpy()
    y1 = graph.run(x.numpy()[0], dequant=True)

    assert np.array_equal(y0, y1)


def test_neg_param():
    class NegativeParam(fmot.nn.DerivedParameter):
        """Computes parameter as -exp(weight/self.alpha) to constrain the weight
        to be negative"""

        def __init__(self, alpha, shape):
            weight = torch.randn(*shape)
            super().__init__(weight)
            self.alpha = alpha

        def derive(self, weight):
            return -torch.exp(weight / self.alpha)

    class MyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = NegativeParam(1, (32, 32))

        def forward(self, x):
            return torch.matmul(x, self.weight().T)

    base_test_run(MyModel(), (8, 32))


def test_diag_matrix():
    class DiagMatrix(fmot.nn.DerivedParameter):
        def derive(self, weight):
            return torch.diag(weight)

    class MyDiagModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = DiagMatrix(torch.randn(32))

        def forward(self, x):
            return torch.matmul(x, self.weight().T)

    base_test_run(MyDiagModel(), (8, 32))


def test_multiparam_0():
    class MyMultiParam(fmot.nn.MultiDerivedParameter):
        def derive(self, weights: List[Tensor]):
            w0, w1 = weights
            return (w0 + w1, w0 - w1)

    class MyMultiModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weights = MyMultiParam(torch.randn(32), torch.randn(32))

        def forward(self, x):
            weights = self.weights()
            w0, w1 = weights
            return w0 + x + w1

    base_test_run(MyMultiModel(), (8, 32))


def test_sequencer_caching():
    """Tests whether derived param in sequencer gets efficiently cached"""

    class DCounter(fmot.nn.DerivedParameter):
        """Counts how many times its been derived"""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.register_buffer("n_derive", torch.tensor(0))

        def derive(self, weight):
            self.n_derive += 1
            return weight

    class MySeq(fmot.nn.Sequencer):
        def __init__(self):
            super().__init__([[32]])
            self.weight = DCounter(torch.randn(32))

        @torch.jit.export
        def step(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
            y = x * self.weight()
            return y, []

    model = MySeq()

    dcounter = model.weight

    model(torch.randn(1, 8, 32))
    assert dcounter.n_derive.item() == 8

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    q_dcounter = cmodel.model.model.weight.parent
    cmodel(torch.randn(1, 8, 32))
    assert q_dcounter.n_derive == 16

    cmodel.quantize([torch.randn(1, 8, 32) for _ in range(4)])
    print(q_dcounter.n_derive)


if __name__ == "__main__":
    # test_neg_param()
    # test_diag_matrix()
    # test_multiparam_0()

    test_sequencer_caching()
