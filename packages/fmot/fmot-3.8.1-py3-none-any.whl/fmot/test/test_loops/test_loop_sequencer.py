import torch
from torch import nn, Tensor
from fmot.nn import Loop
import fmot
import numpy as np
import pytest
from fmot.nn.atomics import GMACv2
from typing import List, Tuple


class Cat(torch.nn.Module):

    """
    Concatenates Tensor along the "Feature Dimension"
    """

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        out = torch.cat(x, dim=-1)
        return out


class Sub(torch.nn.Module):
    def __init__(self, act_precision=24):
        super().__init__()
        self.gmac = GMACv2(
            bits_out=act_precision, scalar_multipliers=torch.tensor([1, -1])
        )

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return self.gmac([], [], [x, y])


class Add(torch.nn.Module):
    def __init__(self, act_precision=24):
        super().__init__()
        self.gmac = GMACv2(
            bits_out=act_precision, scalar_multipliers=torch.tensor([1, 1])
        )

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return self.gmac([], [], [x, y])


class Multiply(torch.nn.Module):
    def __init__(self, act_precision=24):
        super().__init__()
        self.gmac = GMACv2(bits_out=act_precision)

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        out = self.gmac([x], [y], [])
        return out


class CastToPrecision(torch.nn.Module):
    def __init__(self, act_precision=16):
        super().__init__()
        self.gmac = GMACv2(bits_out=act_precision, scalar_multipliers=torch.tensor([1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.gmac([], [], [x])
        return out


class ZerosLike(torch.nn.Module):
    def __init__(self, act_precision=24):
        super().__init__()
        self.gmac = GMACv2(bits_out=act_precision, scalar_multipliers=torch.tensor([0]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.gmac([], [], [x])
        return out


"""
Use a Loop within a MIMO-Sequencer 
"""


class DummyLoop(Loop):
    def __init__(self, n_iter: int, n_channels: int, dim=-1, act_precision: int = 24):
        super().__init__(n_iter=n_iter, slice_blocksizes=[], n_recurse=2, dim=dim)
        self.add = Add(act_precision=act_precision)
        self.sub = Sub(act_precision=act_precision)
        self.mul = Multiply(act_precision=act_precision)

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        x_recurse_1, x_recurse_2 = x_recursed  # Shape: `n_channels`
        x_1, x_2 = x_scope  # Shape: `n_channels`

        next_state_1 = self.add(x_recurse_1, x_1)
        next_state_2 = self.sub(x_recurse_2, x_2)

        out = self.mul(next_state_1, next_state_2)

        # x_recurse', y_concat, y_final
        return [next_state_1, next_state_2], [], [next_state_1, next_state_2, out]


class _LoopInSequencer(fmot.nn.MIMOSequencer, fmot.nn.SuperStructure):
    """
    Set's up `LoopInSequencer`, that defines a Loop within a Sequencer.

    The test can either run with all activations in (a) INT-16/ INT-24
    """

    def __init__(self, activation_precision: int = 24, dim: int = 64, n_iter: int = 10):
        """
        Inputs:
            activation_precision (int): The activation precision of the test
            dim (int): The feature dimension

        The hidden-states will be set to whatever `activation_precision` is set to
        """
        self.activation_precision = activation_precision
        self.dim = dim
        self.n_iter = n_iter

        super().__init__(
            num_inputs=2,
            num_outputs=1,
            state_shapes=[[self.dim], [self.dim]],
            return_hidden_state=True,
        )

        self.loop = DummyLoop(
            n_iter=self.n_iter,
            n_channels=self.dim,
            dim=-1,
            act_precision=self.activation_precision,
        )

        self.cat = Cat()

    def step(
        self, inputs_t: List[torch.Tensor], state: List[torch.Tensor]
    ) -> Tuple[List[torch.Tensor], List[torch.Tensor]]:
        x0, x1 = inputs_t  # self.dim
        s0, s1 = state  # self.dim * self.n_iter

        x0_stack = []
        x1_stack = []
        for _ in range(self.n_iter):
            x0_stack.append(x0)
            x1_stack.append(x1)

        s0_next, s1_next, out = self.loop(
            [],  # x0, x1 (self.dim * self.n_iter)
            [s0, s1],  # s0, s1 (self.dim)
            [x0, x1],
        )

        new_state = []
        new_state.append(s0_next)
        new_state.append(s1_next)

        return [out], new_state


class LoopInSequencer(fmot.nn.SuperStructure):
    def __init__(self, activation_precision: int = 24, dim: int = 64, n_iter: int = 10):
        super().__init__()
        self.sequencer = _LoopInSequencer(
            activation_precision=activation_precision, dim=dim, n_iter=n_iter
        )
        self.cast16 = CastToPrecision(act_precision=16)

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        out, _ = self.sequencer([x, y])
        (out,) = out
        return self.cast16(out)


def test_loop_inside_sequencer(
    activation_prec: int = 24, dim: int = 24, n_iter: int = 4
):
    model = LoopInSequencer(
        activation_precision=activation_prec, dim=dim, n_iter=n_iter
    )

    x0, x1 = torch.ones(1, 5, dim), torch.ones(1, 5, dim)
    out = model(x0, x1)
    print(f"FP Out Pass!")

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    calib_data = [(x0, x1), (x0, x1)]

    cmodel.quantize(calib_data)

    out_cmodel = cmodel(x0, x1)
    print(f"Cmodel Out success")

    fqir_graph = cmodel.trace(*calib_data[0])
    print(f"FQIR Graph Tracing PASS")

    print(fqir_graph.subgraphs["ARITH"])

    out_fqir = fqir_graph.run(
        x0.squeeze().detach().cpu().numpy(),
        x1.squeeze().detach().cpu().numpy(),
        dequant=True,
    )
    print(f"FQIR Out Pass")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    test_loop_inside_sequencer(activation_prec=16, dim=64, n_iter=4)
