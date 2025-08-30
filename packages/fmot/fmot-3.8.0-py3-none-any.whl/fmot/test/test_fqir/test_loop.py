from fmot.fqir import GraphProto, NodeProto, TensorProto, registry_v1
import numpy as np
from functools import partial
import pytest


def get_sum_graph(niter: int, n_channels: int):
    loop_body = GraphProto(name="sum_loop")
    sum_in = TensorProto(
        name="sum_in",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    x_slice = TensorProto(
        name="x_slice",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    sum_out = TensorProto(
        name="sum_out",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )

    # loop input order: [recursed_input_0, ..., sliced_input_0, ...]
    # sum_in is recursed (updated with each graph execution), goes first
    # x_slice is sliced, goes next
    loop_body.add_input(sum_in)
    loop_body.add_input(x_slice)
    add = NodeProto(
        name="add",
        optype=registry_v1["vvadd"],
        inputs={"x": x_slice, "y": sum_in},
        outputs=[sum_out],
        constants={
            "shamt_x": 0,
            "shamt_y": 0,
            "shamt_bwred": 0,
            "bw": 16,
            "bw_x": 16,
            "bw_y": 16,
        },
    )
    loop_body.add_node(add)

    # loop output order: [recursed_update_0, ..., concat_output_0, ..., final_output_0]
    # sum_out is serving as both a recursed_update (for sum_in), as well as a final output, so
    # the loop body returns it twice
    # we don't have any concat outputs
    loop_body.add_output(sum_out)
    loop_body.add_output(sum_out)

    arith = GraphProto(name="ARITH")
    x_in = TensorProto(
        name="x_sequence",
        dtype="fqint16",
        shape=[
            n_channels * niter,
        ],
    )
    sum_init = TensorProto(
        name="sum_init",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    sum_final = TensorProto(
        name="sum_final",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )

    arith.add_input(x_in)

    if True:
        sum_init.value = np.zeros(n_channels, dtype=np.int32)
        arith.add_parameter(sum_init)
    else:
        zeros = NodeProto(
            name="zeros",
            optype=registry_v1["zeros"],
            inputs={},
            outputs=[sum_init],
            constants={
                "shape": [
                    n_channels,
                ]
            },
        )
        arith.add_node(zeros)

    loop_node = NodeProto(
        name="loop",
        optype=registry_v1["loop"],
        inputs={"x_recurse_0": sum_init, "x_sliced_0": x_in},
        outputs=[sum_final],
        constants={
            "n_iter": niter,
            "n_recurse": 1,
            "n_sliced": 1,
            "n_concat": 0,
            "n_final": 1,
            "n_scope": 0,
            "block_size_sliced": [n_channels],
            "reverse_sliced": [False],
            "reverse_concat": [],
        },
        subgraph=loop_body,
    )
    arith.add_node(loop_node)
    arith.add_output(sum_final)

    def runtime(x):
        x_rsh = np.reshape(x, (niter, n_channels))
        return np.sum(x_rsh, axis=0)

    return arith, runtime


def get_cumsum_graph(niter, n_channels, reversed=False):
    loop_body = GraphProto(name="cumsum_loop")
    sum_in = TensorProto(
        name="sum_in",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    x_slice = TensorProto(
        name="x_slice",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    sum_out = TensorProto(
        name="sum_out",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )

    # loop input order: [recursed_input_0, ..., sliced_input_0, ...]
    # sum_in is recursed (updated with each graph execution), goes first
    # x_slice is sliced, goes next
    loop_body.add_input(sum_in)
    loop_body.add_input(x_slice)
    add = NodeProto(
        name="add",
        optype=registry_v1["vvadd"],
        inputs={"x": x_slice, "y": sum_in},
        outputs=[sum_out],
        constants={
            "shamt_x": 0,
            "shamt_y": 0,
            "shamt_bwred": 0,
            "bw": 16,
            "bw_x": 16,
            "bw_y": 16,
        },
    )
    loop_body.add_node(add)

    # loop output order: [recursed_update_0, ..., concat_output_0, ..., final_output_0]
    # sum_out is serving as both a recursed_update (for sum_in), as well as a concat output, so
    # the loop body returns it twice
    # we don't have any final outputs
    loop_body.add_output(sum_out)
    loop_body.add_output(sum_out)

    arith = GraphProto(name="ARITH")
    x_in = TensorProto(
        name="x_sequence",
        dtype="fqint16",
        shape=[
            n_channels * niter,
        ],
    )
    sum_init = TensorProto(
        name="sum_init",
        dtype="fqint16",
        shape=[
            n_channels,
        ],
    )
    sum_final = TensorProto(
        name="cumsum",
        dtype="fqint16",
        shape=[
            n_channels * niter,
        ],
    )

    arith.add_input(x_in)
    zeros = NodeProto(
        name="zeros",
        optype=registry_v1["zeros"],
        inputs={},
        outputs=[sum_init],
        constants={
            "shape": [
                n_channels,
            ]
        },
    )
    arith.add_node(zeros)

    loop_node = NodeProto(
        name="loop",
        optype=registry_v1["loop"],
        inputs={"x_recurse_0": sum_init, "x_sliced_0": x_in},
        outputs=[sum_final],
        constants={
            "n_iter": niter,
            "n_recurse": 1,
            "n_sliced": 1,
            "n_concat": 1,
            "n_final": 0,
            "n_scope": 0,
            "block_size_sliced": [n_channels],
            "reverse_sliced": [reversed],
            "reverse_concat": [reversed],
        },
        subgraph=loop_body,
    )
    arith.add_node(loop_node)
    arith.add_output(sum_final)

    def runtime(x):
        x_rsh = np.reshape(x, (niter, n_channels))
        if reversed:
            x_rsh = x_rsh[::-1]
        y = np.cumsum(x_rsh, axis=0)
        if reversed:
            y = y[::-1]
        y = y.flatten()
        return y

    return arith, runtime


SINGLE_LOOP_TESTCASES = {
    "cumsum": partial(get_cumsum_graph, reversed=False),
    "cumsum-reversed": partial(get_cumsum_graph, reversed=True),
    "sum": get_sum_graph,
}


@pytest.mark.parametrize("case_name", SINGLE_LOOP_TESTCASES.keys())
@pytest.mark.parametrize("n_iter", [1, 8])
@pytest.mark.parametrize("n_channels", [16])
def test_single_loop(case_name: str, n_channels: int, n_iter: int, print_graph=False):
    print(f"TESTING {case_name}(n_iter={n_iter}, n_channels={n_channels})")

    graph, runtime = SINGLE_LOOP_TESTCASES[case_name](n_iter, n_channels)

    x = (np.ones(n_iter * n_channels)).astype(np.int16)
    y_graph = graph.run(x)
    y_gt = runtime(x)

    assert np.all(y_graph == y_gt)
    print("   SUCCESS!")

    if print_graph:
        print(graph)


if __name__ == "__main__":
    # test_single_loop("cumsum", n_channels=16, n_iter=8)
    # test_single_loop("cumsum-reversed", n_channels=16, n_iter=8)
    test_single_loop("sum", n_channels=1, n_iter=8, print_graph=True)
