import numpy as np
from fmot.fqir.nodes.optypes import split_to_subprecisions
import pytest


@pytest.mark.parametrize(
    ["bw_tot", "bws"], [[31, [16, 16]], [24, [13, 12]], [24, [24]]]
)
def test_split_to_subprecisions(bw_tot: int, bws: list[int]):
    N = 1024
    x = np.random.randint(
        low=-(2 ** (bw_tot - 1)), high=2 ** (bw_tot - 1) - 1, size=N, dtype=np.int32
    )

    splits = split_to_subprecisions(x, bws)

    # check that each split falls within its defined bitwidth precision
    for i, (split, bw) in enumerate(zip(splits, bws)):
        min_v, max_v = -(1 << (bw - 1)), ((1 << (bw - 1)) - 1)
        if not (np.all(split >= min_v) and np.all(split <= max_v)):
            raise ValueError(
                f"split {i+1}/{len(bws)} not in {bw}-bit bounds\n\tmax: {np.max(split)} min: {np.min(split)}; lims: [{min_v}, {max_v}]"
            )
        else:
            print(
                f"split {i+1}/{len(bws)} in {bw}-bit bounds\n\tmax: {np.max(split)} min: {np.min(split)}; lims: [{min_v}, {max_v}]"
            )

    x_sim = 0
    shamt = 0
    for bw, split in zip(bws, splits):
        x_sim += split * 2 ** (shamt)
        shamt += bw - 1

    tot_bw = sum(bws) - len(bws) + 1
    x_clp = np.clip(x, -(2 ** (tot_bw - 1)), 2 ** (tot_bw - 1) - 1)

    # ensure that no truncation occured
    assert np.all(x_clp == x)

    if not np.array_equal(x_sim, x_clp):
        import matplotlib.pyplot as plt

        plt.plot(x_clp, x_sim, ".")
        plt.savefig("test.png")

        raise ValueError(f"diff: {x_clp - x_sim}\n{x_clp=}\n{x_sim=}")


if __name__ == "__main__":
    test_split_to_subprecisions(24, [13, 12])
