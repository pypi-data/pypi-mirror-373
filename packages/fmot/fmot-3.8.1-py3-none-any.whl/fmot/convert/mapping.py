import copy
from textwrap import indent

from fmot.qat import bitwidths

from .default_mappings import DEFAULT_MAPPINGS
from .. import qat as Q
from ..qat.nn.quant_wrap import QuantWrapper
from ..nn.super_structures import ProtectedModule
from .apply_tags import copy_tags
from torch import nn


def verbose_printout(name, fp_model, quant_model):
    ind = "    "
    print(name)
    print(f"  float:\n{indent(str(fp_model), ind)}")
    print(f"  qat:\n{indent(str(quant_model), ind)}\n")


def map_to_qat(
    model,
    bw_conf,
    interpolate=True,
    extra_mappings=None,
    quant_wrap=True,
    observer=None,
    deepcopy=False,
    verbose=False,
    dimensions=None,
    signature=None,
    **observer_kwargs,
):
    """Replace float-precision pytorch modules with their quantization-aware counterparts

    Args:
        model (Module): Floating point model to be mapped.
        bw_conf: Bitwidth config (see :doc:`precision`)
        extra_mappings (dict): Optional dictionary of supplemental mapping rules
        deepcopy (bool): Whether the model should be copied or modified in-place
        verbose (bool): Whether to print a status report during mapping.
    """
    if observer is None:
        observer = Q.nn.DEFAULT_OBSERVERS["default"]

    mappings = DEFAULT_MAPPINGS
    if extra_mappings is not None:
        mappings.update(extra_mappings)

    if deepcopy:
        model = copy.deepcopy(model)

    # Get bitwidth conf as a BitwidthConfig object
    if isinstance(bw_conf, str):
        bw_conf = bitwidths.bw_conf_dict[bw_conf]

    # Map root node if it is directly mappable
    if type(model) in mappings:
        new_model = mappings[type(model)]._from_float(
            parent=model,
            bw_conf=bw_conf,
            interpolate=interpolate,
            observer=observer,
            **observer_kwargs,
        )
        if verbose:
            verbose_printout("self", model, new_model)
        copy_tags(model, new_model)

        model = new_model
    # Otherwise map recursively
    else:
        _map(
            model,
            mappings,
            bw_conf,
            interpolate,
            "self",
            verbose,
            observer,
            **observer_kwargs,
        )
    if quant_wrap:
        model = QuantWrapper(
            model=model,
            bitwidth=bw_conf.activations,
            observer=observer,
            dimensions=dimensions,
            signature=signature,
            **observer_kwargs,
        )

    return model


def is_container(module: nn.Module):
    """
    Returns whether a given module is a container-type (e.g. ModuleList/ModuleDict)

    Used to check it is safe for a given module to be a leaf node in mapping
    """
    return isinstance(module, (nn.ModuleList, nn.ModuleDict))


def _map(
    module,
    mappings,
    bw_conf,
    interpolate,
    parent_name,
    verbose,
    observer,
    **observer_kwargs,
):
    to_convert = []  # Modules to attempt to map in the next recursive step
    nchildren = 0

    # TODO: replace this with the tagging API
    if hasattr(module, "precision"):
        precision_tag = module.precision
        bw_conf = bitwidths.bw_conf_dict.get(precision_tag, bw_conf)
        print("Found precision tag")

    if hasattr(module, "limits"):
        limits = module.limits
        print(f"Found limits tag {limits}")

    for name, submodule in module.named_children():
        new_name = f"{parent_name}.{name}"
        nchildren += 1

        curr_bw_conf = bw_conf
        if hasattr(submodule, "precision"):
            precision_tag = submodule.precision
            curr_bw_conf = bitwidths.bw_conf_dict.get(precision_tag, curr_bw_conf)
            print("Found precision tag")

        mapped = False
        for cls_in, cls_out in mappings.items():
            if isinstance(submodule, cls_in):
                new_module = cls_out._from_float(
                    submodule,
                    bw_conf=curr_bw_conf,
                    interpolate=interpolate,
                    observer=observer,
                    **observer_kwargs,
                )
                module.__setattr__(name, new_module)
                if verbose:
                    verbose_printout(new_name, submodule, new_module)

                # automagically copy tags to the mapped module
                copy_tags(submodule, new_module)

                mapped = True
                break
        if not mapped:
            if issubclass(type(submodule), ProtectedModule):
                pass
            else:
                to_convert.append((new_name, submodule))
    if nchildren == 0 and not is_container(module):
        raise ValueError(
            f"Reached leaf node {parent_name} (type: {module}) that could not be mapped."
        )
    for name, submodule in to_convert:
        _map(
            submodule,
            mappings,
            bw_conf,
            interpolate,
            name,
            verbose,
            observer,
            **observer_kwargs,
        )
