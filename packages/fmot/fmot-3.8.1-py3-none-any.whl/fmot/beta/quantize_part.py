import torch
from torch import nn
import fmot
from fmot.qat.control import enable_quantization
from typing import *


def rgetattr(obj, attr, default=None):
    try:
        if "." not in attr:
            return getattr(obj, attr)
        else:
            L = attr.split(".")
            return rgetattr(getattr(obj, L[0]), ".".join(L[1:]), default)
    except AttributeError:
        return default


def quantize_part(model: fmot.ConvertedModel, keys: List[str]):
    """
    Enable quantization only in the chosen parts of the model heirarchy.

    Example:
    ```python
    # quantize the full model
    cmodel = fmot.ConvertedModel(...)
    cmodel.quantize(calibration_data)

    # enable quantization just in the `rnn` submodule; need to tag on 'model.model'
    # due to how ConvertedModel wraps the original model.
    quantize_part(cmodel, 'model.model.rnn')
    ```
    """
    model.disable_quantization()

    for key in keys:
        module = rgetattr(model, key)
        if module is None:
            raise KeyError(
                f"model has no attribute {key}\n{list(map(lambda x: x[0], model.named_modules()))}"
            )
        enable_quantization(module, True)
