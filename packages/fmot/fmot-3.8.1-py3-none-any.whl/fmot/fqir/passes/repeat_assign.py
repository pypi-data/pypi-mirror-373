"""Multiple assign nodes to the same variable are removed, except for the last one.
Interim references are replaced with new variables"""

from ... import fqir
from .helpers import create_replica_tensor, create_replica_node
from collections import defaultdict
from typing import *


def dereference_repeated_assigns(graph: fqir.GraphProto):
    arith = graph.subgraphs["ARITH"]

    tensor_to_assign = defaultdict(list)

    for node in arith.nodes:
        if node.opname == "assign":
            y = node.inputs["y"]
            tensor_to_assign[y].append(node)

    for tensor, assigns in tensor_to_assign.items():
        if len(assigns) > 1:
            deref_assigns(arith, tensor, assigns)


def deref_assigns(
    arith: fqir.GraphProto, tensor: fqir.TensorProto, assigns: List[fqir.NodeProto]
):
    curr_buff = None

    for node in arith.nodes:
        if node in assigns[:-1]:
            arith.nodes.remove(node)
            curr_buff = node.inputs["x"]

        elif (
            tensor in node.inputs.values()
            and curr_buff is not None
            and node.opname != "assign"
        ):
            for k, v in node.inputs.items():
                if v == tensor:
                    node.inputs[k] = curr_buff
