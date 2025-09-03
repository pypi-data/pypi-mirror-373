from fmot import fqir
import numpy as np


def convert_input_to_dynamic_parameter(
    graph: fqir.GraphProto, input_name: str, value: np.ndarray
):
    """Arguments:
    graph (GraphProto): graph we want to modify
    input_name (str): name of the input that we want to convert
        to a default-valued tensor. This should be the name of the variable
        as it appears in "ARITH"
    value (ndarray): integer-valued numpy array holding the new default value.
        Must be the same shape as the tensor
    """

    main = graph
    arith = graph.subgraphs["ARITH"]
    quant = graph.subgraphs["QUANT"]

    name2input = {t.name: t for t in arith.inputs}

    variable = name2input[input_name]

    # check for compatibility (right shape, is integer)
    assert value.shape[0] == variable.shape[0]
    assert np.issubdtype(value.dtype, np.integer)

    # 1. add default value to the variable, move to list of parameters
    variable.value = value
    arith.inputs.remove(variable)
    arith.add_parameter(variable)

    # 2. remove from QUANT and ARITH subgraphs
    quant_source = None
    fp_source = None
    for node in quant.nodes:
        if variable in node.outputs:
            quant_source = node
            break
    if quant_source is not None:
        assert quant_source.opname == "quantize"
        assert len(quant_source.outputs) == 1

        quant.nodes.remove(quant_source)
        fp_source = quant_source.inputs["x"]

        if variable in quant.outputs:
            quant.outputs.remove(variable)
    if fp_source is not None:
        quant.inputs.remove(fp_source)
        main.inputs.remove(fp_source)
        for node in main.nodes:
            for k, v in list(node.inputs.items()):
                if v in [fp_source, variable]:
                    node.inputs.pop(k)

            for y in node.outputs:
                if y == variable:
                    node.outputs.remove(y)

    # 3. Construct a variable-setting graph
    new_graph_name = f"ARITH:SET:{input_name}"
    new_graph = fqir.GraphProto(name=new_graph_name)
    new_graph.add_input(variable)

    node = fqir.NodeProto(
        name=new_graph_name, optype=None, inputs={}, outputs=[], subgraph=new_graph
    )
    main.add_node(node)
    main.add_subgraph(new_graph_name, new_graph)
