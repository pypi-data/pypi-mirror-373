import torch
from torch import nn, Tensor
from fmot.nn import Loop
import fmot
import numpy as np
import pytest


# Define graph-getter functions to help FM import and run tests from fmot loops


class SumLoop(Loop):
    def __init__(self, n_iter: int, n_channels: int, dim=-1):
        super().__init__(
            n_iter=n_iter, slice_blocksizes=[n_channels], n_recurse=1, dim=dim
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        (x_i,) = x_sliced
        (curr_sum,) = x_recursed

        y = x_i + curr_sum

        # x_recurse', y_concat, y_final
        return [y], [], [y]


class CumSumLoop(Loop):
    def __init__(self, n_iter: int, n_channels: int, dim=-1):
        super().__init__(
            n_iter=n_iter, slice_blocksizes=[n_channels], n_recurse=1, dim=dim
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        (x_i,) = x_sliced
        (curr_sum,) = x_recursed
        y = x_i + curr_sum

        # x_recurse', y_concat, y_final
        return [y], [y], []


class SumModel(nn.Module):
    def __init__(self, n_iter, n_channels, cumsum=False):
        super().__init__()
        if cumsum:
            self.summer = CumSumLoop(n_iter, n_channels)
        else:
            self.summer = SumLoop(n_iter, n_channels)
        self.n_channels = n_channels
        self.s_init = nn.Parameter(torch.zeros(n_channels), requires_grad=False)

    def forward(self, x):
        # summer(x_sliced, x_recurse_init, x_scope) -> [y_concat] + [y_final]
        (y,) = self.summer([x], [self.s_init], [])
        return y


class MeshSum(Loop):
    def __init__(self, n_iter: int, n_channels: int):
        super().__init__(
            n_iter=n_iter, n_recurse=1, slice_blocksizes=[n_iter * n_channels]
        )
        self.sum_inner = SumModel(n_iter, n_channels, cumsum=True)

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ):
        (x_i,) = x_sliced
        (curr_sum,) = x_recursed
        y = self.sum_inner(x_i) + curr_sum

        return [y], [y], []


class MeshSumModel(nn.Module):
    def __init__(self, n_iter, n_channels):
        super().__init__()
        self.mesh_sum = MeshSum(n_iter, n_channels)
        self.s_init = nn.Parameter(
            torch.zeros(n_channels * n_iter), requires_grad=False
        )

    def forward(self, x):
        (y,) = self.mesh_sum([x], [self.s_init], [])
        return y


def _get_sum(n_iter: int, n_channels: int, cumsum: bool):
    model = SumModel(n_iter=n_iter, n_channels=n_channels, cumsum=cumsum)

    cmodel = fmot.ConvertedModel(model, batch_dim=0)
    cmodel.quantize([torch.ones(8, n_iter * n_channels) for _ in range(10)])

    graph = cmodel.trace()

    return model, cmodel, graph


def get_sum(n_iter, n_channels):
    return _get_sum(n_iter, n_channels, cumsum=False)


def get_cumsum(n_iter, n_channels):
    return _get_sum(n_iter, n_channels, cumsum=True)


@pytest.mark.parametrize("n_iter", [8])
@pytest.mark.parametrize("n_channels", [4])
@pytest.mark.parametrize("cumsum", [True, False])
def test_sum(n_iter: int, n_channels: int, cumsum):
    model, cmodel, graph = _get_sum(n_iter, n_channels, cumsum)

    x = torch.ones(n_iter * n_channels)
    y0 = model(x).numpy()
    y1 = cmodel(x).numpy()
    y2 = graph.run(x.numpy(), dequant=True)

    assert np.all(y1 == y2)
    assert np.mean((y0 - y1) ** 2) < 1e-4


def get_nested_meshsum(n_iter, n_channels):
    model = MeshSumModel(n_iter=n_iter, n_channels=n_channels)

    cmodel = fmot.ConvertedModel(model, batch_dim=0)
    cmodel.quantize([torch.ones(8, n_iter**2 * n_channels) for _ in range(10)])

    graph = cmodel.trace()

    return model, cmodel, graph


@pytest.mark.parametrize("n_iter", [8])
@pytest.mark.parametrize("n_channels", [4])
def test_nested_meshsum(n_iter: int, n_channels: int):
    model, cmodel, graph = get_nested_meshsum(n_iter, n_channels)

    x = torch.ones(n_iter**2 * n_channels)
    y0 = model(x).numpy()
    y1 = cmodel(x).numpy()
    y2 = graph.run(x.numpy(), dequant=True)

    assert np.all(y1 == y2)
    assert np.mean((y0 - y1) ** 2) < 1e-4


class _LoopWithoutRecurse(Loop):
    """A loop that has no recursed state"""

    def __init__(self, n_iter: int, n_channels: int, dim=-1):
        super().__init__(
            n_iter=n_iter, slice_blocksizes=[n_channels], n_recurse=0, dim=dim
        )
        self.weight = nn.Parameter(torch.randn(n_channels))

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ):
        (x_i,) = x_sliced
        y = x_i + self.weight

        return [], [y], []


