from fmot.fqir import TensorProto, GraphProto, NodeProto, registry_v1
import numpy as np
from collections import defaultdict
from typing import *


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


def fold_reused_params(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    _fold_reused_params(arith)

    for node in arith.nodes:
        if node.subgraph is not None:
            _fold_reused_params(node.subgraph)


def _fold_reused_params(graph: GraphProto):
    # fill a dict mapping reused params to their first occurance
    reuse2parent: Dict[TensorProto, TensorProto] = {}
    unique_tensors: List[TensorProto] = []
    for p in graph.parameters:
        v = p.value

        found_match = False
        for ut in unique_tensors:
            if np.array_equal(ut.value, v):
                found_match = True
                reuse2parent[p] = ut
                break

        if not found_match:
            unique_tensors.append(p)

    # replace all uses of reused params with their parent, remove from param list
    for orig, replacement in reuse2parent.items():
        replace_tensor_in_graph(orig, replacement, graph)
        graph.parameters.remove(orig)
