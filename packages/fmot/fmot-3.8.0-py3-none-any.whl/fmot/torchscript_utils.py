"""
Utilities for parsing torchscipt IR graphs
"""


def parse_attributes(node):
    # This assumes that the name and attribute are in the
    # last [..] pattern occurence: might break?
    segment = str(node).split("[")[-1].split("]")[0]
    items = segment.split("=")
    attributes = {}
    for k, v in zip(items[::2], items[1::2]):
        v = v.strip('"')
        attributes[k] = v
    return attributes


def get_attr_name(node):
    return parse_attributes(node)["name"]


def get_type(x):
    return x.type().str()


def get_input_names(node):
    return [x.debugName() for x in node.inputs()]


def get_tensorial_input_names(node):
    return [x.debugName() for x in node.inputs() if istensor(x) or istensorlist(x)]


def get_output_names(node):
    return [x.debugName() for x in node.outputs()]


def get_inputs_outputs_sourceref(node, tensorial_inputs=False):
    if tensorial_inputs:
        inputs = get_tensorial_input_names(node)
    else:
        inputs = get_input_names(node)
    outputs = get_output_names(node)
    sourceref = node.sourceRange()
    return inputs, outputs, sourceref


def istensor(x):
    return get_type(x) == "Tensor"


def istensorlist(x):
    return get_type(x) == "Tensor[]"


def isnestedtensorlist(x):
    """
    Check if the type string of x indicates it is a nested list of tensors, regardless of depth.
        If it is a Nested-List, the identifier will be like: 'Tensor[][][][]' or 'Tensor[][]' .. etc.
        Essentially "Tensor" followed by infinite "[]"

    Args:
        x: The node whose output type we want to check.

    Returns:
        bool: True if x is a nested list of tensors, False otherwise.
    """
    # Get the type string of the output of x
    type_str = get_type(x)

    # Check if the type string starts with 'Tensor'
    if not type_str.startswith("Tensor"):
        return False

    # Extract the brackets part of the type string
    brackets = type_str[len("Tensor") :]

    # Use a stack to check if brackets are properly nested
    stack = []
    for char in brackets:
        if char == "[":
            stack.append(char)
        elif char == "]":
            if not stack:
                return False
            stack.pop()
        else:
            return False

    return len(stack) == 0


def ismodule(x):
    return get_type(x).startswith("__torch__")


_CASTERS = {"int": int, "float": float, "bool": lambda x: bool(int(x)), "str": str}


def get_value(x, module=None):
    typ_str = get_type(x)
    if typ_str in _CASTERS:
        attrs = parse_attributes(x.node())
        if x.node().kind() == "prim::GetAttr":
            return get_attribute_value(x, module)
        else:
            value = attrs["value"]
            v = _CASTERS[typ_str](value)
            return v
    else:
        return None


def get_attribute_value(x, module):
    if module is None:
        raise RuntimeError(f"get_attribute_value expects a non-None module, {x=}")
    attrs = parse_attributes(x.node())
    value = getattr(module, attrs["name"])
    return value


def get_list(x, module=None):
    node = x.node()
    if node.kind() == "prim::ListConstruct":
        return [get_value(xx, module=module) for xx in node.inputs()]
    elif node.kind() == "prim::GetAttr":
        return get_attribute_value(x, module)
    else:
        raise ValueError(f"{node.kind()=} not recognized for get_list")


def isaten(node):
    return node.kind().startswith("aten::")


def isblock(node):
    return len(list(node.blocks())) > 0


def hasaten(graph):
    if graph is None:
        return False
    return any([isaten(node) for node in graph.nodes()])


def hassubblocks(graph):
    return any([isblock(node) for node in graph.nodes()])


def isgetparam(node):
    return node.kind() == "prim::GetAttr" and istensor(node.output())


def isgetattr(node):
    return node.kind() == "prim::GetAttr" and not istensor(node.output())


def isgetattrmodule(node):
    return isgetattr(node) and ismodule(node.output())


def iscallmethod(node):
    return node.kind() == "prim::CallMethod"


