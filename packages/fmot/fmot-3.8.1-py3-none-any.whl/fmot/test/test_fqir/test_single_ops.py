"""Tests for single ops"""
import numpy as np
import pytest
from fmot import fqir


def run_single_op(
    node, input_tprotos, input_vals, output_tproto=None, expected_output=None
):
    """Run a single Op in a Node"""
    graph = fqir.GraphProto()
    for inp in input_tprotos:
        graph.add_input(inp)
    graph.add_node(node)
    if output_tproto is not None:
        if not isinstance(output_tproto, (list, tuple)):
            output_tproto = [output_tproto]
        for out in output_tproto:
            graph.add_output(out)
    out_val = graph.run(*input_vals)
    if expected_output is not None:
        np.testing.assert_equal(out_val, expected_output)


@pytest.mark.parametrize("shamt_x,shamt_y", [[1, 0], [0, 1]])
def test_vvadd(shamt_x, shamt_y):
    """Test the vvadd operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    y = fqir.TensorProto("y", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    y_val = np.array([3, 4])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = (x_val << shamt_x) + (y_val << shamt_y)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvadd"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={
            "rounded": False,
            "shamt_x": shamt_x,
            "shamt_y": shamt_y,
            "shamt_bwred": 0,
            "bw": 8,
            "bw_x": 8,
            "bw_y": 8,
        },
    )

    run_single_op(node, [x, y], [x_val, y_val], z, z_val)


def test_viadd():
    """Test the viadd operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    # constant values
    y_val = 1
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val + y_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["viadd"],
        inputs={"x": x},
        outputs=[z],
        constants={
            "y": y_val,
            "shamt_x": 0,
            "shamt_y": 0,
            "shamt_bwred": 0,
            "bw": 8,
            "bw_x": 8,
            "bw_y": 8,
        },
    )

    run_single_op(node, [x], [x_val], z, z_val)


@pytest.mark.parametrize("shamt_x,shamt_y", [[1, 0], [0, 1]])
def test_vvsub(shamt_x, shamt_y):
    """Test the vvsub operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    y = fqir.TensorProto("y", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    y_val = np.array([3, 4])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = (x_val << shamt_x) - (y_val << shamt_y)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvsub"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={
            "shamt_x": shamt_x,
            "shamt_y": shamt_y,
            "shamt_bwred": 0,
            "bw": 8,
            "bw_x": 8,
            "bw_y": 8,
        },
    )

    run_single_op(node, [x, y], [x_val, y_val], z, z_val)


def test_vneg():
    """Test the vneg operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = -x_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vneg"],
        inputs={"x": x},
        outputs=[z],
        constants={"bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_vvmul():
    """Test the vvmul operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    y = fqir.TensorProto("y", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    y_val = np.array([3, 4])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val * y_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": False, "shamt_bwred": 0, "bw": 8},
    )

    run_single_op(node, [x, y], [x_val, y_val], z, z_val)


def test_vvmul_rounding():
    """Test the rounding to nearest logic in vvmul operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [1])
    y = fqir.TensorProto("y", int, [1])
    bw = 16
    # create some values for the inputs
    x_val = np.array([2**14])
    # define the output tensor
    z = fqir.TensorProto("z", int, [1])

    # This operation is expected to be rounded down
    y1_val = np.array([2])
    z1_val = np.array([1])  # calculate the expected output
    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": True, "shamt_bwred": -(bw - 1), "bw": bw},
    )

    run_single_op(node, [x, y], [x_val, y1_val], z, z1_val)

    # This operation is expected to be rounded up
    y2_val = np.array([2 + 1])
    z2_val = np.array(
        [2]
    )  # calculate the expected output, would have expected 1 without rounding
    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": True, "shamt_bwred": -(bw - 1), "bw": bw},
    )

    run_single_op(node, [x, y], [x_val, y2_val], z, z2_val)

    z3_val = np.array(
        [1]
    )  # calculate the expected output, would have expected 1 without rounding
    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vvmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": False, "shamt_bwred": -(bw - 1), "bw": bw},
    )

    run_single_op(node, [x, y], [x_val, y2_val], z, z3_val)


def test_vimul():
    """Test the vimul operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    y = fqir.TensorProto("y", int, [2])
    # create some values for the inputs
    x_val = np.array([1, 2])
    # define constants
    y_val = 2
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val * y_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["vimul"],
        inputs={"x": x},
        outputs=[z],
        constants={"y": y_val, "shamt_bwred": 0, "bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_matmul():
    """Test the matmul operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2, 2])
    y = fqir.TensorProto("y", int, [2, 2])
    # create some values for the inputs
    x_val = np.array([[1, 2], [3, 4]])
    y_val = np.array([[1, 2], [3, 4]])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val @ y_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["matmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": False, "shamt_bwred": 0, "bw_out": 8},
    )

    run_single_op(node, [x, y], [x_val, y_val], z, z_val)


def test_addmm():
    """Test the addmm operator"""
    # define the input tensors
    bias = fqir.TensorProto("bias", int, [2])
    x = fqir.TensorProto("x", int, [2, 2])
    y = fqir.TensorProto("y", int, [2, 2])
    # create some values for the inputs
    bias_val = np.array([0, 1])
    x_val = np.array([[1, 2], [3, 4]])
    y_val = np.array([1, 2])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val @ y_val + bias_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["addmm"],
        inputs={"bias": bias, "x": x, "y": y},
        outputs=[z],
        constants={"rounded": False, "shamt_bias": 0, "shamt_bwred": 0, "bw_out": 8},
    )

    run_single_op(node, [bias, x, y], [bias_val, x_val, y_val], z, z_val)


