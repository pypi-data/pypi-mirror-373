import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_inputs(node, objs):
    """Pull a node's inputs out of the object dictionary, append the node's constant parameters

    Args:
        node (:class:`NodeProto`): Node to retrieve inputs for
        objs (dict of {name`:`value}):
    Returns:
        dict: Mapping argument names (e.g. Op argument names) to TensorProtos
    """
    try:
        inputs = {argname: objs[tproto.name] for argname, tproto in node.inputs.items()}
    except Exception as e:
        raise RuntimeError(f"{str(e)}\n{node=}, {node.inputs=} {objs.keys()=}")
    inputs.update(node.constants)
    return inputs


def store_outputs(node, outputs, objs):
    """Store a Node's outputs with its corresponding output :class:`TensorProto`

    Association stored in the graph object-value tracker dictionary

    Args:
        node (:class:`NodeProto`): Node that generated the outputs
        outputs (:obj:`numpy.ndarray` or tuple of): Node outputs
        objs (dict of {name`:`value}): Graph object-value tracker
    """
    if not isinstance(outputs, tuple):
        outputs = (outputs,)
    for proto, x in zip(node.outputs, outputs):
        objs[proto.name] = x


def run_graph(
    graph,
    *inputs,
    return_objs=False,
    objs=None,
    skipped_subgraphs=None,
    dequant=False,
    return_dict=False,
):
    """Run a GraphProto

    Nodes are executed in the order they were added (see :attr:`fqir.GraphProto.add_node`)

    Args:
        graph (:class:`fqir.GraphProto`): Graph to run
        inputs (:class:`numpy.ndarray`): Input tensors. Order must match runtime signature
        return_objs (bool, optional): Return the runtime state dictionary.
            Maps :class:`TensorProto` names to values
        objs (dict, optional): Track which graph objects have which values. Used in recursion
        skipped_subgraphs (list of [str], optional): list of subgraph names to skip
        dequant (bool, optional): Perform dequantization
        return_dict (bool, optional): Return graph output as a dictionary mapping object to value.
            Otherwise, just returns the values
    """
    if skipped_subgraphs is None:
        skipped_subgraphs = []
    if objs is None:
        objs = {}
    for tproto, x in zip(graph.inputs, inputs):  # load inputs
        objs[tproto.name] = x
    for tproto in graph.parameters:  # load parameters
        objs[tproto.name] = tproto.value
    for node in graph.nodes:
        inputs = get_inputs(node, objs)
        if node.subgraph is not None and node.subgraph.name not in skipped_subgraphs:
            if node.optype is not None:
                try:
                    outputs = node.runtime(**inputs)
                    if node.optype.name == "assign":
                        objs[node.inputs["y"].name] = objs[node.inputs["x"].name]
                except Exception as e:
                    print(f"Error in node {node}: {node.constants=}")
                    raise
            else:
                inputs = list(inputs.values())
                outputs, new_objs = run_graph(
                    node.subgraph, *inputs, return_objs=True, objs=objs
                )
                objs.update(new_objs)
        elif node.optype is not None:
            try:
                outputs = node.runtime(**inputs)
                if node.optype.name == "assign":
                    objs[node.inputs["y"].name] = objs[node.inputs["x"].name]
            except Exception as e:
                print(f"Error in node {node}: {node.constants=}")
                raise
        else:
            outputs = None
        if outputs is not None:
            if isinstance(outputs, dict):
                objs.update(outputs)
            else:
                store_outputs(node, outputs, objs)

    outputs = [objs[proto.name] for proto in graph.outputs]

    if dequant:
        assert "DEQUANT" in graph.subgraphs
        outputs = [objs[proto.name] for proto in graph.subgraphs["DEQUANT"].outputs]

    if len(outputs) == 0:
        outputs = None
    elif len(outputs) == 1:
        outputs = outputs[0]
    else:
        outputs = tuple(outputs)

    if return_dict:
        if not isinstance(outputs, tuple):
            outputs = (outputs,)
        outputs = {var.name: value for var, value in zip(graph.outputs, outputs)}

    if return_objs:
        ret = outputs, objs
    else:
        ret = outputs
    return ret


def run_sequential_graph(
    graph,
    *inputs,
    return_objs=False,
    arith_only=False,
    dequant=False,
    objs=None,
    return_dict=False,
):
    """Run a sequential graph"""
    # initialize state variables
    if objs is None:
        __, objs = run_graph(graph.subgraphs["INIT"], return_objs=True)

    if arith_only:
        step_graph = graph.subgraphs["ARITH"]
    else:
        step_graph = graph
    outputs = []

    if graph.unbind_dim is not None:
        inputs = [np.swapaxes(x, graph.unbind_dim, 0) for x in inputs]

    max_time_samples = inputs[0].shape[0]
    for i, input_tensor in enumerate(inputs):
        assert input_tensor.shape[0] == max_time_samples, (
            f"Input tensor at index {i} has a different time dimension: "
            f"{input_tensor.shape[0]} instead of {max_time_samples}."
        )

    for t in range(max_time_samples):
        # Gather the time slice from each input
        x_ts = tuple(inputs[i][t] for i in range(len(inputs)))

        y_t, objs = run_graph(
            step_graph,
            *x_ts,
            return_objs=True,
            objs=objs,
            skipped_subgraphs=["INIT"],
            dequant=dequant,
        )
        outputs.append(y_t)
    if isinstance(outputs[0], np.ndarray):
        outputs = [np.stack(outputs, axis=0)]
    else:
        out = []
        for i in range(len(outputs[0])):
            out.append(np.stack([o[i] for o in outputs], axis=0))
        outputs = out
    if graph.unbind_dim is not None:
        outputs = [np.swapaxes(o, graph.unbind_dim, 0) for o in outputs]
    if return_dict:
        outputs = {graph.outputs[0].name: outputs}
    if len(outputs) == 1:
        outputs = outputs[0]
    if return_objs:
        return outputs, objs
    else:
        return outputs