class LoopWithoutRecurse(nn.Module):
    """Wrapper for _LoopWithoutRecurse.
    Adds the same param vector to each subvector --> n_recuse = 0
    """

    def __init__(self, n_iter: int, n_channels: int, dim=-1):
        super().__init__()
        self.loop = _LoopWithoutRecurse(n_iter, n_channels, dim)

    def forward(self, x):
        (y,) = self.loop([x], [], [])
        return y


def get_loop_norecurse(n_iter, n_channels):
    model = LoopWithoutRecurse(n_iter=n_iter, n_channels=n_channels)

    cmodel = fmot.ConvertedModel(model, batch_dim=0)
    cmodel.quantize([torch.ones(8, n_iter**2 * n_channels) for _ in range(10)])

    graph = cmodel.trace()

    return model, cmodel, graph


@pytest.mark.parametrize("n_iter", [8])
@pytest.mark.parametrize("n_channels", [4])
@torch.no_grad()
def test_loop_norecurse(n_iter: int, n_channels: int):
    model, cmodel, graph = get_loop_norecurse(n_iter, n_channels)
    print(graph)

    x = torch.ones(n_iter**2 * n_channels)
    y0 = model(x).numpy()
    y1 = cmodel(x).numpy()
    y2 = graph.run(x.numpy(), dequant=True)

    assert np.all(y1 == y2)
    assert np.mean((y0 - y1) ** 2) < 1e-4


class _MulByRepeatedAddition(Loop):
    """This loop utilizes the x_scope field"""

    def __init__(self, n_iter: int, n_channels: int, dim=-1):
        super().__init__(n_iter=n_iter, n_recurse=1, slice_blocksizes=[], dim=-1)

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        """
        Args:
            x_sliced (list[Tensor]): list of sliced inputs for the current iteration,
                of same length as `self.slice_blocksizes`
            x_recursed (list[Tensor]): list of the current values of each of the recursed variables,
                of same length as `self.n_recursed`
            x_scope (list[Tensor]): list of globally scoped activations (these will be the same at each
                iteration of the loop)

        Returns: tuple[list[Tensor], list[Tensor], list[Tensor]]
            - x_recursed (list[Tensor]): updated values for each of the recursed variables
            - y_concat_i (list[Tensor]): outputs to be concatenated
            - y_final (list[Tensor]): outputs for which only the final value will be returned from the Loop
        """
        (sum_curr,) = x_recursed
        (x,) = x_scope

        y = sum_curr + x

        return [y], [], [y]


class MulByRepeatedAddition(nn.Module):
    def __init__(self, n_iter: int, n_channels: int):
        super().__init__()
        self.loop = _MulByRepeatedAddition(n_iter, n_channels, -1)
        self.zeros = nn.Parameter(torch.zeros(n_channels), requires_grad=False)

    def forward(self, x):
        (y,) = self.loop([], [self.zeros], [x])
        return y


def get_mul_repeated_add(n_iter, n_channels):
    model = MulByRepeatedAddition(n_iter=n_iter, n_channels=n_channels)
    cmodel = fmot.ConvertedModel(model, batch_dim=0)

    cmodel.quantize([torch.randn(8, n_channels) for _ in range(10)])

    graph = cmodel.trace()

    return model, cmodel, graph


@pytest.mark.parametrize("n_iter", [8, 31])
@pytest.mark.parametrize("n_channels", [4, 16])
@torch.no_grad()
def test_loop_with_scope(n_iter: int, n_channels: int):
    model, cmodel, graph = get_mul_repeated_add(n_iter, n_channels)

    x = torch.randn(n_channels)
    y0 = model(x).numpy()
    y1 = cmodel(x).numpy()
    y2 = graph.run(x.numpy(), dequant=True)
    x = x.numpy()

    assert np.allclose(y0, x * n_iter)
    assert np.allclose(y1, y2)
    assert np.mean((y0 - y1) ** 2) < 3e-2

    print("test passed!")


