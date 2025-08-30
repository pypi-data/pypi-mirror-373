from fmot import fqir


def kernelize_temporal_unfold(graph: fqir.GraphProto):
    """
    Adds init node for temporal unfold, and utilizes a buffer variable.
    """

    arith = graph.subgraphs["ARITH"]
    if "INIT" in graph.subgraphs:
        no_init = False
        init = graph.subgraphs["INIT"]
    else:
        no_init = True
        init = fqir.GraphProto(name="INIT")

    replace_dict = {}

    for node in arith.nodes:
        if node.opname == "temporal_unfold_unkernelized":
            new_node = get_unfold(node)
            replace_dict[node] = new_node

    if len(replace_dict) > 0:
        if no_init:
            init_node = fqir.NodeProto(
                name="INIT", optype=None, inputs={}, outputs=[], subgraph=init
            )
            graph.add_node(init_node)
            graph.add_subgraph("INIT", init)
        nodes = []
        for orig in arith.nodes:
            if orig in replace_dict:
                new = replace_dict[orig]
                nodes.append(new)

                buff = new.inputs["buffer"]
                zero_node = fqir.NodeProto(
                    name=f"init_{buff.name}",
                    optype=fqir.registry_v1["zeros"],
                    inputs={},
                    outputs=[buff],
                    constants={"shape": buff.shape},
                )
                init.add_node(zero_node)
            else:
                nodes.append(orig)
        arith.nodes = nodes

    return graph


def get_unfold(node):
    """7/28/23: raises an error if the temporal_unfold has stride != 1"""

    constants = node.constants
    stride = constants.pop("stride")
    if stride != 1:
        raise ValueError(
            f"Cannot kernelize temporal_unfold with stride != 1, had stride = {stride}"
        )

    buffer_length = constants["buffer_length"]
    x = node.inputs["x"]
    in_length = x.shape[0]
    buff_size = in_length * buffer_length

    buffer = fqir.TensorProto(
        name=f"%buffer_{x.name}", dtype=x.dtype, shape=[buff_size]
    )
    node = fqir.NodeProto(
        name=node.name,
        optype=fqir.registry_v1["temporal_unfold"],
        inputs={"x": x, "buffer": buffer},
        constants=constants,
        outputs=node.outputs,
        sourceref=node.sourceref,
    )

    return node


def add_conv2d_buffer(graph: fqir.GraphProto):
    """
    Adds buffer to conv2d nodes that need them.
    """

    arith = graph.subgraphs["ARITH"]
    if "INIT" in graph.subgraphs:
        no_init = False
        init = graph.subgraphs["INIT"]
    else:
        no_init = True
        init = fqir.GraphProto(name="INIT")

    num_changes = 0
    for node in arith.nodes:
        if node.opname == "temporal_conv2d":
            k_t = node.constants["kernel_size_t"]
            d_t = node.constants["dilation_t"]

            bufflen = (k_t - 1) * d_t

            if bufflen != 0:
                x = node.inputs["input"]
                x_len = x.shape[0]
                buffer = fqir.TensorProto(
                    name=f"%buffer_{x.name}", dtype=x.dtype, shape=[x_len * bufflen]
                )

                node.inputs["buffer"] = buffer

                zero_node = fqir.NodeProto(
                    name=f"init_{buffer.name}",
                    optype=fqir.registry_v1["zeros"],
                    inputs={},
                    outputs=[buffer],
                    constants={"shape": buffer.shape},
                )
                init.add_node(zero_node)
                num_changes += 1

    if num_changes > 0 and no_init:
        init_node = fqir.NodeProto(
            name="INIT", optype=None, inputs={}, outputs=[], subgraph=init
        )
        graph.add_node(init_node)
        graph.add_subgraph("INIT", init)