def getcallmethod(node):
    if not iscallmethod(node):
        raise ValueError(
            f"node was expected to be prim::CallMethod, was {node.kind()} instead"
        )

    attrs = parse_attributes(node)
    return attrs["name"]


def calls_allowed_methods(node, allowed_methods: list):
    """checks if a prim::CallMethod node calls one of the allowed methods"""
    methodname = getcallmethod(node)
    if methodname in allowed_methods:
        return True
    elif methodname.split("__")[0] in allowed_methods:
        return True
    else:
        return False


def assert_calls_allowed_methods(graph, allowed_methods: list):
    for node in itergraph(graph):
        if iscallmethod(node):
            if not calls_allowed_methods(node, allowed_methods):
                raise ValueError(
                    f'Node {node} calls method "{getcallmethod(node)}", which is not one of {allowed_methods}. Please contain your forward logic'
                    f" in forward methods.\n\n{graph}"
                )


def isprimcallmethod(node):
    return node.kind() == "prim::PythonOp" and node.pyname() == "forward"


def istag(node):
    return node.kind() == "prim::PythonOp" and node.pyname() == "tag"


def get_constant_value(node):
    value_str = parse_attributes(node)["value"]
    value_type = get_type(node.output())
    value = _CASTERS[value_type](value_str)
    return value


def isprimconstant(node):
    if node.kind() == "prim::Constant":
        attrs = parse_attributes(node)
        return "value" in attrs
    else:
        return False


def get_constant_value(node):
    value_str = parse_attributes(node)["value"]
    value_type = get_type(node.output())
    value = _CASTERS[value_type](value_str)
    return value


def isprimconstant(node):
    if node.kind() == "prim::Constant":
        attrs = parse_attributes(node)
        return "value" in attrs
    else:
        return False


def islistconstruct(node, tensorlist=True):
    is_list_construct = node.kind() == "prim::ListConstruct"
    result = False
    if is_list_construct and tensorlist:
        result = istensorlist(node.output()) or isnestedtensorlist(node.output())
    return result


def islistunpack(node):
    return node.kind() == "prim::ListUnpack"


def istupleconstruct(node):
    return node.kind() == "prim::TupleConstruct"


def istupleunpack(node):
    return node.kind() == "prim::TupleUnpack"


def isprint(node):
    return node.kind() == "prim::Print"


def hasgetparam(graph):
    if graph is None:
        return False
    return any([isgetparam(node) for node in graph.nodes()])


def get_function_name(node):
    assert node.kind() == "prim::CallFunction"
    return next(node.inputs()).type().__repr__()


def islistgetitem(node):
    if node.kind() == "aten::__getitem__":
        inputs = list(node.inputs())
        maybe_list = inputs[0]
        if istensorlist(maybe_list):
            return True
        else:
            return False
    else:
        return False


def isdict(node):
    return get_type(node).startswith("Dict")


def isdictgetitem(node):
    if node.kind() == "aten::__getitem__":
        inputs = list(node.inputs())
        maybe_dict = inputs[0]
        if isdict(maybe_dict):
            return True
        else:
            return False
    else:
        return False


def islistappend(node):
    if node.kind() == "aten::append":
        inputs = list(node.inputs())
        maybe_list = inputs[0]
        if istensorlist(maybe_list):
            return True
        else:
            return False
    else:
        return False


def isatensize(node):
    return node.kind() == "aten::size"


def ispythonicaten(node):
    return any(
        [isatensize(node), islistappend(node), islistgetitem(node), isdictgetitem(node)]
    )


def isfunctional(node):
    if node.kind() == "prim::CallFunction":
        funcname = get_function_name(node)
        return funcname.startswith("__torch__.torch.nn.functional.")
    else:
        return False


def isfmotfunctional(node):
    if node.kind() == "prim::CallFunction":
        funcname = get_function_name(node)
        return funcname.startswith("__torch__.fmot.functional")
    else:
        return False


