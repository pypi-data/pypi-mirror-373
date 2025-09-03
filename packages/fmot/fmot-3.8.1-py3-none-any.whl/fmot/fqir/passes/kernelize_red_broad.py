from fmot.fqir import TensorProto, GraphProto, NodeProto, registry_v1
import numpy as np
from collections import defaultdict
import logging
from typing import *

logger = logging.getLogger(__name__)


def _kernelize_sum(graph: GraphProto):
    # group sum nodes by input length (that way we can
    #   emit the minimum number of matrix params)
    dbl_sum_nodes = defaultdict(list)
    std_sum_nodes = defaultdict(list)

    for node in graph.nodes:
        if node.opname == "sum":
            ilen = node.inputs["x"].shape[0]
            if node.inputs["x"].dtype == "fqint8":
                std_sum_nodes[ilen].append(node)
            elif node.inputs["x"].dtype == "fqint16":
                dbl_sum_nodes[ilen].append(node)

    for length, sums in std_sum_nodes.items():
        _kern_sum_group(graph, length, sums, dtype="fqint4")
    for length, sums in dbl_sum_nodes.items():
        _kern_sum_group(graph, length, sums, dtype="fqint8")

    for node in graph.nodes:
        if node.subgraph is not None:
            _kernelize_sum(node.subgraph)


def kernelize_sum(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    _kernelize_sum(arith)


def replace_node(graph: GraphProto, orig: NodeProto, new: NodeProto):
    replaced = False
    for i, node in enumerate(graph.nodes):
        if node == orig:
            graph.nodes[i] = new
            replaced = True
            break
    if not replaced:
        raise RuntimeError(f"Failed to locate and replace node in graph:\n{orig}")


def _kern_sum_group(arith: GraphProto, length: int, sums: List[NodeProto], dtype: str):
    weight = TensorProto(
        f"%w_sum_{length}_{dtype}",
        dtype=dtype,
        shape=(length, 1),
        value=np.ones((length, 1), dtype=int),
    )
    arith.add_parameter(weight)
    for sum_node in sums:
        x = sum_node.inputs["x"]
        y = sum_node.outputs[0]
        mm_node = NodeProto(
            sum_node.name,
            optype=registry_v1["matmul"],
            inputs={"x": x, "y": weight},
            outputs=[y],
            constants={
                "rounded": False,
                "shamt_bwred": sum_node.constants["shamt_bwred"],
                "bw_out": sum_node.constants["bw"],
            },
        )
        replace_node(arith, sum_node, mm_node)


def _kernelize_broadcast(graph: GraphProto):
    def has_broadcast(node: NodeProto):
        if not node.optype.can_bcast_in:
            return False
        vec_lens = set()
        for inp in node.inputs.values():
            if len(inp.shape) == 1:
                vec_lens.add(inp.shape[0])
        if len(vec_lens) > 1:
            return 1 in vec_lens
        else:
            return False

    bcast_vars: Dict[TensorProto, List[Tuple[NodeProto, str]]] = defaultdict(list)

    # arith = graph.subgraphs["ARITH"]
    for node in graph.nodes:
        if has_broadcast(node):
            for key, tensor in node.inputs.items():
                if len(tensor.shape) == 1 and tensor.shape[0] == 1:
                    bcast_vars[tensor].append((node, key))

    # cache and reuse broad cast matrices if multiple broadcasts go to the same shape
    std_bmatrices = {}
    dbl_bmatrices = {}

    for tensor, successors in bcast_vars.items():
        _kern_broadcast(graph, tensor, successors, std_bmatrices, dbl_bmatrices)


def kernelize_broadcast(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    _kernelize_broadcast(arith)

    for node in arith.nodes:
        if node.subgraph is not None:
            _kernelize_broadcast(node.subgraph)


def insert_node_after_creation(
    graph: GraphProto, tensor: TensorProto, node_to_add: NodeProto
):
    """inserts node in the graph after the given tensor is output from a node"""

    if tensor in graph.inputs:
        graph.nodes.insert(0, node_to_add)
    else:
        loc = 0
        for i, node in enumerate(graph.nodes):
            if tensor in node.outputs:
                loc = i
                break
        graph.nodes.insert(loc + 1, node_to_add)


def _kern_broadcast(
    arith: GraphProto,
    tensor: TensorProto,
    successors: List[Tuple[NodeProto, str]],
    std_bmatrices: Dict[int, TensorProto],
    dbl_bmatrices: Dict[int, TensorProto],
):
    logger.debug(f"\nKernelizing broadcast on tensor {tensor}...\n{successors=}")

    if tensor.dtype == "fqint8":
        bmatrices = std_bmatrices
        bm_dtype = "fqint4"
        bw = 8
    elif tensor.dtype == "fqint16":
        bmatrices = dbl_bmatrices
        bm_dtype = "fqint8"
        bw = 16
    else:
        raise ValueError(f"Encountered unexpected datatype {tensor.dtype}")

    # break up successors into a different list for each broadcasted length
    succ_by_len: Dict[int, List[Tuple[NodeProto, str]]] = defaultdict(list)
    for node, port in successors:
        length = node.outputs[0].shape[0]
        succ_by_len[length].append((node, port))

    # for each broadcasted length, insert a broadcast node
    # and replace succesor input with new broadcasted variable
    for length, l_succs in succ_by_len.items():
        btensor = TensorProto(
            f"{tensor.name}_bcast_{length}",
            tensor.dtype,
            shape=[length],
            avg_sparsity=tensor.avg_sparsity,
            quanta=tensor.quanta,
            named_dims=tensor.named_dims,
        )

        # add as a new param if `tensor` is a parameter
        if tensor in arith.parameters:
            btensor.value = np.ones(length, dtype=int) * tensor.value[0]
            arith.add_parameter(btensor)

        else:
            # re-use broadcast matrix of the given length if it already exists
            if length in bmatrices:
                bmatrix = bmatrices[length]
            else:
                bmatrix = TensorProto(
                    f"%broadcast_{length}",
                    dtype=bm_dtype,
                    shape=[1, length],
                    value=np.ones((1, length), dtype=int),
                )
                bmatrices[length] = bmatrix
                arith.add_parameter(bmatrix)

            broad_node = NodeProto(
                f"{tensor.name}_broadcast_{length}",
                registry_v1["matmul"],
                inputs={"x": tensor, "y": bmatrix},
                outputs=[btensor],
                constants={"rounded": False, "shamt_bwred": 0, "bw_out": bw},
            )
            insert_node_after_creation(arith, tensor, broad_node)
            logger.debug(f"broadcast node: {broad_node}")

        # replace inputs with broadcasted inputs
        for node, key in l_succs:
            node.inputs[key] = btensor
