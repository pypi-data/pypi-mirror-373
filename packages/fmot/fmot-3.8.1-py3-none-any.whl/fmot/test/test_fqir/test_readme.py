import numpy as np
from fmot import fqir


def test_readme():
    """Test the basic example in the FQIR README

    This fqir graph will take in two input vectors, add them together, and return the sum
    """
    # define the input tensors
    x = fqir.TensorProto("x", int, [8])
    y = fqir.TensorProto("y", int, [8])
    # define the output tensor
    z = fqir.TensorProto("z", int, [8])

    # define the addition operation using the fqir registry
    vvadd = fqir.NodeProto(
        name="op",
        optype=fqir.registry_v1["vvadd"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={
            "rounded": False,
            "shamt_x": 0,
            "shamt_y": 0,
            "shamt_bwred": 0,
            "bw": 8,
            "bw_x": 8,
            "bw_y": 8,
        },
    )

    # put the tensors and add op into a graph
    graph = fqir.GraphProto()
    graph.add_input(x)
    graph.add_input(y)
    graph.add_node(vvadd)
    graph.add_output(z)

    # create some values for the inputs
    x_val = np.arange(8)
    y_val = np.arange(8)
    # pass the inputs through the graph and generate the output
    z_val = graph.run(x_val, y_val)
    np.testing.assert_equal(z_val, x_val + y_val)


if __name__ == "__main__":
    test_readme()
