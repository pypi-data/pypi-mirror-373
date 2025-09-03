import torch
from torch import nn
from collections import namedtuple
from functools import wraps
import warnings


class _diffable_pos(torch.autograd.Function):
    """
    Returns the mask x > 0 as a FloatTensor.
    Uses a surrogate gradient equivalent to the gradient w.r.t. ReLU
    """

    @staticmethod
    def forward(ctx, x):
        nz = x > 0
        ctx.save_for_backward(nz)
        return nz.float()

    @staticmethod
    def backward(ctx, grad):
        grad_nz = None
        if ctx.needs_input_grad[0]:
            (nz,) = ctx.saved_tensors
            grad_nz = nz.float() * grad
        return grad_nz


ActivationCount = namedtuple("ActivationCount", ["L1", "L0", "numel"])


class ActivationCounter(nn.Module):
    def __init__(self):
        super().__init__()
        self.reset_counter()
        self._reset_by_wrapper = False

    @torch.jit.ignore
    def forward(self, x, mask=None):
        if not self._reset_by_wrapper:
            msg = (
                "Activation counters were not reset upon reciept of new inputs."
                + " This can lead to unbounded memory growth."
                + " Please wrap the top-level forward method with @fmot.utils.reset_counters."
            )
            if isinstance(self, ActivationCountingReLU):
                stacklevel = 4
            else:
                stacklevel = 3
            warnings.warn(msg, stacklevel=stacklevel)
        y = x.abs()
        numel = y.numel()
        if mask is not None:
            y = y.masked_fill(mask == 0, 0)
            numel = mask.sum()
        self._L1 += y.sum()
        self._L0 += _diffable_pos.apply(y).sum()
        self._numel += numel
        return x

    def reset_counter(self, _from_wrapper=False):
        self._L1 = 0
        self._L0 = 0
        self._numel = 0
        if _from_wrapper:
            self._reset_by_wrapper = True

    def collect(self, reset=True):
        out = ActivationCount(L1=self._L1, L0=self._L0, numel=self._numel)
        if reset:
            self.reset_counter()
        return out


class ActivationCountingReLU(ActivationCounter):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()

    @torch.jit.ignore
    def forward(self, x):
        x = self.relu(x)
        return super().forward(x)


ActivityScore = namedtuple("ActivationScore", ["L1", "L0"])


def collect_activations(model, reset=True):
    L1 = 0
    L0 = 0
    numel = 0
    itemized = {}
    for name, module in model.named_modules():
        if isinstance(module, ActivationCounter):
            count_obj = module.collect(reset=reset)
            L1 += count_obj.L1
            L0 += count_obj.L0
            numel += count_obj.numel
            itemized[name] = ActivityScore(
                L1=count_obj.L1 / count_obj.numel, L0=count_obj.L0 / count_obj.numel
            )
    return ActivityScore(L1=L1 / numel, L0=L0 / numel), itemized


def reset_counters(obj, _from_wrapper=False):
    """
    obj: either a nn.Module or a function
        if obj is a Module, will reset activation counters for all submodules
        if obj is a class method of an nn.Module, it will be wrapped such that
            it will reset counters each time the method is called (before
            evaluation of the method)
    """
    if isinstance(obj, nn.Module):
        for module in obj.modules():
            if isinstance(module, ActivationCounter):
                module.reset_counter(_from_wrapper=_from_wrapper)
    elif callable(obj):
        f = obj

        @wraps(f)
        def wrapped(*args, **kwargs):
            self = args[0]
            if not isinstance(self, nn.Module):
                raise ValueError(
                    "reset_counters must wrap a class method of a torch.nn.Module"
                )
            reset_counters(self, _from_wrapper=True)
            return f(*args, **kwargs)

        return wrapped
    else:
        raise ValueError(
            "reset_counters expects either a nn.Module or function to wrap"
        )
