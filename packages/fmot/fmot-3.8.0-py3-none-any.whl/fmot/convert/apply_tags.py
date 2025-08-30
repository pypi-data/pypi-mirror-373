import torch
from torch import nn
from fmot.qat.nn import AtomicModule, Quantizer, DefObs, ParameterQuantizer
from typing import *

VERBOSE = False


def apply_dont_round(tag_value: bool, module: AtomicModule):
    """ "Disables rounding on an atomic module if the value of the tag is True"""
    if tag_value:
        module.round = False

        if VERBOSE:
            print(f"Disabling rounding in module {module}")


def apply_observer_class(tag_value: Optional[str], module: AtomicModule):
    if tag_value is not None:
        for child in module.modules():
            if isinstance(child, Quantizer) and not child.is_param_quantizer:
                new_obs = DefObs.get_obs(tag_value)()
                child.observer = new_obs

            if VERBOSE:
                print(f"Setting observer to {tag_value} due to a quantization tag")


def apply_hello_world(tag_value: Optional[str], module: AtomicModule):
    print(f"hello world = {tag_value}")


TAG_APPLIERS = {
    "dont_round": apply_dont_round,
    "observer_class": apply_observer_class,
    "hello_world": apply_hello_world,
}


def copy_tags(parent: nn.Module, child: nn.Module):
    """Carry any tags from parent module to child module (for use in both patching and mapping)"""
    for tag_name in TAG_APPLIERS.keys():
        if hasattr(parent, tag_name):
            setattr(child, tag_name, getattr(parent, tag_name))


def apply_tags_to_atomic_children(model: nn.Module):
    """ "Enforce tags from a parent module to all of its atomic children (including itself)

    Supported tags:
        _avoid_round = True -> this module will avoid numerical rounding (for example, used for DWConv1d)

        (more to be added)
    """

    modules = set(model.modules())
    modules.add(model)
    for module in modules:
        # create a set of the atomic submodules of the module (including itself if it is atomic)
        atomic_children = set(module.modules())
        atomic_children.add(module)
        atomic_children = filter(lambda x: isinstance(x, AtomicModule), atomic_children)

        for tagname, tagapplier in TAG_APPLIERS.items():
            if hasattr(module, tagname):
                tag_value = getattr(module, tagname)
                if VERBOSE:
                    print(f"module has a {tagname}={tag_value} annotation")
                for child in atomic_children:
                    tagapplier(tag_value, child)
