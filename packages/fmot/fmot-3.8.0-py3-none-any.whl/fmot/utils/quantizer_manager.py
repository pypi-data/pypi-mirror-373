import torch
from fmot.qat.nn import Quantizer

"""
Quantizer Aquisition
"""


def trace_quantizers(qlist, module):
    if isinstance(module, Quantizer):

        def tracing_hook(module, inputs, outputs):
            if module not in qlist:
                qlist.append(module)

        handle = module.register_forward_hook(tracing_hook)
        return handle
    return None


def get_quantizers(model, *inputs):
    """
    Returns a list of all of the model's quantizers, listed
    in order of execution.

    Args:
        model (torch.nn.Module): Converted pytorch model (qat format)
        *inputs (*torch.Tensor): Input(s) to the model, for tracing
            purposes

    Returns:
        - List of all of the quantizers in the model
    """
    qlist = []
    handles = []
    for n, m in model.named_modules():
        handle = trace_quantizers(qlist, m)
        if handle is not None:
            handles.append(handle)
    __ = model(*inputs)
    for h in handles:
        h.remove()
    return qlist


def group_quantizers(quantizers):
    """
    Args:
        quantizers (list[fmot.qat.nn.Quantizer]): list of quantizers
    Returns:
        List of quantizers and QuantizationGroups, where individual quantizers
        are replaced with their parent quantization groups
    """
    qlist_out = []
    consumed = set()
    for quant in quantizers:
        if quant not in consumed:
            if len(quant.member_of) == 0:
                qlist_out.append(quant)
                consumed.add(quant)
            else:
                for group in quant.member_of:
                    if group not in qlist_out:
                        qlist_out.append(group)
                    for member in group.members:
                        consumed.add(member)
    return qlist_out