def isuserfunction(node):
    if node.kind() == "prim::CallFunction":
        funcname = get_function_name(node)
        return not funcname.startswith("__torch__.torch.nn.functional.")
    else:
        return False


def isNone(node):
    if (node.kind() == "prim::Constant") and (str(node).find("None") != -1):
        return True
    else:
        return False


def getfunctionalname(node):
    assert isfunctional(node) or isfmotfunctional(node)
    funcname = get_function_name(node)
    assert funcname.startswith("__torch__")

    funcname = funcname.split("__torch__.")[1]
    if funcname.startswith("torch.nn.functional"):
        funcname = "F." + funcname.split("torch.nn.functional.")[1]
    elif funcname.startswith("fmot.functional."):
        funcname = "fmot." + funcname.split("fmot.functional.")[1]
    else:
        raise ValueError("Could not extract functional name")

    return funcname


def getuserfuncname(node):
    assert isuserfunction(node)
    funcname = get_function_name(node)
    assert funcname.startswith("__torch__")
    funcname = funcname.split("__torch__.")[1]
    return funcname


def ispermissiveaten(node):
    """For a given node, returns True if:

    1. the node is not an aten operation

    OR if it is an aten operation, it will still return True if one
    of the following is satisfied:
        2. the inputs are all integers
        3. the node is an append, slice, or getitem applied to a tensorlist
        4. the node is aten::len
    """

    # 1: True if not aten
    if not isaten(node):
        return True

    # 2. True if all arguments are ints
    input_types = set()
    for input in node.inputs():
        input_types.add(input.type().str())
    if len(input_types) == 1:
        if list(input_types)[0] == "int":
            # print(f'Node applied to just ints {node}')
            return True

    # 3. True if it is append, slice, or getitem on a Tensor[]

    # 3.a. list __getitem__
    if node.kind() == "aten::__getitem__":
        x, idx = node.inputs()
        assert idx.type().str() in ["int", "str"]
        if x.type().str().startswith("Tensor[]"):
            return True

    # 3.b. list append
    if node.kind() == "aten::append":
        base, __ = node.inputs()
        if base.type().str().startswith("Tensor[]"):
            # print(f'TensorList.append: {node}')
            return True

    # 3.c. list slice
    if node.kind() == "aten::slice":
        # note: not checking types of slice start/end/delta arguments,
        # just the base input
        base, __, __, __ = node.inputs()
        if base.type().str().startswith("Tensor[]"):
            # print(f'TensorList.slice: {node}')
            return True

    # 4. aten::len is okay
    if node.kind() == "aten::len":
        return True

    return False


def hasfunctional(graph):
    return any([isfunctional(node) for node in graph.nodes()])


def hasuserfunction(graph):
    return any([isuserfunction(node) for node in graph.nodes()])


def needspatching(graph):
    if graph is None:
        raise ValueError("Could not get graph")
    else:
        try:
            if any(
                [
                    hasgetparam(graph),
                    hasaten(graph),
                    hasfunctional(graph),
                    hasuserfunction(graph),
                ]
            ):
                if hassubblocks(graph):
                    raise NotImplementedError(
                        f"Graph has conditional blocks, not supported at this time\n{graph}"
                    )

                assert_calls_allowed_methods(graph, ["forward"])

                return True
        except:
            print(f"needspatching failed on graph {graph}")
            raise


def itergraph(graph):
    for node in graph.nodes():
        yield node
        for blk in node.blocks():
            for sub_node in itergraph(blk):
                yield sub_node


def issuperstructure(graph):
    """
    A SuperStructure is a module that satisfies the following constraints:

    1. No direct parameter accesses in the module
    2. No arithmetic aten operations are used, but some aten ops are still allowed
        (permissive aten operation check allows for aten ops that act on collections of tensors, like aten::append)
    3. No functional operations
    """

    for node in itergraph(graph):
        if isgetparam(node):
            return False
        elif not ispermissiveaten(node):
            return False
        elif isfunctional(node) or isuserfunction(node):
            return False
    assert_calls_allowed_methods(graph, ["forward"])

    return True
