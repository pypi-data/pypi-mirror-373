from .. import GraphProto, NodeProto, TensorProto


def get_all_tensors(graph):
    """
    Returns a set of all TensorProtos in a GraphProto

    Args:
        graph (GraphProto)
    Returns:
        Set[TensorProto]: A set of all tensors in the graph
    """
    tprotos = set(graph.inputs)
    tprotos.update(set(graph.parameters))
    for node in graph.nodes:
        tprotos.update(set(node.outputs))
        if node.subgraph is not None:
            tprotos.update(get_all_tensors(node.subgraph))
    return tprotos


def isroot(tensor):
    return len(tensor.parents) == 0


def isleaf(tensor):
    return len(tensor.children) == 0


def get_root_parents(tensor):
    roots = set()
    for parent in tensor.parents:
        if isroot(parent):
            roots.add(parent)
        else:
            roots.update(get_root_parents(parent))
    return roots


def isinput(tensor, graph):
    return tensor in graph.inputs


def isoutput(tensor, graph):
    return tensor in graph.outputs


def isparam(tensor, graph, recurse=True):
    ip = tensor in graph.parameters
    if recurse:
        for subgraph in graph.subgraphs.values():
            ip = ip or isparam(tensor, subgraph, recurse=True)
    return ip


def replace_tensor_in_graph(
    orig: TensorProto, replacement: TensorProto, graph: GraphProto
):
    """Replace all occurances of 'orig' with 'replacement'"""
    # iterate through nodes
    for node in graph.nodes:
        # replace if found as an input
        for k, v in node.inputs.items():
            if v == orig:
                node.inputs[k] = replacement

        # replace if found as an output
        for i, y in enumerate(node.outputs):
            if y == orig:
                node.outputs[i] = replacement

    # iterate through graph-level inputs and outputs
    for i, x in enumerate(graph.inputs):
        if x == orig:
            graph.inputs[i] = replacement

    for i, y in enumerate(graph.outputs):
        if y == orig:
            graph.outputs[i] = replacement


def create_replica_tensor(tensor: TensorProto, tag: str = "", shape=None):
    if shape is None:
        shape = tensor.shape

    new_tensor = TensorProto(
        name=tensor.name + tag,
        dtype=tensor.dtype,
        shape=shape,
        avg_sparsity=tensor.avg_sparsity,
        value=tensor.value,
        quanta=tensor.quanta,
        density_per_element=tensor.density_per_element,
        named_dims=tensor.named_dims,
    )
    return new_tensor


def create_replica_node(
    node: NodeProto, tag: str = "", inputs: dict = None, outputs: list = None
):
    if inputs is None:
        inputs = node.inputs
    if outputs is None:
        outputs = node.outputs
    new_node = NodeProto(
        name=node.name + tag,
        optype=node.optype,
        inputs=inputs,
        outputs=outputs,
        constants=node.constants,
        subgraph=node.subgraph,
        sourceref=node.sourceref,
    )
    return new_node
