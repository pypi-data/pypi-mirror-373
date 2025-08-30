from fmot.convert.default_patchings import DEFAULT_PATCHINGS, PatchRule
from fmot.convert.default_mappings import DEFAULT_MAPPINGS
from fmot.convert.default_substitutions import DEFAULT_SUBSTITUTIONS
from fmot.convert.lut_registry import LUT_REGISTRY
import inspect
from torch import nn
import fmot
import types


def iter_nn_module_beneath_package(module: types.ModuleType, depth: int):
    """Automatically yields all of the nn.Module layers under
    a given package (e.g. fmot.nn)"""
    assert isinstance(module, types.ModuleType)
    for value in module.__dict__.values():
        if isinstance(value, type) and issubclass(value, nn.Module):
            yield value
        # elif isinstance(value, types.ModuleType) and depth > 0:
        #     if "fmot" in value.__file__:
        #         for x in iter_nn_module_beneath_package(value, depth-1):
        #             yield x


def supported_ops():
    """
    Returns a list of supported operations.
    """
    sops = set()

    # iterate over all of the substitutions
    for m in DEFAULT_SUBSTITUTIONS:
        # if m.__module__.startswith("torch"):
        sops.add(m)

    # iterate over all of the patchings, ensuring that there is an available mapping
    for k, v in DEFAULT_PATCHINGS.items():
        if isinstance(v, PatchRule):
            patchings = v.options
        else:
            patchings = [v]
        sops.add(k)

    # iterate over all of the mappings, add mappings that start with builtin modules
    for m in DEFAULT_MAPPINGS:
        if m.__module__.startswith("torch"):
            sops.add(m)
        elif hasattr(m, "report_supported") and m.report_supported:
            sops.add(m)

    for m in iter_nn_module_beneath_package(fmot.nn, depth=3):
        if hasattr(m, "report_supported") and m.report_supported:
            sops.add(m)

    for m in LUT_REGISTRY:
        sops.add(m)

    return list(sops)


def typename(x):
    if isinstance(x, type):
        s = str(x)
        return s.split("'")[1]
    else:
        return x


def conversion_branch(op):
    branch = [op]
    if inspect.isfunction(op):
        assert op.__module__ == "torch.nn.functional"
        op = "F." + op.__name__
        branch = [op]
    elif type(op).__name__ == "builtin_function_or_method":
        name = op.__name__
        op = "aten::" + name
        branch = ["torch." + name, op]
    if op in DEFAULT_PATCHINGS:
        op = DEFAULT_PATCHINGS[op]
        if isinstance(op, PatchRule):
            op = op.options[0]
        branch += [op]
    if op in DEFAULT_MAPPINGS:
        op = DEFAULT_MAPPINGS[op]
        branch += [op]
    else:
        branch += ["patched", "mapped"]
    return " -> ".join([typename(n) for n in branch])


if __name__ == "__main__":
    print(list(iter_nn_module_beneath_package(fmot.nn, depth=3)))
    # print(fmot.nn.__file__)
