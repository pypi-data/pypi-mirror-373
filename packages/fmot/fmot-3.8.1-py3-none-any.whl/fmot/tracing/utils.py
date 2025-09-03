import inspect


def combine_iterators(x, types=None):
    """
    Combines all tuples/lists/dict-values contained inside of x into a single list.
    Example:

        x = (1, [2,3,4], (5, 6), {'alpha': 9})
        print(combine_iterators(x))
        >>> [1,2,3,4,5,6,9]

    """
    out = []
    _combine_iterators(x, out, types=types)
    return out


def _combine_iterators(x, out, types=None):
    """Construct a flattened list recursively"""
    if isinstance(x, (list, tuple)):
        for xx in x:
            _combine_iterators(xx, out, types=types)
    elif isinstance(x, dict):
        for xx in x.values():
            _combine_iterators(xx, out, types=types)
    else:
        if types is not None:
            if isinstance(x, types):
                out.append(x)
        else:
            if x is not None:
                out.append(x)


def getargnames(module):
    """Get a list of the argument names for a module's forward method"""
    if hasattr(module, "_getargnames"):
        ret = module._getargnames()
    else:
        sig = inspect.signature(type(module).forward)
        ret = list(dict(sig.parameters).keys())[1:]
    return ret


def store_hierarchical_names(model):
    """Stores a hierarchical name for each submodule in a model"""
    for name, module in model.named_modules():
        try:
            module.hierarchical_name = name
        except:
            pass


def get_hierarchical_name(module):
    """Returns a module's hierarchical name, if one has been assigned.

    Otherwise, returns the name of its type
    """
    if hasattr(module, "hierarchical_name"):
        ret = module.hierarchical_name
    else:
        ret = type(module).__name__
    return ret


def allhaveprotos(tensorlist):
    """Checks if every tensor in tensorlist has a proto attribute, while skipping over None inputs

    Vacuously True if tensorlist is empty
    """
    ret = True
    if len(tensorlist) > 0:
        for x in tensorlist:
            if x is None:
                # print("Warning: None input is being skipped over in the graph")
                pass
            elif not hasattr(x, "proto"):
                ret = False
    return ret


# automatic variable naming

COUNT = 0


def get_autogen_count():
    global COUNT
    COUNT += 1
    return COUNT


def autogen_name(prefix="x"):
    return f"%{prefix}.{get_autogen_count()}"


def reset_autogen_count():
    global COUNT
    COUNT = 0
