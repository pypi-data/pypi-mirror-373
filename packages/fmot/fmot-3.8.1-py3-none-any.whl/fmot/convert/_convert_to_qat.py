from . import patching, mapping, substitution, prune_reparametrization, apply_tags
from fmot.qat import bitwidths
import warnings
import inspect
import torch
from fmot.qat.nn import (
    DEFAULT_OBSERVERS,
    density_matmul,
    act_density,
    ObserverBase,
    QuantWrapper,
)
from fmot.configure import CONFIG, configure_act_observer, configure_param_observer
from typing import *


def convert(
    model: torch.nn.Module,
    precision: str,
    interpolate: bool,
    verbose: bool,
    dimensions: List[Literal["B", "T", "F"]],
    observer: Union[ObserverBase, str] = DEFAULT_OBSERVERS["default"],
    observer_conf: dict = None,
    param_observer: str = None,
) -> Tuple[QuantWrapper, dict]:
    """
    Args:
        model (torch.nn.Module): pytorch model to convert
        precision (str): precision -- 'standard' or 'double'
        interpolate (bool): whether to use interpolating lookup tables
        verbose (bool): if True, will print out details of the conversion process
        dimensions (list[str]): list of input tensor dimension roles,
            i.e. :attr:`['B', 'T', 'F']`.
        observer (fmot.qat.nn.ObserverBase): observer class to use for calibration,
            default is MinMaxObserver
        observer_conf (dict): parameters to pass into the observer upon initialization,
            such as smoothing coefficients. Default is None.

    Returns:

        - converted_model
        - parameter_mapping_dictionary
    """

    # Get model signature
    try:
        signature = inspect.signature(model.forward)
    except:
        signature = None

    if param_observer is not None:
        configure_param_observer(param_observer)

    if isinstance(observer, str):
        observer = configure_act_observer(observer)

    if isinstance(precision, str):
        precision = bitwidths.bw_conf_dict[precision]
    pinfo = prune_reparametrization.remove_all_pruners(model, verbose=verbose)
    param_map_dict = dict()
    smodel = substitution.torch_to_sequencer(
        model,
        extra_substitutions=None,
        substitutions_dict=param_map_dict,
        verbose=verbose,
    )
    pmodel = patching.patch(
        smodel, extra_patchings=None, extra_mappings=None, verbose=verbose
    )
    obs_kwargs = observer_conf if observer_conf else {}
    cmodel = mapping.map_to_qat(
        pmodel,
        bw_conf=precision,
        interpolate=interpolate,
        extra_mappings=None,
        quant_wrap=True,
        deepcopy=False,
        verbose=verbose,
        observer=observer,
        dimensions=dimensions,
        signature=signature,
        **obs_kwargs,
    )
    cmodel.substitutions_dict = param_map_dict
    prune_reparametrization.reapply_all_pruners(
        cmodel, model, pinfo, param_map_dict, verbose=verbose
    )

    # inherit any tags
    apply_tags.apply_tags_to_atomic_children(cmodel)

    return cmodel, param_map_dict


def convert_torch_to_qat(
    model,
    bw_conf="double",
    interpolate=True,
    extra_patchings=None,
    extra_mappings=None,
    extra_substitutions=None,
    quant_wrap=True,
    verbose=False,
    remove_pruners=True,
    dimensions=None,
):
    """Convert a PyTorch model to fmot.qat format

    Args:
        model (:class:`torch.nn.Module`): PyTorch model to be converted
        bw_conf (str): Bitwidth configuration. Must be one of
            ``["double", "standard", "eights"]``. Default is ``"double"``. See
            :doc:`precision` for more information.
        interpolate (bool): Whether to use interpolation (and other approximation methods)
            to improve the accuracy of LUT-based nonlinearities.
        extra_patchings (dict): Optional dictionary of supplemental patching rules.
        extra_mappings (dict): Optional dictionary of supplemental mapping rules.
        quant_wrap (bool): Whether to wrap the model with input quantizers.
            Default is True.
        verbose (bool): Whether to print a status report during conversion.
        remove_pruners (bool): whether to remove (and reapply) pruning
            reparametrization during conversion, default True.
        dimensions (list[str]): dimension tags for the model input. Not a
            required argument.
    """
    raise ValueError("Deprecated")
