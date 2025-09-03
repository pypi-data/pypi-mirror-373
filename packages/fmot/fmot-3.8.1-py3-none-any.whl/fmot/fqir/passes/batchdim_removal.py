from . import helpers
import numpy as np
import copy
from collections import defaultdict

"""
Tagging helper functions
"""


def tag_dim(obj, dim):
    """
    Annotate a TensorProto with a ``_tagged_dim`` attribute, for use in
    batchdim propogation and batchdim removal

    Args:
        tensor (TensorProto): TensorProto to be tagged
        dim (int): Integer dimension annotation
    """
    if dim is not None:
        obj._tagged_dim = dim


def get_tagged_dim(obj):
    """
    Read a TensorProto for its ``_tagged_dim``, return None if there is no
    such annotation.

    Args:
        tensor (TensorProto)
    Returns:
        int: Integer dimension annotation
    """
    return getattr(obj, "_tagged_dim", None)


def remove_tagged_dim(tensor):
    """
    Remove the dimension corresponding to the ``_tagged_dim`` annotation. Clean
    up by deleting the ``_tagged_dim`` annotation.

    Args:
        tensor (TensorProto)
    """
    dim = get_tagged_dim(tensor)
    if dim is not None:
        shape: tuple = tensor.shape
        shape.pop(dim)
        tensor.shape = shape
    if hasattr(tensor, "_tagged_dim"):
        del tensor._tagged_dim


"""
Dimprop Rules

A dimprop rule is a function that operates on a node (in-place).

Each dimprop rule propogates a tagged dimension (i.e. a tagged batch-dim)
from node inputs to node outputs.
"""


def elementwise_dimprop(*constants_to_change):
    def f(node):
        """
        The standard dimprop rule.

        Propogates a tagged dimension from inputs to outputs, for broadcasted
        elementwise operations. Appropriate for:

        * vector-immediate ops (viadd, vimul)
        * vector-vector ops (vvadd, vvsub, vvmul)
        * nonlinearities (lut, relu, neg, quantize)
        * vector joining/splitting ops (chunk, cat)

        Args:
            node (NodeProto)
        """

        # Get ndim and tagged dim for all node inputs
        ndim = []
        tagged_dim = []
        for x in node.inputs.values():
            ndim.append(len(x.shape))
            tagged_dim.append(get_tagged_dim(x))
        ndim = np.array(ndim)
        tagged_dim = np.array(tagged_dim)

        # /!\ NotImplemented: >2 dimensions
        if len(ndim) > 0 and np.max(ndim) > 2:
            if node.opname == "temporal_conv2d":
                pass
            else:
                raise NotImplementedError(
                    f"""
                Cannot handle batch dim removal in the case of >2 dimensions in node:
                {node}
                {node.optype}
                {node.sourceref}
                inputs: {[x for x in node.inputs.values()]}
                """
                )

        # Only consider inputs with 2 dimensions
        tdims = tagged_dim[ndim == 2]
        if len(tdims) == 0:
            dim = None
        elif len(tdims) > 0:
            dim = tdims[0]
        if len(tdims) > 1:
            assert np.all(
                tdims[1:] == dim
            ), f"""
            Node did not have aligned batch dims:
            {node.optype}
            {node.sourceref}
            """

        # Tag outputs with dim removal
        for output in node.outputs:
            tag_dim(output, dim)

        # Change dim constants:
        if dim is not None:
            for cnst in constants_to_change:
                d = node.constants[cnst]
                if d < dim:
                    pass
                elif d == dim:
                    raise ValueError(
                        f"""
                    Cannot modify dim {dim} as it is invoked in constant {cnst}
                    in node:
                    {node}
                    {node.sourceref}
                    """
                    )
                elif d > dim:
                    d = d - 1
                node.constants[cnst] = d

    return f


