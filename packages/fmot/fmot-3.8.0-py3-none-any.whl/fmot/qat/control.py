from .nn import Quantizer, ObserverBase, Shift, Gt0, ParameterQuantizer, ILUT, GMACv2
from .annotated_tensors import set_dim_annotations
import torch
from .bitwidths import BitwidthConfig, bw_conf_dict
import inspect
from typing import get_type_hints
import warnings


def cache_parameters(module):
    for submodule in module.modules():
        if isinstance(submodule, ParameterQuantizer):
            submodule.cache()


def decache_parameters(module):
    for submodule in module.modules():
        if isinstance(submodule, ParameterQuantizer):
            submodule.decache()


def enable_observation(model, value=True):
    for module in model.modules():
        if isinstance(module, (Quantizer, ObserverBase)):
            module.observe = value
        elif hasattr(module, "observe"):
            if isinstance(module.observe, bool):
                module.observe = value
    return model


def disable_observation(model):
    return enable_observation(model, False)


def get_all_tensors(x):
    """Flattens any nested iterator containing tensors into a single-level list of tensors"""
    if isinstance(x, torch.Tensor):
        return [x]
    elif isinstance(x, (tuple, list)):
        res = []
        for xx in x:
            res += get_all_tensors(xx)
        return res
    elif isinstance(x, dict):
        res = []
        for xx in x.values():
            res += get_all_tensors(xx)
        return res
    else:
        return []


def enable_quantization(model, value=True):
    for module in model.modules():
        if isinstance(module, Quantizer):
            module.quantize = value
        elif hasattr(module, "quantize"):
            if isinstance(module.quantize, bool):
                module.quantize = value
    return model


def disable_quantization(model):
    return enable_quantization(model, False)


def needs_second_pass(model):
    return any([type(l) in [Shift, Gt0, ILUT, GMACv2] for l in model.modules()])


def get_dimensions_from_output(output):
    """
    Recursively iterate through the output to find a valid leaf node with a .dimensions attribute.
    If multiple dimensions are found, raise an exception with an error message.

    Args:
        output: The model output which could be a tensor, list, or dictionary.

    Returns:
        The dimensions attribute of the leaf node.
    """

    def recursive_find_dimensions(data, found_dimensions=None):
        if found_dimensions:
            # Return the "Top-Most" layer Dimension.
            return found_dimensions

        if isinstance(data, torch.Tensor):
            found_dimensions = data.dimensions if hasattr(data, "dimensions") else None
        elif isinstance(data, (list, tuple)):
            for item in data:
                found_dimensions = recursive_find_dimensions(item, found_dimensions)
        elif isinstance(data, dict):
            for value in data.values():
                found_dimensions = recursive_find_dimensions(value, found_dimensions)
        elif data is None:
            pass
        else:
            raise Exception(f"Err: Unhandled data type: {type(data)}")

        return found_dimensions

    dimensions = recursive_find_dimensions(output)
    if dimensions is None:
        warnings.warn("Err: No .dimensions attribute found in the output")
    return dimensions


def get_num_input_args(model: torch.nn.Module) -> int:
    """
    Returns the number of arguments expected by the model's forward method.

    Args:
        model (nn.Module): The PyTorch model.

    Returns:
        int: The number of arguments expected by the forward method.
    """
    # Get the type hints of the model's forward method
    forward_func = model.model.forward

    # Determine the number of arguments expected by the forward method
    sig = inspect.signature(forward_func)
    params = sig.parameters.values()
    num_params = len(params)
    return num_params


@torch.no_grad()
def quantize(
    model, input_iterator, dimensions=["B", "T", "F"], report_qsnr=False, _pass=0
):
    """Quantize a model, given a set of test inputs.

    Args:
        model (:class:`torch.nn.Module`): Model to be quantized
        input_iterator (iterable): Inputs to use when setting quantization parameters
        dimensions (list of str): Which dimension is which
        report_qsnr (bool): Report the quantization signal-to-noise ratio
    """
    # First pass: Obs ON, Quant Off
    # Second pass: Obs ON, Quant ON
    # Final state: Obs Off, Quant ON
    # Second pass is used to handle gt0 ops:can't quantize its inputs in first pass
    # or we would observe zeros in many cases

    if report_qsnr:
        x0 = input_iterator[0]
        if isinstance(x0, torch.Tensor):
            x0 = (x0,)
        yfp = model(*x0)
    batch_dim = dimensions.index("B")
    if len(input_iterator) <= 1 and input_iterator[0].shape[batch_dim] <= 1:
        raise Exception(
            " At least two samples should be given in order to track quantization statistics"
            " , but you only fed one input with batch dimension 1."
        )

    # do preliminary run on all batches to init some observers
    for i, x in enumerate(input_iterator):
        for xx in get_all_tensors(x):
            set_dim_annotations(dimensions, xx)
        if not isinstance(x, tuple):
            out = model(x)
        else:
            out = model(*x)

    # now enable observation
    model = enable_observation(model)

    # calibrate the model on all batches
    for i, x in enumerate(input_iterator):
        for xx in get_all_tensors(x):
            set_dim_annotations(dimensions, xx)
        if not isinstance(x, tuple):
            out = model(x)
        else:
            out = model(*x)

    setattr(model, "output_dimensions", get_dimensions_from_output(out))

    model = disable_observation(model)
    model = enable_quantization(model)
    if _pass == 0 and needs_second_pass(model):
        model = quantize(model, input_iterator, dimensions=dimensions, _pass=1)
    if report_qsnr:
        yfq = model(*x0)
        print(f"QSNR: {qsnr(yfp, yfq).cpu().item():.3f} dB")

    return model


@torch.no_grad()
def measure_qsnr(model, input_iterator):
    x = input_iterator[0]
    yfq = model(x)
    disable_quantization(model)
    yfp = model(x)
    enable_quantization(model)
    print(yfp.flatten())
    return qsnr(yfp.flatten(), yfq.flatten())


def ignore_infnan(x):
    x[torch.isnan(x)] = 0
    x[torch.isinf(x)] = 0
    return x


def qsnr(Yfp, Yfq):
    Yfp = ignore_infnan(Yfp).flatten()
    Yfq = ignore_infnan(Yfq).flatten()
    num = Yfp.pow(2).sum()
    den = (Yfp - Yfq).pow(2).sum()
    return 10 * torch.log10(num / den)


def change_bitwidth_in_place(model, bw_conf):
    """Modify a model's bitwidth in-place (homogenous)

    Args:
        model (torch.nn.Module)
        bw_conf (str, BitwidthConfig): new precision to use

    Returns:
        model
    """
    if not isinstance(bw_conf, BitwidthConfig):
        bw_conf = bw_conf_dict[bw_conf]
    for module in model.modules():
        if isinstance(module, Quantizer):
            module.update_bitwidth(bw_conf)
    return model
