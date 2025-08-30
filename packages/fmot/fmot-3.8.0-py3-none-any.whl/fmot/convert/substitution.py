import torch
from torch import nn
import fmot
from fmot import qat as Q
from copy import deepcopy
from .default_substitutions import get_default_substitutions
from ..nn.super_structures import ProtectedModule
from ..utils.typing import SubstDict
from .apply_tags import copy_tags
import logging

logger = logging.getLogger(__name__)

# from fmot.nn.special_rnn import convert_dilated_lstm


def torch_to_sequencer(
    model, extra_substitutions=None, substitutions_dict=SubstDict, verbose=False
):
    substitutions = get_default_substitutions()
    if extra_substitutions is not None:
        substitutions.update(extra_substitutions)

    model = deepcopy(model)

    inherited_name = ""

    if type(model) in substitutions:
        logger.debug(
            f"{type(model)} found in substitution dict, calling _from_torchmodule for {substitutions[type(model)]}"
        )
        new_module = substitutions[type(model)]._from_torchmodule(
            model,
            toplevel=model,
            inherited_name=inherited_name,
            inherited_dict=substitutions_dict,
        )

        # copy annotations
        copy_tags(model, new_module)

        if verbose:
            print(f"Converting self ({type(model)}) to {substitutions[type(model)]}")
        model = new_module
    _recursive_substitution(
        model, substitutions, verbose, "self", model, inherited_name, substitutions_dict
    )
    return model


def _recursive_substitution(
    module,
    substitutions,
    verbose,
    parent_name,
    toplevel,
    inherited_name="",
    inherited_dict=SubstDict,
):
    for name, submodule in module.named_children():
        if type(submodule) in substitutions:
            logger.debug(
                f"{type(submodule)} found in substitution dict, calling _from_torchmodule for {substitutions[type(submodule)]}"
            )
            new_module = substitutions[type(submodule)]._from_torchmodule(
                submodule, toplevel, inherited_name + name + ".", inherited_dict
            )
            setattr(module, name, new_module)
            copy_tags(submodule, new_module)
            if verbose:
                print(
                    f"Converting {parent_name}.{name} ({type(submodule)}) to {substitutions[type(submodule)]}"
                )
        elif issubclass(type(submodule), ProtectedModule):
            pass
        else:
            _recursive_substitution(
                submodule,
                substitutions,
                verbose,
                f"{parent_name}.{name}",
                toplevel,
                inherited_name=inherited_name + f"{name}.",
                inherited_dict=inherited_dict,
            )
