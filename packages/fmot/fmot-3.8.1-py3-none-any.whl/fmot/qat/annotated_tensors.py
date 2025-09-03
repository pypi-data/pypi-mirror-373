import torch
from functools import wraps, partial
from .bitwidths import fqint4, fqint8, fqint16, fqint24
import warnings

ANNOS = [
    "bitwidth",
    "quanta",
    "quantized",
    "avg_sparsity",
    "annotated",
    "prev_relu",
    "density_per_element",
]  # ,'dimensions']


def tag_dim(forward_func):
    """Decorator for any forward method that tags the dimensions
    of the inputs with the class dimensions attribute
    If inputs have a dimensions attribute already, it's left unchanged
    """

    def dim_tagged_forward(self, *args, **kwargs):
        for arg in args:
            if not hasattr(arg, "dimensions") and arg is not None:
                set_dim_annotations(self.dimensions, arg)
        return forward_func(self, *args, **kwargs)

    return dim_tagged_forward


def annotate(
    x,
    bitwidth,
    quanta,
    quantized=False,
    avg_sparsity=None,
    dimensions=None,
    prev_relu=False,
    density_per_element=None,
):
    x.bitwidth = bitwidth
    x.quanta = quanta
    x.quantized = quantized
    if avg_sparsity is None:
        avg_sparsity = 0.0
    x.avg_sparsity = avg_sparsity
    x.prev_relu = prev_relu
    set_dim_annotations(dimensions, x)
    x.annotated = True
    x.density_per_element = density_per_element
    return x


def copy_annotations(x, y):
    """copy x's annotations to y"""
    for anno in ANNOS:
        y.__setattr__(anno, x.__getattribute__(anno))
    try:
        y.__setattr__("dimensions", x.__getattribute__("dimensions"))
    except:
        warnings.warn(
            "Input dimensions are missing: dimension information has not been propagated correctly"
        )
    return y


def cast_float_annotated(x):
    y = x.float()
    y = copy_annotations(x, y)
    return y


def copy_dim_annotations(x, y):
    """copy x's dimensions annotations to y"""
    try:
        dimensions = x.__getattribute__("dimensions")
        if dimensions is not None:
            y.__setattr__("dimensions", list(dimensions))
    except:
        pass
        # warnings.warn(
        #     "Input dimensions are missing: dimension information has not been propagated correctly"
        # )
    return y


def set_dim_annotations(dim, y):
    """set y's dimensions annotation to dim"""
    try:
        if type(y) == tuple:
            for yy in y:
                yy.__setattr__("dimensions", dim)
        else:
            y.__setattr__("dimensions", dim)
    except:
        # warnings.warn("Could not propagte dimension to input")
        pass
    return y


def get_dim_annotations(*args):
    """get arg's dimensions annotation
    We assume that longest dimension = last dimension
    to support broadcasting
    """
    try:
        max_len_dim = 0
        for arg in args:
            try:
                if len(arg.dimensions) > max_len_dim:
                    max_len_dim = len(arg.dimensions)
                    dimensions = arg.__getattribute__("dimensions")
            except:
                pass  # we discard if one of the inputs is not annotated
        return dimensions
    except:
        # warnings.warn(
        #     "Input dimensions are missing: dimension information has not been propagated correctly"
        # )
        return None


def asint(x):
    if x.quantized:
        z = (x / 2**x.quanta).int()
        bits = x.bitwidth.bitwidth
        z = torch.clamp(z, -(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
        return z
    else:
        raise ValueError("Cannot convert unquantized tensor to integer")


def check_for_annotations(obj):
    if isinstance(obj, torch.Tensor):
        if not hasattr(obj, "annotated"):
            warnings.warn(
                "input tensor has not been passed through a quantizer, "
                + "indicating that an operation has not been properly quantized",
                stacklevel=4,
            )
    elif callable(obj):
        f = obj

        @wraps(f)
        def wrapped(self, *args, **kwargs):
            for arg in args:
                check_for_annotations(arg)
            for k, v in kwargs.items():
                check_for_annotations(v)
            outputs = f(self, *args, **kwargs)
            if isinstance(outputs, torch.Tensor):
                check_for_annotations(outputs)
            else:
                for output in outputs:
                    check_for_annotations(output)

            return outputs

        return wrapped
    else:
        pass


def get_all_input_tensors(*args, **kwargs):
    for arg in list(args) + list(kwargs.values()):
        if isinstance(arg, torch.Tensor):
            yield arg
        elif isinstance(arg, (tuple, list)):
            for x in get_all_input_tensors(*arg):
                yield x
        elif isinstance(arg, dict):
            for x in get_all_input_tensors(**arg):
                yield x
        elif isinstance(arg, (float, int, bool)):
            pass
        elif arg is None:
            pass
        else:
            raise ValueError(f"Unexpected argument type: {type(arg)}")


class UnsupportedPrecisionError(Exception):
    pass


def raise_error_on_int24(message: str, *args, **kwargs):
    """Raises an exception if any int24 tensors are found in traversal of args/kwargs.

    Arguments:
        message (str): an error message to explain why int24 is not supported.
        args (Any)
        kwargs (Any)
    """
    for arg in get_all_input_tensors(*args, **kwargs):
        if hasattr(arg, "bitwidth"):
            if arg.bitwidth == fqint24:
                raise UnsupportedPrecisionError(message)
        else:
            # raise ValueError(f"torch.Tensor lacked a bitwidth annotation -- {message}")
            pass


def supports_int24(status: bool = True, reason: str = None):
    """Wrapper: if status is False, raises an error if any
    int24 inputs are passed in

    Arguments:
        status (bool): if True, then no error will be raised on int24 inputs
            If False, will check and raise errors on int24 inputs.
        reason (str, optional): add this reason to the error message. Optional.

    Usage example:
    ```python

    class BareLUT(AtomicModule):
        ...

        @int24_supported(status=False, reason="BareLUT does not support int24 inputs")
        def forward(self, ...):
            ...
    ```
    """

    def wrapper(func: callable):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            # only check if status = False
            if status:
                pass
            else:
                message = (
                    f"Module of type {type(self)} got an int24 input. Not supported."
                )
                if reason is not None:
                    message += f"\nReason: {reason}"
                raise_error_on_int24(message, *args, **kwargs)

            return func(self, *args, **kwargs)

        return wrapped

    return wrapper