def test_relu():
    """Test the relu operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = np.clip(x_val, 0, None)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["relu"],
        inputs={"x": x},
        outputs=[z],
        constants={},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_lut():
    """Test the lut operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([0, 1])

    # define constants
    class Table:  # simple namespace
        def __init__(self):
            pass

    table = Table()
    table.x = np.arange(256)
    table.y = np.arange(256)
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = table.y[x_val]

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["lut"],
        inputs={"x": x},
        outputs=[z],
        constants={
            "shamt_address": 0,
            "bw_address": 8,
            "table": table,
            "function": "test",
        },
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_transpose():
    """Test the transpose operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2, 2])
    # create some values for the inputs
    x_val = np.array([[0, 1], [2, 3]])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2, 2])
    # calculate the expected output
    z_val = x_val.T

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["transpose"],
        inputs={"x": x},
        outputs=[z],
        constants={"dim0": 0, "dim1": 1},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_reshape():
    """Test the reshape operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2, 2])
    # create some values for the inputs
    x_val = np.array([[0, 1], [2, 3]])
    # define constants
    shape = (4,)
    # define the output tensor
    z = fqir.TensorProto("z", int, [2, 2])
    # calculate the expected output
    z_val = x_val.reshape(shape)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["reshape"],
        inputs={"x": x},
        outputs=[z],
        constants={"shape": shape},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_quantize():
    """Test the quantize operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([0.0, 0.5])
    # define constants
    quanta = -1
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = (x_val / (2**quanta)).astype(int)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["quantize"],
        inputs={"x": x},
        outputs=[z],
        constants={"quanta": quanta, "bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_dequantize():
    """Test the dequantize operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([0, 1])
    # define constants
    quanta = -1
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val.astype(float) * (2**quanta)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["dequantize"],
        inputs={"x": x},
        outputs=[z],
        constants={"quanta": quanta},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_chunk():
    """Test the chunk operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2, 2])
    # create some values for the inputs
    x_val = np.array([[0, 1], [2, 3]])
    # define the output tensor
    z0 = fqir.TensorProto("z0", int, [1, 2])
    z1 = fqir.TensorProto("z1", int, [1, 2])
    # calculate the expected output
    z0_val, z1_val = np.array_split(x_val, 2)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["chunk"],
        inputs={"x": x},
        outputs=[z0, z1],
        constants={"chunks": 2, "dim": 0},
    )

    run_single_op(node, [x], [x_val], [z0, z1], [z0_val, z1_val])


def test_cat():
    """Test the cat operator"""
    # define the input tensors
    x0 = fqir.TensorProto("x0", int, [2, 2])
    x1 = fqir.TensorProto("x1", int, [2, 2])
    # create some values for the inputs
    x0_val = np.array([[0, 1], [2, 3]])
    x1_val = np.array([[0, 1], [2, 3]])
    # define the output tensor
    z = fqir.TensorProto("z", int, [4, 2])
    # calculate the expected output
    z_val = np.concatenate([x0_val, x1_val])

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["cat"],
        inputs={"x0": x0, "x1": x1},
        outputs=[z],
        constants={"dim": 0},
    )

    run_single_op(node, [x0, x1], [x0_val, x1_val], z, z_val)


def test_stack():
    """Test the stack operator"""
    # define the input tensors
    x0 = fqir.TensorProto("x0", int, [2, 2])
    x1 = fqir.TensorProto("x1", int, [2, 2])
    # create some values for the inputs
    x0_val = np.array([[0, 1], [2, 3]])
    x1_val = np.array([[0, 1], [2, 3]])
    # define the output tensor
    z = fqir.TensorProto("z", int, [4, 2])
    # calculate the expected output
    z_val = np.stack([x0_val, x1_val])

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["stack"],
        inputs={"x0": x0, "x1": x1},
        outputs=[z],
        constants={"dim": 0},
    )

    run_single_op(node, [x0, x1], [x0_val, x1_val], z, z_val)


def test_zeros():
    """Test the zeros operator"""
    # define constants
    shape = (2,)
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = np.zeros(shape)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["zeros"],
        inputs={},
        outputs=[z],
        constants={"shape": shape},
    )

    run_single_op(node, [], [], z, z_val)


def test_sum():
    """Test the sum operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = np.sum(x_val)

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["sum"],
        inputs={"x": x},
        outputs=[z],
        constants={"dim": 0, "keepdim": False, "shamt_bwred": 0, "bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_assign():
    """Test the assign operator"""
    # define the input tensors
    y = fqir.TensorProto("y", int, [2])
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    y_val = np.array([-1, 1])
    x_val = np.array([-1, 1])

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["assign"],
        inputs={"y": y, "x": x},
        outputs=[],
        constants={},
    )

    run_single_op(node, [x, y], [x_val, y_val], None, None)


def test_constant_like():
    """Test the constant_like operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define constants
    imm = 2
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = np.ones_like(x_val) * imm

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["constant_like"],
        inputs={"x": x},
        outputs=[z],
        constants={"imm": imm},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_copy():
    """Test the copy operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["copy"],
        inputs={"x": x},
        outputs=[z],
        constants={},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_shift():
    """Test the shift operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define constants
    shamt = -1
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val << shamt if shamt >= 0 else x_val >> -shamt

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["shift"],
        inputs={"x": x},
        outputs=[z],
        constants={"shamt": shamt, "bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


def test_gt0():
    """Test the gt0 operator"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    # create some values for the inputs
    x_val = np.array([-1, 1])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    # calculate the expected output
    z_val = x_val.copy()
    z_val[z_val < 0] = 0

    node = fqir.NodeProto(
        name="",
        optype=fqir.registry_v1["gt0"],
        inputs={"x": x},
        outputs=[z],
        constants={"bw": 8},
    )

    run_single_op(node, [x], [x_val], z, z_val)


if __name__ == "__main__":
    test_chunk()
