"""
A tool used to insert FixedRangeObservers into a model with saturating 
nonlinearities. Saturating nonlinearities such as sigmoid and tanh are insensitive 
to inputs with magnitudes greater than 8 and 4, respectively. 
"""
import fmot
import torch
import networkx as nx
from collections import defaultdict
import functools

__all__ = ["insert_fixed_range_observers"]

# All atomic modules that we want to trace into nx.DiGraph
ATOMICS = [
    fmot.qat.nn.VVAdd,
    fmot.qat.nn.VIAdd,
    fmot.qat.nn.VVSub,
    fmot.qat.nn.Neg,
    fmot.qat.nn.VVMul,
    fmot.qat.nn.VIMul,
    fmot.qat.nn.Matmul,
    fmot.qat.nn.AddMM,
    fmot.qat.nn.ReLU,
    fmot.qat.nn.Transpose,
    fmot.qat.nn.FTranspose,
    fmot.qat.nn.Reshape,
    fmot.qat.nn.Chunk,
    fmot.qat.nn.BareCat,
    fmot.qat.nn.Stack,
    fmot.qat.nn.Sum,
    fmot.qat.nn.OnesLike,
    fmot.qat.nn.Shift,
    fmot.qat.nn.Requantize,
    fmot.qat.nn.Gt0,
    fmot.qat.nn.Linear,
    fmot.qat.nn.AffineLinear,
    fmot.qat.nn.PerChannelAffineLinear,
    fmot.qat.nn.ILUT,
    fmot.qat.nn.RSqrtPlusEps,
    fmot.qat.nn.PowFrac,
    fmot.qat.nn.BareLUT,
    fmot.qat.nn.Requantize,
]

# All atomic modules that pass a fixed domain to their predecessors.
# No multiply or LUT atomics.
FR_ATOMICS = [
    fmot.qat.nn.VVAdd,
    fmot.qat.nn.VIAdd,
    fmot.qat.nn.VVSub,
    fmot.qat.nn.Neg,
    fmot.qat.nn.ReLU,
    fmot.qat.nn.Transpose,
    fmot.qat.nn.FTranspose,
    fmot.qat.nn.Reshape,
    fmot.qat.nn.Chunk,
    fmot.qat.nn.BareCat,
    fmot.qat.nn.Stack,
    fmot.qat.nn.Shift,
    fmot.qat.nn.Requantize,
    fmot.qat.nn.Gt0,
]


def hook_layer(module, graph):
    """
    A hook function that adds a node and edges to a
    networkx digraph during tracing. Modifies graph in-place.

    Args:
        module (torch.nn.Module): layer to add to graph during tracing
        graph (nx.DiGraph): directed acyclic graph

    Returns:
        - RemoveableHandle
    """

    module._called = False

    def hook_fn(module, inputs, outputs):
        if module._called:
            return outputs
        else:
            module._called = True

        graph.add_node(module)
        if isinstance(inputs, torch.Tensor):
            inputs = (inputs,)
        for i in inputs:
            if hasattr(i, "node"):
                graph.add_edge(i.node, module)
        if isinstance(outputs, torch.Tensor):
            outputs.node = module
            return outputs
        else:
            for o in outputs:
                o.node = module
            return outputs

    return module.register_forward_hook(hook_fn)


def _attach_handles(module: torch.nn.Module, G, handles):
    if type(module) in ATOMICS:
        handles.append(hook_layer(module, G))
    else:
        for submodule in module.children():
            _attach_handles(submodule, G, handles)


def trace_graph(model, x):
    """
    Trace an nx.DiGraph with input x. Graph is not guaranteed to be perfect
    (i.e. not good enough to use as a program), but will be good enough
    to recursively backtrack to apply fixed-range observers to the model.

    Args:
        model (torch.nn.Module): Converted pytorch model
        x (torch.Tensor, tuple(torch.Tensor)): tracing input(s) to the model

    Returns:
        - Graph (nx.DiGraph). Nodes are atomic modules, and directed edges denote
            data dependencies
    """
    G = nx.DiGraph()
    handles = []
    _attach_handles(model, G, handles)
    if isinstance(x, tuple):
        __ = model(*x)
    elif isinstance(x, list):
        raise ValueError("Could not trace graph")
    elif isinstance(x, torch.Tensor):
        __ = model(x)
    for h in handles:
        h.remove()
    return G