def matmul_dimprop(mat1, mat2):
    """
    Construct a dimprop rule for a matmul operation.

    Args:
        mat1 (str): Name of the first matrix operand in the node's signature
        mat2 (str): Name of the second matrix operand in the node's signature

    Returns:
        function: dimprop function

    Case 1: First dim of mat1 is tagged
        (B, F1) x (F1, F2) -> (B, F2)

    Case 2: Second dim of mat2 is tagged
        (F2, F1) x (F1, B) -> (F2, B)

    .. warning::
        The returned dimprop function returns errors when called if:

        * An inner tensor dimension is tagged (i.e. dim 1 of mat1 or dim 0 of mat2)
        * Either matrix has >2 dimensions (NotImplementedError)
    """

    def f(node):
        x1 = node.inputs[mat1]
        x2 = node.inputs[mat2]

        # /!\ Don't yet handle >2 dimensions
        if any([len(x.shape) > 2 for x in [x1, x2]]):
            raise NotImplementedError(
                f"""
            Cannot handle matmul batchdim removal with >2 dimensions, see node:
            {node}
            {node.sourceref}
            """
            )
        dim = None
        if get_tagged_dim(x1) == 0:
            dim = 0
        elif get_tagged_dim(x2) == 1:
            dim = 1
        elif get_tagged_dim(x1) == 1:
            raise ValueError(
                f"""
            Cannot remove an inner dimension of a matmul.
             (*, B) x (*, *) :
            {node}
            {node.sourceref}
            """
            )
        elif get_tagged_dim(x2) == 0:
            raise ValueError(
                f"""
            Cannot remove an inner dimension of a matmul.
             (*, *) x (B, *) :
            {node}
            {node.sourceref}
            """
            )
        for output in node.outputs:
            tag_dim(output, dim)

    return f


def loop_dimprop(node):
    subgraph = node.subgraph
    n_recurse = node.constants["n_recurse"]

    for i, input in enumerate(node.inputs.values()):
        tag_dim(subgraph.inputs[i], get_tagged_dim(input))

    propogate_tagged_dim(subgraph)

    for i, output in enumerate(node.outputs):
        tag_dim(output, get_tagged_dim(subgraph.outputs[i + n_recurse]))


def transpose_dimprop(node):
    x = node.inputs["x"]

    # /!\ Don't yet handle >2 dimensions
    assert (
        len(x.shape) == 2
    ), f"""
    Cannot handle transpose batchdim removal for >2 dimensions, see node:
    {node.optype}
    {node.sourceref}
    """
    dim = get_tagged_dim(x)
    if dim is not None:
        dim = (dim + 1) % 2
    tag_dim(node.outputs[0], dim)


DIMPROP_RULES = defaultdict(elementwise_dimprop)
DIMPROP_RULES.update(
    {
        "matmul": matmul_dimprop("x", "y"),
        "addmm": matmul_dimprop("x", "y"),
        "transpose": transpose_dimprop,
        "chunk": elementwise_dimprop("dim"),
        "cat": elementwise_dimprop("dim"),
    }
)


def remove_batchdim(graph, dim=0):
    """
    Remove the batch dimension from an FQIR graph.
    The batch dimension is propogated through the graph, starting with the
    inputs.

    Args:
        graph (GraphProto)
        dim (int): Dimension to treat as the batch dimension
    """

    try:
        new_graph = copy.deepcopy(graph)
        graph = new_graph
    except:
        pass

    # Tag the batchdim in the inputs
    for x in graph.inputs:
        assert (
            len(x.shape) > dim
        ), f"Cannot remove dim {dim} from a vector with shape {x.shape}"
        tag_dim(x, dim)

    if "INIT" in graph.subgraphs:
        for x in helpers.get_all_tensors(graph.subgraphs["INIT"]):
            tag_dim(x, dim)

    # Propogate the tagged dim through the graph
    propogate_tagged_dim(graph)

    # Remove tagged dims
    for x in helpers.get_all_tensors(graph):
        remove_tagged_dim(x)

    # Reshape zeros:
    if "INIT" in graph.subgraphs:
        for node in graph.subgraphs["INIT"].nodes:
            shape = list(node.constants["shape"])
            shape.pop(dim)
            node.constants["shape"] = tuple(shape)

    return graph


def propogate_tagged_dim(graph):
    for node in graph.nodes:
        if node.opname == "loop":
            loop_dimprop(node)
        elif node.subgraph is not None:
            propogate_tagged_dim(node.subgraph)
        else:
            DIMPROP_RULES[node.optype.name](node)
