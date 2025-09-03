from fmot import fqir
from collections import defaultdict
import numpy as np
from .helpers import replace_tensor_in_graph
from ordered_set import OrderedSet as set
import logging

logger = logging.getLogger("fqir cleanup passes")


def uniquify_names(graph: fqir.GraphProto):
    try:
        arith = graph.subgraphs["ARITH"]
    except:
        arith = graph

    name2tensors = defaultdict(set)

    def add_tensor(x: fqir.TensorProto):
        name2tensors[x.name].add(x)

    for node in arith.nodes:
        for x in node.inputs.values():
            add_tensor(x)
        for x in node.outputs:
            add_tensor(x)

    for name, tensors in name2tensors.items():
        if len(tensors) > 1:
            for i, t in enumerate(tensors):
                t.name = f"{name}.{i}"

    return graph


def correct_subgraph_outputs(graph: fqir.GraphProto):
    for node in graph.nodes:
        if node.subgraph is not None:
            outputs = node.subgraph.outputs
            node.outputs = outputs

            correct_subgraph_outputs(node.subgraph)


def _limit_biases(graph: fqir.GraphProto):
    """Restrict biases to the symmetric range [-2**(B-1)+1, 2**(B-1)-1]"""
    for node in graph.nodes:
        if node.opname == "addmm":
            bias = node.inputs["bias"]
            if bias.dtype == "fqint8":
                bw = 8
            else:
                bw = 16

            val = bias.value
            if val is not None:
                val = np.clip(val, -(2 ** (bw)) + 1, 2 ** (bw) - 1)
                bias.value = val


def limit_biases(graph: fqir.GraphProto):
    arith = graph.subgraphs["ARITH"]
    _limit_biases(arith)

    for node in arith.nodes:
        if node.subgraph is not None:
            _limit_biases(node.subgraph)


def remove_unused_params(graph: fqir.GraphProto):
    arith = graph.subgraphs["ARITH"]
    _remove_unused_params(arith)

    for node in arith.nodes:
        if node.subgraph is not None:
            _remove_unused_params(node.subgraph)


def _remove_unused_params(graph: fqir.GraphProto):
    """Strips graph of unused parameters"""
    unused_params = set(graph.parameters)

    for node in graph.nodes:
        for inp in node.inputs.values():
            if inp in unused_params:
                unused_params.remove(inp)

    logger.debug(f"Unused params to remove: {unused_params}")

    for param in unused_params:
        graph.parameters.remove(param)


def _remove_null_shifts(graph: fqir.GraphProto):
    """Strips graph of shift-by-zero"""

    def remove_one_null_shift(graph: fqir.GraphProto):
        for node in graph.nodes:
            if node.opname == "shift":
                x = node.inputs["x"]
                y = node.outputs[0]
                shamt = node.constants["shamt"]

                if x.dtype == y.dtype and shamt == 0 and y not in graph.outputs:
                    replace_tensor_in_graph(y, x, graph)
                    graph.nodes.remove(node)
                    return True
        return False

    while remove_one_null_shift(graph):
        pass

    for node in graph.nodes:
        if node.subgraph is not None:
            _remove_null_shifts(node.subgraph)


def remove_null_shifts(graph: fqir.GraphProto):
    arith = graph.subgraphs["ARITH"]

    _remove_null_shifts(arith)
