from fmot import fqir
from ..passes.cleanup import uniquify_names
from typing import *


def set_signature(
    graph: fqir.GraphProto,
    input_names: List[str] = None,
    output_names: List[str] = None,
):
    if input_names is not None:
        assert len(input_names) == len(
            graph.inputs
        ), f"input_names: {input_names} graph inputs: {graph.inputs}"
        for tensor, name in zip(graph.inputs, input_names):
            tensor.name = name

    if output_names is not None:
        assert len(output_names) == len(graph.outputs)
        for tensor, name in zip(graph.outputs, output_names):
            tensor.name = name

    return uniquify_names(graph)
