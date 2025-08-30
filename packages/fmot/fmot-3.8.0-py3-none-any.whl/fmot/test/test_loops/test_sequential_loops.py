"""
Sequential loops: loops that interate within sequencers (e.g. time-domain FIR)
"""
import torch
import fmot
from torch import nn, Tensor
from fmot.nn import Loop, Sequencer
import numpy as np
import pytest


class _FIRApplyLoop(Loop):
    def __init__(self, hop_length: int, b: np.ndarray | Tensor):
        super().__init__(
            n_iter=hop_length,
            n_recurse=1,
            slice_blocksizes=[1],
            slice_reversed=[False],
            concat_reversed=[False],
            dim=-1,
        )
        self.b = nn.Parameter(torch.as_tensor(b))

        self.hop_length = hop_length
        self.n_taps = len(b)

        self.n_taps_min_1 = len(b) - 1

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        (x_t,) = x_sliced
        (buff,) = x_recursed

        buff, _ = torch.split(buff, [self.n_taps_min_1, 1], -1)
        buff = torch.cat([x_t, buff], -1)

        bdot = buff * self.b
        bdot = torch.sum(bdot, -1, keepdim=True)

        return [buff], [bdot], [buff]


class _StandaloneFIRLoop(nn.Module):
    """Only for testing purposes..."""

    def __init__(self, hop_length: int, b: np.ndarray | Tensor):
        super().__init__()
        self.hop_length = hop_length
        self.n_taps = len(b)

        self.loop = _FIRApplyLoop(hop_length, b)
        self.zeros_init = nn.Parameter(torch.zeros(self.n_taps, self.hop_length))

    def forward(self, x):
        zero_init = torch.matmul(x, self.zeros_init.t())
        y, _ = self.loop(x_to_slice=[x], x_recursed_init=[zero_init], x_scope=[])
        return y


class _FIRApplySeq(Sequencer):
    def __init__(self, hop_length: int, b: np.ndarray | Tensor):
        self.n_taps = len(b)
        self.hop_length = hop_length

        super().__init__([[self.n_taps]], 0, 1)
        self.loop = _FIRApplyLoop(hop_length, b)

    @torch.jit.export
    def step(self, x_t: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        (buff,) = state
        y_t, buff = self.loop(x_to_slice=[x_t], x_recursed_init=[buff], x_scope=[])

        return y_t, [buff]


class FIRApply(nn.Module):
    def __init__(self, hop_length: int, b: np.ndarray | Tensor):
        super().__init__()
        self.hop_length = hop_length
        self.n_taps = len(b)
        self.wrapped = _FIRApplySeq(hop_length, b)

    def forward(self, x):
        y, _ = self.wrapped(x)
        return y


@pytest.mark.parametrize("b", [np.random.randn(16)])
@pytest.mark.parametrize("hop_length", [32])
def test_fir_apply(b: np.ndarray, hop_length: int):
    T = 2

    model = FIRApply(hop_length, b)

    y = model(torch.randn(8, T, hop_length))
    print(y.shape)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    cmodel.quantize([torch.randn(8, T, hop_length) for _ in range(10)])

    print("QUANTIZED!")

    graph = cmodel.trace()

    print(graph)
