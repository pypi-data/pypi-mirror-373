from fmot.fqir import GraphProto, NodeProto, TensorProto, registry_v1
from typing import Union, Optional


def replace_tensor_references(
    graph: GraphProto,
    old: TensorProto,
    new: TensorProto,
    after: Optional[NodeProto] = None,
):
    """Swaps out references to TensorProto `old` with TensorProto `new`

    Only applies to nodes that used to take `old` in as an input -- does not
    modify the creation op for `old`.
    """
    seen_after = after is None

    for node in graph.nodes:
        if seen_after:
            for key, x in node.inputs.items():
                if x == old:
                    node.inputs[key] = new
            # for i, x in enumerate(node.outputs):
            #     if x == old:
            #         node.outputs[i] = new
        elif node == after:
            seen_after = True

    return graph


def get_creation_node(graph: GraphProto, tensor: TensorProto):
    """Each Tensor in the graph can only have one creation node.
    If more than one is found, raises an Error.

    If no creation node is found, returns None.
    """
    creation_nodes = []

    for node in graph.nodes:
        if tensor in node.outputs:
            creation_nodes.append(node)

    if len(creation_nodes) == 0:
        return None
    elif len(creation_nodes) == 1:
        return creation_nodes[0]
    else:
        raise ValueError(
            f"tensor {tensor} has multiple creation nodes in the graph; illegal. Nodes:\n{creation_nodes}"
        )


def get_last_creation_node(graph: GraphProto, tensors: list[TensorProto]):
    """Returns the creation node that appears latest in the graph for any of the given tensors.

    Returns None if no creation ops were found."""

    creation_nodes = set([get_creation_node(graph, t) for t in tensors])
    if None in creation_nodes:
        creation_nodes.remove(None)

    last_node = None
    for node in graph.nodes:
        if node in creation_nodes:
            last_node = node

    return last_node


def find_references_to_tensors_between(
    graph: GraphProto,
    start: Optional[NodeProto],
    end: Optional[NodeProto],
    tensors: set[TensorProto],
) -> set[TensorProto]:
    """
    Find tensors referenced between two nodes in a graph.

    Args:
        graph (GraphProto): The FQIR graph.
        start (NodeProto, optional): Start node (exclusive). If None, search starts from the first node.
        end (NodeProto, optional): End node (inclusive). If None, search goes to the last node.
        tensors (set[TensorProto]): Set of tensors to search for.

    Returns:
        set[TensorProto]: Tensors from `tensors` that are referenced between `start` (exclusive) and `end` (inclusive).
    """
    nodes = graph.nodes
    idx_start = nodes.index(start) + 1 if start else 0
    idx_end = nodes.index(end) + 1 if end else len(nodes)

    span = nodes[idx_start:idx_end]

    referenced = {
        t
        for node in span
        for t in (set(node.inputs.values()).union(set(node.outputs)))
        if t in tensors
    }
    return referenced


def get_assign_for(graph: GraphProto, tensor: TensorProto) -> NodeProto:
    """
    Locates the assign, temporal_unfold1d, or temporal_unfold2d node that updates the given tensor or convolutional buffer.

    If no assign node is found, raises a RuntimeError
    """
    for node in graph.nodes:
        if node.opname == "assign":
            y = node.inputs["y"]
            if y == tensor:
                return node
        elif node.opname == "temporal_conv2d" and "buffer" in node.inputs:
            buff = node.inputs["buffer"]
            if buff == tensor:
                return node
        elif node.opname == "temporal_unfold" and "buffer" in node.inputs:
            buff = node.inputs["buffer"]
            if buff == tensor:
                return node

    raise RuntimeError(
        f"Could not find an assign/temporal_unfold/temporal_conv2d node that updates {tensor}"
    )


def get_latest_node_among(graph: GraphProto, nodes: list[NodeProto]):
    rem_nodes = set(nodes)
    for node in graph.nodes:
        if node in rem_nodes:
            rem_nodes.remove(node)
            if len(rem_nodes) == 0:
                return node

    if len(rem_nodes) != 0:
        raise RuntimeError(
            f"Could not find all nodes in {nodes} in the given graph. Remaining: {rem_nodes}"
        )


def predecessors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_pred in graph.nodes:
            if node in maybe_pred.outputs:
                yield maybe_pred

    elif isinstance(node, NodeProto):
        for x in node.inputs.values():
            yield x


def successors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_succ in graph.nodes:
            if node in maybe_succ.inputs.values():
                yield maybe_succ

    elif isinstance(node, NodeProto):
        for x in node.outputs:
            yield x


def get_all_tensors(graph: GraphProto) -> set[TensorProto]:
    tensors = set()
    for p in graph.parameters:
        tensors.add(p)
    for x in graph.inputs:
        tensors.add(x)
    for node in graph.nodes:
        for x in node.inputs.values():
            tensors.add(x)
        for y in node.outputs:
            tensors.add(y)
    for y in graph.outputs:
        tensors.add(y)

    return tensors