def find_lin_requant(graph):
    n = 0
    for node in graph:
        if isinstance(node, (fmot.qat.nn.Matmul, fmot.qat.nn.AddMM)):
            succs = list(graph.successors(node))
            if len(succs) == 1 and isinstance(
                succs[0], (fmot.qat.nn.Requantize, fmot.qat.nn.ILUT)
            ):
                nxt = succs[0]
                if isinstance(nxt, fmot.qat.nn.ILUT):
                    requant = nxt.shift_down
                else:
                    requant = nxt
                obs = requant.quantizer.observer
                if isinstance(obs, fmot.qat.nn.FixedRangeObserver):
                    old_obs = node.quantizer.observer
                    node.quantizer.observer = fmot.qat.nn.FixedRangeWrappedObserver(
                        limits=obs.limits, wrapped=old_obs
                    )
                    n += 1
        elif isinstance(node, fmot.qat.nn.AffineLinear):
            succs = list(graph.successors(node))
            if len(succs) == 1 and isinstance(
                succs[0], (fmot.qat.nn.Requantize, fmot.qat.nn.ILUT)
            ):
                nxt = succs[0]
                if isinstance(nxt, fmot.qat.nn.ILUT):
                    requant = nxt.shift_down
                else:
                    requant = nxt
                obs = requant.quantizer.observer
                if isinstance(obs, fmot.qat.nn.FixedRangeObserver):
                    limits = obs.limits
                    wide_limits = tuple(
                        map(lambda x: 2 * x if x is not None else None, limits)
                    )
                    old_obs = node.multiplier.quantizer.observer
                    # node.multiplier.quantizer.observer = fmot.qat.nn.FixedRangeWrappedObserver(limits=wide_limits, wrapped=old_obs)
                    n += 1

                    old_obs = node.vimul.quantizer.observer
                    node.vimul.quantizer.observer = (
                        fmot.qat.nn.FixedRangeWrappedObserver(
                            limits=limits, wrapped=old_obs
                        )
                    )
                    n += 1
        elif isinstance(node, fmot.qat.nn.PerChannelAffineLinear):
            succs = list(graph.successors(node))
            if len(succs) == 1 and isinstance(
                succs[0], (fmot.qat.nn.Requantize, fmot.qat.nn.ILUT)
            ):
                nxt = succs[0]
                if isinstance(nxt, fmot.qat.nn.ILUT):
                    requant = nxt.shift_down
                else:
                    requant = nxt
                obs = requant.quantizer.observer
                if isinstance(obs, fmot.qat.nn.FixedRangeObserver):
                    limits = obs.limits
                    wide_limits = tuple(
                        map(lambda x: 2 * x if x is not None else None, limits)
                    )
                    old_obs = node.multiplier.quantizer.observer
                    # node.multiplier.quantizer.observer = fmot.qat.nn.FixedRangeWrappedObserver(limits=wide_limits, wrapped=old_obs)
                    n += 1

                    old_obs = node.renorm.quantizer.observer
                    node.renorm.quantizer.observer = (
                        fmot.qat.nn.FixedRangeWrappedObserver(
                            limits=limits, wrapped=old_obs
                        )
                    )
                    n += 1
        elif isinstance(node, fmot.qat.nn.Linear):
            succs = list(graph.successors(node))
            if len(succs) == 1 and isinstance(
                succs[0], (fmot.qat.nn.Requantize, fmot.qat.nn.ILUT)
            ):
                nxt = succs[0]
                if isinstance(nxt, fmot.qat.nn.ILUT):
                    requant = nxt.shift_down
                else:
                    requant = nxt
                obs = requant.quantizer.observer
                if isinstance(obs, fmot.qat.nn.FixedRangeObserver):
                    old_obs = node.multiplier.quantizer.observer
                    node.multiplier.quantizer.observer = (
                        fmot.qat.nn.FixedRangeWrappedObserver(
                            limits=obs.limits, wrapped=old_obs
                        )
                    )
                    n += 1
    return n


def insert_fixed_range_observers(model, x):
    """
    Recurse backwards from each saturating nonlinearity to apply fixed-range
    observers to predecessor layers. This restricts dynamic range prior to
    saturating nonlinearities like sigmoid and tanh, to make the most of
    dynamic range once the model is quantized.

    Args:
        model (torch.nn.Module): Converted pytorch model
        x (torch.Tensor or tuple(torch.Tensor)): Input(s) to the model, for tracing
            purposes
        scaling (float): Optional scaling factor for dynamic ranges. Should be
            >= 1. Default is 1.
        in_place (bool): Whether to modify the model in-place or to modify a replica.
            Default is False.
        verbose (bool): Print out details about the insertion of
            :attr:`FixedRangeWrappedObserver` layers.
        use_vvmul (bool): If True, passes fixed range through VVMUL if one of the
            operands is the output of a sigmoid or tanh nonlinearity. Default True.
    """
    graph = trace_graph(model, x)
    return find_lin_requant(graph) > 0
