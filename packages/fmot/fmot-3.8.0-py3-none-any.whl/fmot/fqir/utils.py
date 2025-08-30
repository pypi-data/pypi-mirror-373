import numpy as np
import torch


def get_tensor_length(tprotos):
    """
    Get the seq_length from an iterable of tensor protos
    """
    length = None
    max_numel = 0
    for x in tprotos:
        sl = x.seq_length
        if sl is not None:
            numel = np.prod(sl)
            if numel > max_numel:
                length = sl
                max_numel = numel
    return length


def asint(x):
    if x.quantized:
        z = (x / 2**x.quanta).int()
        bits = x.bitwidth.bitwidth
        z = torch.clamp(z, -(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
        return z
    else:
        raise ValueError("Cannot convert unquantized tensor to integer")