def find_tensor_with_name(graph: GraphProto, name: str):
    all_tensors = get_all_tensors(graph)

    found = None
    for t in all_tensors:
        if t.name == name:
            if found is None:
                found = t
            else:
                raise RuntimeError(
                    f"multiple tensors with the name {name} were found in the graph"
                )

    if found is None:
        raise RuntimeError(f"Could not locate tensor {name} in graph")

    return found


def get_insertion_idx(graph, after: Union[TensorProto, NodeProto]):
    """
    Find the insertion index in a graph immediately after a given tensor or node.

    If `after` is a TensorProto:
        - If it is an input or parameter tensor, returns index 0 (before any computation nodes).
        - Otherwise, finds the node that produces this tensor and inserts after it.

    If `after` is a NodeProto:
        - Inserts directly after this node.

    Args:
        graph (GraphProto): The graph in which to find the insertion index.
        after (Union[TensorProto, NodeProto]): Tensor or node to insert after.

    Returns:
        int: Index in `graph.nodes` after which the new node should be inserted.

    Raises:
        ValueError: If the tensor's producing node cannot be located in the graph.
    """
    if isinstance(after, TensorProto):
        if after in graph.inputs:
            return 0
        elif after in graph.parameters:
            return 0
        else:  # hunt for the creation op
            new_after = None
            for x in graph.nodes:
                if after in x.outputs:
                    new_after = x
                    break
            if new_after is None:
                return 0
                # raise ValueError(
                #     f"Could not locate the producing node for tensor {after}. in graph {graph}"
                # )
            after = new_after

    idx = graph.nodes.index(after)
    return idx


def insert_node_after(
    graph: GraphProto, node: NodeProto, after: Union[TensorProto, NodeProto, list]
):
    """
    Insert a node into a graph immediately after a specified tensor, node, or list of nodes/tensors.

    If multiple `after` targets are provided (as a list), the node is inserted after the latest one
    (i.e., the maximum insertion index among them).

    Args:
        graph (GraphProto): The graph to modify.
        node (NodeProto): The node to insert.
        after (Union[TensorProto, NodeProto, list]): A tensor, node, or list of tensors/nodes indicating
            where to insert after.

    Returns:
        GraphProto: The modified graph with the node inserted.

    Raises:
        ValueError: If any tensor's producing node cannot be located in the graph.
    """
    if isinstance(after, (NodeProto, TensorProto)):
        idx = get_insertion_idx(graph, after)
    else:
        idx = max([get_insertion_idx(graph, x) for x in after])
    graph.nodes.insert(idx + 1, node)
    return graph


def merge_graphs(
    src_graph: GraphProto,
    dst_graph: GraphProto,
    after: Optional[set[NodeProto]] = None,
    location="end",
):
    """
    Insert nodes from src_graph into dst_graph, either at the end, or following a set of nodes.

    Arguments:
        src_graph (GraphProto): graph that will be the source of new nodes
        dst_graph (GraphProto): graph that src_graph will be insert into
        after (set[NodeProto], optional): an optional set of nodes to insert src_graph after. If not provided, will
            insert src_graph at position determined by "location".
        location (str, optional): "beginning" or "end". Default "end"
    """

    if after is None:
        if location == "end":
            dst_graph.nodes = dst_graph.nodes + src_graph.nodes
        elif location == "beginning":
            dst_graph.nodes = src_graph.nodes + dst_graph.nodes
        else:
            raise ValueError(f"location {location} was not 'beginning' or 'end'")
    else:
        pre = []
        for node in dst_graph.nodes:
            if node in after:
                after.remove(node)
            pre.append(node)
            if len(after) == 0:
                break

        post = dst_graph.nodes[len(pre) :]

        dst_graph.nodes = pre + src_graph.nodes + post

    for p in src_graph.parameters:
        dst_graph.add_parameter(p)

    dst_graph.inputs = src_graph.inputs + dst_graph.inputs
    dst_graph.outputs = src_graph.outputs + dst_graph.outputs

    return src_graph


def tensor_like(src: TensorProto, name: str, quanta=None, value=None):
    new = TensorProto(
        name=name,
        dtype=src.dtype,
        shape=src.shape,
        value=value,
        quanta=src.value if quanta is None else quanta,
    )
    return new


def concat_inputs(graph: GraphProto):
    inputs = graph.inputs
    for x in inputs:
        assert x.dtype == "fqint16"

    x_cat = TensorProto(
        name="inputs_concat",
        dtype="fqint16",
        shape=[sum([x.shape[0] for x in inputs])],
        quanta=None,
    )
    split = NodeProto(
        name="split_in",
        optype=registry_v1["split"],
        inputs={"x": x_cat},
        outputs=inputs,
        constants={"lengths": [x.shape[0] for x in inputs], "dim": 0},
    )
    graph.inputs = [x_cat]
    graph.nodes.insert(0, split)
