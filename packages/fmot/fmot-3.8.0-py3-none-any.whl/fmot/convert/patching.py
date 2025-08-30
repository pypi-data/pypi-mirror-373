from .patch_ir import get_patched_module_from_torch, get_graph
from .default_mappings import DEFAULT_MAPPINGS
from .. import torchscript_utils as tsutils
import copy
from fmot.nn import Sequencer, Loop
from textwrap import indent
from fmot.nn.super_structures import SUPERSTRUCT_DIC, ProtectedModule
import inspect
from torch import nn


def needspatching(module, mappings):
    """
    Returns if a given module needs patched with a PatchedModule. If the
    module's type is a key in the mapping dictionary, it doesn't need patching.
    Otherwise, check the TorchScript IR for aten, torch.nn.functional, and direct
    parameter accesses.

    Args:
        module (Module): Module to be checked
        mappings (dict): Dictionary of mappings
    """
    try:
        if isinstance(module, (nn.ModuleList, nn.ModuleDict, nn.ParameterList)):
            return False
        if type(module) in mappings:
            return False
        # If our module is (inherited from) a SuperStructure, we basically want to
        # skip over all aten/functional operations for the moment,
        # sublayers will still be patched later
        elif any(
            issubclass(type(module), super_struct) for super_struct in SUPERSTRUCT_DIC
        ):
            return False
        elif issubclass(type(module), ProtectedModule):
            return False

        # torchscript utils now has its own way to check for super-structure that doens't rely on the user directly
        # annotating it themselves
        graph = get_graph(module, step=isinstance(module, (Sequencer, Loop)))
        if tsutils.issuperstructure(graph):
            return False
        else:
            return tsutils.needspatching(graph)
    except:
        print(f"needspatching failed on module {module}")
        raise


def verbose_printout(parent_name, child_name, patch, original_model):
    name = parent_name
    if child_name is not None:
        name += "." + child_name
    if not isinstance(original_model, Sequencer):
        model_code = inspect.getsource(original_model.forward)
    else:
        model_code = inspect.getsource(original_model.step)
    print(f'Setting "{name}" to: {type(patch).__name__}[{patch.orig_name}]')
    print("Original Code:")
    print(indent(model_code, "  "))
    print("New Code:")
    print(indent(patch.code(), "  "))
    print()


def patch(
    model, extra_patchings=None, extra_mappings=None, deepcopy=False, verbose=False
):
    """
    Recursively patch a model, and all of its submodules, as needed.

    Args:
        model (Module): Pytorch model to be patched
        extra_patchings (dict): Optional dictionary to extend the patching dictionary
        extra_mappings (dict): Optional dictionary to extend the mapping dictionary
        deepcopy (bool): Whether the model should be copied or modified in-place
        verbose (bool): Whether to print out a report of the modules that are being patched
    """
    mappings = DEFAULT_MAPPINGS
    if extra_mappings is not None:
        mappings.update(extra_mappings)
    if deepcopy:
        model = copy.deepcopy(model)
    if needspatching(model, mappings):
        new_model = get_patched_module_from_torch(
            model, extra_patchings=extra_patchings
        )
        if verbose:
            verbose_printout("self", None, new_model, model)
        model = new_model
    _patch_in_place(model, extra_patchings, mappings, "self", verbose)
    return model


def _patch_in_place(module, extra_patchings, mappings, parent_name, verbose):
    to_patch = (
        []
    )  # Modules to patch in the next recursive step. Entries are (name, module)

    for name, submodule in module.named_children():
        # Patch everything except raw patchlists and quantdicts
        if issubclass(type(submodule), ProtectedModule):
            pass
        elif type(submodule) in mappings:
            pass
        elif needspatching(submodule, mappings) and not name in [
            "patchlist",
            "quantdict",
        ]:
            patch = get_patched_module_from_torch(
                submodule, extra_patchings=extra_patchings
            )
            module.__setattr__(name, patch)

            # Patch the patch in the next recursive step
            to_patch.append((name, patch))

            if verbose:
                verbose_printout(parent_name, name, patch, submodule)

        else:
            # Patch the submodule in the next recursive step
            to_patch.append((name, submodule))

    # Dispatch the next recursive step
    for name, submodule in to_patch:
        _patch_in_place(
            submodule,
            extra_patchings,
            mappings,
            parent_name=f"{parent_name}.{name}",
            verbose=verbose,
        )