class _MultiSliceEchoLoop(Loop):
    """
    Simple echo loop to test slice/concat direction:
        - Two sliced inputs of unequal width.
        - slice_reversed  = [True,  False]  .. iterate first input backwards.
        - concat_reversed = [False, True]   .. concatenate second output backwards.
    Outputs (`y_concat_i`) are just the slices themselves so ordering is easy
    to inspect.
    """

    def __init__(self, n_iter: int, n_chan1: int, n_chan2: int, dim: int = -1):
        super().__init__(
            n_iter=n_iter,
            n_recurse=0,
            slice_blocksizes=[n_chan1, n_chan2],
            slice_reversed=[True, False],
            concat_reversed=[False, True],
            dim=dim,
        )

    @torch.jit.export
    def step(
        self,
        x_sliced: list[Tensor],
        x_recursed: list[Tensor],
        x_scope: list[Tensor],
    ):
        x1, x2 = x_sliced
        x1 = x1 + 0
        x2 = x2 + 0
        # x_recurse, x_concat, x_final
        return [], [x1, x2], []


class MultiSliceEchoModel(nn.Module):
    def __init__(self, n_iter: int, n_chan1: int, n_chan2: int):
        super().__init__()
        self.loop = _MultiSliceEchoLoop(n_iter, n_chan1, n_chan2)

    def forward(self, x1: Tensor, x2: Tensor):
        y1, y2 = self.loop([x1, x2], [], [])
        return y1, y2


def _get_multi_slice_loop(n_iter: int, n_chan1: int, n_chan2: int):
    """Helper to build eager, quantised, and traced versions."""
    model = MultiSliceEchoModel(n_iter, n_chan1, n_chan2)

    cmodel = fmot.ConvertedModel(model, batch_dim=0)
    cmodel.quantize(
        [
            (
                torch.randn(4, n_iter * n_chan1),
                torch.randn(4, n_iter * n_chan2),
            )
            for _ in range(6)
        ]
    )
    graph = cmodel.trace()
    return model, cmodel, graph


@pytest.mark.parametrize("n_iter", [4])
@pytest.mark.parametrize("dims", [(2, 3)])  # unequal block sizes
def test_multi_slice_reverse_concat(n_iter: int, dims: tuple[int, int]):
    """
    Validate that:
      - slice_reversed modifies iteration order for the first tensor.
      - concat_reversed modifies concatenation order for the second tensor.
      - ConvertedModel and traced Graph outputs match  reference.
    """
    n_chan1, n_chan2 = dims
    model, cmodel, graph = _get_multi_slice_loop(n_iter, n_chan1, n_chan2)

    # Deterministic inputs (0…N) make ordering obvious.
    x1 = torch.randn(n_iter * n_chan1, dtype=torch.float32)
    x2 = torch.randn(n_iter * n_chan2, dtype=torch.float32)

    y_ref1, y_ref2 = model(x1, x2)
    y_q1, y_q2 = cmodel(x1, x2)
    y_g1, y_g2 = graph.run(x1.numpy(), x2.numpy(), dequant=True)

    # Expected ordering
    # first tensor: reverse order at slice time → already backwards
    exp1 = (
        torch.flip(
            x1.view(n_iter, n_chan1), dims=[0]
        )  # flip over iteration axis --- reverse over iterations
        .contiguous()
        .view(-1)
        .numpy()
    )
    # second tensor: normal slices but reverse order at concat
    exp2 = (
        torch.flip(
            x2.view(n_iter, n_chan2), dims=[0]
        )  # flip over iteration axis --- reverse before final cat
        .contiguous()
        .view(-1)
        .numpy()
    )

    # FP <--> Expected
    assert np.allclose(y_ref1.numpy(), exp1)
    assert np.allclose(y_ref2.numpy(), exp2)

    # FP <--> Qmodel
    assert np.allclose(y_q1.numpy(), y_g1)
    assert np.allclose(y_q2.numpy(), y_g2)

    # FP <--> FQIR
    assert np.mean((y_ref1.numpy() - y_q1.numpy()) ** 2) < 1e-4
    assert np.mean((y_ref2.numpy() - y_q2.numpy()) ** 2) < 1e-4


class LoopWithBroadcast(Loop):
    """TODO: testcase to ensure that broadcast works for loop"""

    pass


class LoopWithI24Recursion(Loop):
    """TODO: testcase for int24 recursion variable"""

    pass


class LoopWithI24Sliced(Loop):
    """TODO: testcase for int24 recursion variable"""

    pass


class LoopWithI24Concat(Loop):
    """TODO: testcase for int24 recursion variable"""

    pass


if __name__ == "__main__":
    # test_sum(n_iter=10, n_channels=16, cumsum=True)
    # test_nested_meshsum(n_iter=10, n_channels=16)
    # test_loop_norecurse(10, 16)
    # test_loop_with_scope(8, 4)
    test_multi_slice_reverse_concat(8, (10, 12))
