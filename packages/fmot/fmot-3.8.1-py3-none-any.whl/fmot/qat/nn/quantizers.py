import torch
from torch import nn
import warnings
from ..fake_quantization import fake_quantize
from ..bitwidths import Bitwidth
from ..annotated_tensors import (
    annotate,
    copy_dim_annotations,
    set_dim_annotations,
    tag_dim,
    ANNOS,
)
from ._utils import intitem

# from fmot.utils import reset_counters
from torch import Tensor
from typing import List, Tuple, Optional
from torch.jit import Final
import math
from functools import partial
from fmot.configure import CONFIG
import logging

logger = logging.getLogger(__name__)

EPS = 2**-40


class ObserverBase(nn.Module):
    """Base observer class to be subclassed to implement a particular observer.

    All Observers must subclass this base class
    (otherwise automatic quantization mechanisms will fail).
    """

    def __init__(self):
        super().__init__()
        self.observe = False
        self.cache = None

    def reset(self):
        raise NotImplementedError

    @torch.no_grad()
    def update_statistics(self, x):
        """
        Each subclass must implement this method; used to update the observer's
        internal statistics -- to be used later to optimize the quantization
        configuration
        """
        raise NotImplementedError

    def forward(self, x):
        """
        If the observation is enabled, internal statistics will be updated.
        """
        if self.observe:
            self.update_statistics(x)

    def calculate_quanta(self, bits, verbose=False):
        r"""
        Calculates the optimal quanta given internal statistics. Wrapper method
        to _calculate_quanta, with caching mechanics. Subclasses must implement
        _calculate_quanta.

        Args:
            bits (int): bitwidth to be used once the observed tensor is quantized

        Returns:
            quanta (int): optimal quanta
        """
        return self._calculate_quanta(bits, verbose=verbose)

    def _calculate_quanta(self, bits, verbose=False):
        r"""
        Calculates the optimal quanta given internal statistics. Must be implemented
        in subclasses

        Args:
            bits (int): bitwidth to be used once the observed tensor is quantized

        Returns:
            quanta (int): optimal quanta
        """
        raise NotImplementedError

    def do_on_fp(self, x):
        """When quantize = False, this operation is performed to transform input x.
        By default, x is not modified. Subclasses can overwrite this."""
        return x


class MinMaxObserver(ObserverBase):
    """MinMaxObserver stores a running minimum and maximum value

    The optimal quanta is chosen so that the quantization range barely
    fits the min/max observed activations.

    .. note::

        This observer is very sensitive to large-magnitude outlier activations.
        If any outlier activations are observed, the resulting quantization range
        will be very large and may result in large numerical rounding errors.

    .. note::

        This observer is not the best choice to use for quantization aware training
        (QAT). During QAT, activation or parameter magnitudes may shrink.
        The MinMaxObserver's min/max statistics will not change, even if the
        magnitude is changing over time.
    """

    def __init__(self, bits_headroom: int = 0):
        super().__init__()
        self.register_buffer("min_val", torch.tensor([]))
        self.register_buffer("max_val", torch.tensor([]))
        self.reset()
        self.bits_headroom = bits_headroom

    def reset(self):
        dev = self.min_val.device
        self.register_buffer("min_val", torch.tensor([], device=dev))
        self.register_buffer("max_val", torch.tensor([], device=dev))

    @torch.no_grad()
    def update_statistics(self, x):
        x[torch.isinf(x)] = 0
        x[torch.isnan(x)] = 0
        if self.min_val.numel() == 0 or self.max_val.numel() == 0:
            self.min_val = torch.min(x)
            self.max_val = torch.max(x)
        else:
            self.min_val = torch.min(self.min_val, torch.min(x))
            self.max_val = torch.max(self.max_val, torch.max(x))

    def _calculate_quanta(self, bits, verbose=False):
        if self.min_val.numel() == 0 or self.max_val.numel() == 0:
            raise Exception(f"Must run observer before calling calculate_quanta {self}")

        min_val = torch.min(self.min_val, -torch.ones_like(self.min_val) * EPS)
        max_val = torch.max(self.max_val, torch.ones_like(self.max_val) * EPS)

        quanta_neg = torch.ceil(torch.log2(torch.abs(min_val)) + 1 - bits)
        quanta_pos = torch.ceil(torch.log2(torch.abs(max_val) / (2 ** (bits - 1) - 1)))

        if verbose:
            print("qpos:", quanta_pos)
            print("qneg:", quanta_neg)
        quanta = torch.max(quanta_neg, quanta_pos)

        if bits == 16:
            quanta = quanta + int(max(CONFIG.minmax_headroom, self.bits_headroom, 0))

        return quanta


class QuantileMinMaxObserver(MinMaxObserver):
    def __init__(self, quantile=0.99):
        super().__init__()
        self.quantile = quantile

    @torch.no_grad()
    def update_statistics(self, x):
        x[torch.isinf(x)] = 0
        x[torch.isnan(x)] = 0

        curr_max = torch.quantile(x, self.quantile)
        curr_min = -torch.quantile(-x, self.quantile)

        if self.min_val.numel() == 0 or self.max_val.numel() == 0:
            self.min_val = curr_min
            self.max_val = curr_max
        else:
            self.min_val = torch.min(self.min_val, curr_min)
            self.max_val = torch.max(self.max_val, curr_max)


class MovingAverageMinMaxObserver(MinMaxObserver):
    """Takes an exponential moving average of min and max activation statistics

    The optimal quanta is chosen so that the quantization range barely fits the min/max moving
    averages.

    Args:
        alpha (float): Smoothing coefficient, between 0 and 1. A value of 0
            means that the previous min/max value is completely overwritten with
            each observation.

    .. note::

        This observer is better suited than :class:`MinMaxObserver` for QAT,
        as the running min/max can shrink or grow with the observed tensor.

    .. note::

        This observer may not be well suited for sequantial models such
        as RNNs and Conv1Ds. Each time-step will result in a new observation,
        so the running min/max can change over the course of the input sequence.
        If the smoothing coefficient is small and the sequence is long, the
        running min/max may forget about large activations that were seen at the
        beginning of the sequence. This can be mitigated by setting alpha to a
        larger value.
    """

    def __init__(self, alpha=0.9):
        super().__init__()
        self.alpha = alpha

    @torch.no_grad()
    def update_statistics(self, x):
        x[torch.isinf(x)] = 0
        x[torch.isnan(x)] = 0
        curr_min = x.min()
        curr_max = x.max()
        if self.min_val.numel() == 0:
            self.min_val = curr_min
            self.max_val = curr_max
        else:
            self.min_val = self.alpha * self.min_val + (1 - self.alpha) * curr_min
            self.max_val = self.alpha * self.max_val + (1 - self.alpha) * curr_min


class FixedRangeObserver(MinMaxObserver):
    """
    A MinMaxObserver, with minimum and maximum limits. Used by default
    directly before saturating nonlinearities like tanh and sigmoid to
    restrict input tensors to the non-saturating range.

    .. warning::

        Users should not use FixedRangeObserver as the global default
        observer.
    """

    """
    hard_maximum -> whether to use asymmetric range [-128, 127] when optimizing
    quanta, or to approximate this with [-128, 128].
    """

    def __init__(self, limits, hard_maximum=True):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits
        self.hard_maximum = hard_maximum

    def _calculate_quanta(self, bits, verbose=False):
        r"""Calculates the optimal quanta given min and max
        value tensors.
        """
        lmin, lmax = self.limits
        if self.min_val.numel() == 0 or self.max_val.numel() == 0:
            raise ValueError("Empty observer!")

        min_val = torch.min(self.min_val, -torch.ones_like(self.min_val) * EPS)
        max_val = torch.max(self.max_val, torch.ones_like(self.max_val) * EPS)

        if lmin is not None:
            min_val = torch.max(min_val, torch.ones_like(min_val) * lmin)
        if lmax is not None:
            max_val = torch.min(max_val, torch.ones_like(max_val) * lmax)

        quanta_neg = torch.ceil(torch.log2(torch.abs(min_val)) + 1 - bits)
        if self.hard_maximum:
            quanta_pos = torch.ceil(
                torch.log2(torch.abs(max_val) / (2 ** (bits - 1) - 1))
            )
        else:
            quanta_pos = torch.ceil(torch.log2(torch.abs(max_val)) + 1 - bits)
        quanta = torch.max(quanta_neg, quanta_pos)
        return quanta

    def do_on_fp(self, x):
        if CONFIG.sim_fixed_range_fp:
            if (self.limits[0] is not None) or (self.limits[1] is not None):
                return torch.clamp(x, *self.limits)
            else:
                return x
        else:
            return x


class FixedRangeWrappedObserver(ObserverBase):
    """
    hard_maximum -> whether to use asymmetric range [-128, 127] when optimizing
    quanta, or to approximate this with [-128, 128].
    """

    def __init__(self, limits, wrapped, hard_maximum=True):
        super().__init__()
        self.observe = wrapped.observe
        self.limits = limits
        self.wrapped = wrapped
        self.hard_maximum = hard_maximum

    def reset(self):
        self.wrapped.reset()

    @torch.no_grad()
    def update_statistics(self, x):
        self.wrapped.update_statistics(x)

    def _calculate_quanta(self, bits, verbose=False):
        q_w = self.wrapped.calculate_quanta(bits, verbose=verbose)
        lmin, lmax = [
            torch.ones_like(q_w) * l if l is not None else None for l in self.limits
        ]
        vmin, vmax = -(2 ** (bits - 1 + q_w)), (2 ** (bits - 1) - 1) * 2**q_w
        under, over = False, False
        if lmin is not None:
            if vmin < lmin:
                vmin = lmin
        if lmax is not None:
            if vmax > lmax:
                vmax = lmax
        quanta_neg = torch.ceil(torch.log2(torch.abs(vmin)) + 1 - bits)
        if self.hard_maximum:
            quanta_pos = torch.ceil(torch.log2(torch.abs(vmax) / (2 ** (bits - 1) - 1)))
        else:
            quanta_pos = torch.ceil(torch.log2(torch.abs(vmax)) + 1 - bits)

        quanta = torch.max(quanta_neg, quanta_pos)
        return quanta

    def do_on_fp(self, x):
        if CONFIG.sim_fixed_range_fp:
            if (self.limits[0] is not None) or (self.limits[1] is not None):
                return torch.clamp(x, *self.limits)
            else:
                return x
        else:
            return x


class FixedQuantaObserver(ObserverBase):
    def __init__(self, quanta: int):
        super().__init__()
        assert isinstance(quanta, int)
        self.register_buffer("quanta", torch.tensor(quanta))

    def reset(self):
        pass

    def set_quanta(self, quanta: Tensor):
        self.quanta = quanta.detach()

    @torch.no_grad()
    def update_statistics(self, x):
        pass

    def _calculate_quanta(self, bits, verbose=False):
        return self.quanta

    @classmethod
    def from_limits(cls, min_val, max_val, bitwidth=16, i16_clipping_tolerance=2):
        """Create a FixedQuantaObserver from min/max range values.

        Designed to allow for a tiny amount of clipping in the case of i16
        audio
        """
        min_lim = -(2 ** (bitwidth - 1))
        max_lim = 2 ** (bitwidth - 1) - 1

        max_val = max(max_val, min_val)
        min_val = min(max_val, min_val)

        if min_val > 0:
            opt_scale = max_val / max_lim
        elif max_val < 0:
            opt_scale = min_val / min_lim
        else:
            opt_scale = max(max_val / max_lim, min_val / min_lim)

        opt_quanta = math.log2(opt_scale)
        ceil_quanta = math.ceil(opt_quanta)
        floor_quanta = math.floor(opt_quanta)

        if bitwidth <= 8:
            quanta = int(ceil_quanta)
        else:
            # for precisions higher than i8, allow for tiny amount of clipping,
            # by i16_clipping_tolerance
            opt_max = (2 ** (bitwidth - 1) - 1) * 2**opt_quanta
            flr_max = (2 ** (bitwidth - 1) - 1) * 2**floor_quanta
            flr_max_plus_tol = flr_max + i16_clipping_tolerance * 2**floor_quanta

            if opt_max < flr_max_plus_tol:
                quanta = int(floor_quanta)
            else:
                quanta = int(ceil_quanta)

        return cls(quanta=quanta)


class GaussianObserver(ObserverBase):
    """
    GaussianObserver fits a normal distribution to the observed tensor.
    Records a running mean and variance. The quanta is chosen to minimize
    the expected value of quantization mean squared error.

    Args:
        ignore_zero (bool): If :attr:`True`, inputs that are exactly equal
            to zero will not contribute to running mean and variance. This
            is especially helpful when the observed tensor is sparse, i.e. a
            pruned parameter matrix. Default is :attr:`True`.
        alpha (float): An optional smoothing coefficient, between 0 and 1.
            If :attr:`alpha` is not :attr:`None`, the running mean and variance
            will be updated as an exponential moving average instead of as
            global sums. Default is :attr:`None`.

    .. note::

        This Observer tends to have superior performance on aggressively quantized
        models (i.e. using :attr:`'standard'` precision).

    .. note::

        If a model is being fine-tuned with QAT, better performance may be obtained
        by using exponential moving average and variance. This can be done by setting
        :attr:`alpha` to a float between 0 and 1. If the model is sequential
        (i.e. RNN), it is recommended that :attr:`alpha` is close to :attr:`1`,
        for example :attr:`0.99`, to avoid mean and variance from drifting from
        time-step to time-step of a sequence.
    """

    def __init__(self, ignore_zero=True, alpha=None):
        super().__init__()
        self.observe = False
        self.ignore_zero = ignore_zero
        self.alpha = alpha
        self.reset()

    def reset(self):
        if hasattr(self, "N"):
            dev = self.N.device
        else:
            dev = None
        self.register_buffer("N", torch.tensor(0, dtype=torch.long, device=dev))
        self.register_buffer("running_x", torch.tensor(0.0, device=dev))
        self.register_buffer("running_x2", torch.tensor(0.0, device=dev))
        self.register_buffer("maxabs", torch.tensor(0.0, device=dev))

    @torch.no_grad()
    def update_statistics(self, x):
        if x.device != self.N.device:
            self.to(x.device)
        N = x.numel()
        if self.ignore_zero:
            N = int((x != 0).sum())
        curr_x = x.sum()
        curr_x2 = x.pow(2).sum()
        if self.alpha is None:
            self.N += N
            self.running_x += curr_x
            self.running_x2 += curr_x2
        else:
            self.N = self.N * self.alpha + N * (1 - self.alpha)
            self.running_x *= self.alpha
            self.running_x += curr_x * (1 - self.alpha)
            self.running_x2 *= self.alpha
            self.running_x2 += curr_x2 * (1 - self.alpha)
        self.maxabs = torch.max(self.maxabs, x.abs().max())

    def _calculate_quanta(self, bits, verbose=False):
        """Calculates the optimal quanta given a gaussian approximation
        to activation statistics"""
        if self.N == 0:
            raise Exception(f"Need to observe before quantizing {self}")
        mu = self.running_x / self.N
        E_x2 = self.running_x2 / self.N
        std = torch.sqrt(E_x2 - mu**2)
        dev = std.device

        # Initial guess based on largest magnitude activation
        qinit = torch.ceil(torch.log2(self.maxabs) + 1 - bits)

        data = torch.randn(1000, device=dev) * std + mu
        quantas = torch.arange(start=qinit - 5, end=qinit + 5, device=dev)
        mse_min = float("inf")
        qopt = None
        for q in quantas:
            qdata = fake_quantize(data, q, bits)
            mse = (data - qdata).pow(2).mean()
            if mse < mse_min:
                mse_min = mse
                qopt = q
        if qopt is None:
            qopt = qinit
            print(
                f"WARNING: GaussianObserver set qopt to None, qinit={qinit}, quantas={quantas}"
            )
        return qopt

    @staticmethod
    def truncation_error(bits, quanta, mu, sigma):
        r"""
        Trucation error is computed as an integral of the squared truncation
        error weighted by the guassian. The integral is only computed for the
        tails of the distribution -- above and below the max/min quantization
        levels.

            GTE = \integral_{A_{max}, \infty} p(x) (x-A_{max})^2 dx +
                \integral_{-\infty, A_{min}} p(x) (x-A_{min})^2 dx
        """
        A_max = (2 ** (bits - 1) - 1) * 2**quanta
        A_min = -(2 ** (bits - 1)) * 2**quanta

        def eta(A):
            return (A**2 - 2 * A * mu + mu**2 + sigma**2) / 2

        def delta(A):
            return sigma * (mu - A) / math.sqrt(2 * math.pi)

        def nerf(x):
            return torch.erf((x - mu) / (sigma * math.sqrt(2)))

        def gexp(x):
            return torch.exp(-((x - mu) ** 2) / (2 * sigma**2))

        max_tail = eta(A_max) * (1 - nerf(A_max)) + delta(A_max) * gexp(A_max)
        min_tail = eta(A_min) * (1 + nerf(A_min)) - delta(A_min) * gexp(A_min)
        return max_tail + min_tail

    @staticmethod
    def rounding_error(bits, quanta, mu, sigma):
        scale = 2**quanta
        A_max = (2 ** (bits - 1) - 1) * scale
        A_min = -(2 ** (bits - 1)) * scale

        def nerf(x):
            return torch.erf((x - mu) / (math.sqrt(2) * sigma))

        error = (scale**3) / 6 * (nerf(A_max) - nerf(A_min))
        return error

    @staticmethod
    def gaussian_error(bits, quanta, mu, sigma):
        e_trunc = GaussianObserver.truncation_error(bits, quanta, mu, sigma)
        e_round = GaussianObserver.rounding_error(bits, quanta, mu, sigma)
        return e_trunc + e_round


class DefObs:
    def __getitem__(self, key):
        if key == "default":
            return DefObs.get_obs(CONFIG.default_observer)
        elif key == "param":
            return DefObs.get_obs(CONFIG.param_observer)
        else:
            raise KeyError(f"Default for {key} not defined")

    @staticmethod
    def get_obs(key):
        if key in ["min_max", "minmax"]:
            return MinMaxObserver
        elif key == "gaussian":
            return GaussianObserver
        elif key == "moving_min_max":
            return MovingAverageMinMaxObserver
        elif key.startswith("quantile"):
            # expects "quantile99", "quantile80", etc.
            quantile = key.split("quantile")[1]
            try:
                quantile = float(quantile)
            except:
                raise ValueError(f"Quantile {quantile} could not be converted to float")
            assert 0 <= quantile <= 100
            quantile = quantile / 100
            return partial(QuantileMinMaxObserver, quantile=quantile)
        else:
            raise KeyError(f"Observer {key} not defined")


DEFAULT_OBSERVERS = DefObs()


class Quantizer(nn.Module):
    """
    Attributes:
        param: parameter associated to the quantizer (we assume
        that we can only have one to one correspondance)
    """

    def __init__(
        self,
        bitwidth,
        observer=DEFAULT_OBSERVERS["default"],
        rounded=False,
        dimensions=None,
        **observer_kwargs,
    ):
        super().__init__()
        assert isinstance(bitwidth, Bitwidth)
        self.bitwidth = bitwidth
        self.rounded = rounded
        self.dimensions = dimensions
        self.observer = observer(**observer_kwargs)
        self.quantize = False
        self.observe = False
        self.member_of = []
        self.param = None

        self.is_param_quantizer = False

    def forward(self, x):
        if isinstance(self.observer, FixedQuantaObserver):
            self.quantize = True

        if self.observe:
            self.observer.update_statistics(x)
        quanta = None
        if self.quantize:
            quanta = self.observer.calculate_quanta(self.bitwidth.bitwidth)
            self.prev_quanta = quanta

            if quanta is None:
                raise ValueError(f"Quanta was None! {self.observer}")
            y = copy_dim_annotations(
                x,
                fake_quantize(x, quanta, self.bitwidth.bitwidth, rounded=self.rounded),
            )
        else:
            y = self.observer.do_on_fp(x)
        try:
            dimensions = x.dimensions
        except:
            # warnings.warn(
            #     "Input dimensions are missing: "
            #     + "dimension information may not propagate correctly"
            # )
            dimensions = None
        y = annotate(y, self.bitwidth, quanta, self.quantize, dimensions=dimensions)
        return y

    def _observe(self, x):
        if self.observe:
            self.observer.update_statistics(x)

    def get_bits_quanta(self):
        bits = self.bitwidth.bitwidth
        quanta = self.observer.calculate_quanta(bits)
        return bits, quanta

    @torch.no_grad
    def update_statistics(self, x):
        if self.observe:
            self.observer(x)

    def _get_constants(self, x):
        constants = {}
        if self.quantize:
            constants["quanta"] = intitem(
                self.observer.calculate_quanta(self.bitwidth.bitwidth)
            )
            constants["bw"] = self.bitwidth.bitwidth
        return constants

    def update_bitwidth(self, bw_conf):
        for group in self.member_of:
            group.update_bitwidth(bw_conf)
        self._update_bitwidth(bw_conf)

    def _update_bitwidth(self, bw_conf):
        self.bitwidth = bw_conf.get_bitwidth(self.bitwidth.role)
        if self.param is not None:
            if len(self.param) != 0:
                self.param[0].bitwidth = self.bitwidth

    def assign_to_group(self, group):
        self.member_of.append(group)


class ParameterQuantizer(Quantizer):
    def __init__(
        self, bitwidth, observer=None, rounded=True, dimensions=None, **observer_kwargs
    ):
        if observer is None:
            observer = DEFAULT_OBSERVERS["param"]
        super().__init__(bitwidth, observer, rounded, dimensions)
        self.register_buffer("_cache", None)
        self._use_cache = False
        self.param = []

        self.is_param_quantizer = True

    @classmethod
    def _from_float(
        cls, parent, bw_conf, interpolate, observer=DEFAULT_OBSERVERS["param"], **kwargs
    ):
        observer = partial(observer, **kwargs)
        # TODO: can weights have more than 3 dimensions?
        if parent.is_weight:
            bw = bw_conf.weights
            dimensions = ["F", "F"]
        else:
            bw = bw_conf.activations
            dimensions = ["F"]
        return cls(bitwidth=bw, dimensions=dimensions, observer=observer)

    def forward(self, x):
        if self._use_cache:
            if self._cache is None:
                y = super().forward(set_dim_annotations(self.dimensions, x))
                self.param = [y]
                self.register_buffer("_cache", y)
            return self._cache
        else:
            y = super().forward(set_dim_annotations(self.dimensions, x))
            return y

    def cache(self):
        self.register_buffer("_cache", None)
        self._use_cache = True

    def decache(self):
        self.register_buffer("_cache", None)
        self._use_cache = False


class StateQuantizer(Quantizer):
    def __init__(
        self,
        bitwidth,
        observer=MinMaxObserver,
        rounded=True,
        dimensions=None,
        **observer_kwargs,
    ):
        super().__init__(bitwidth, observer, rounded, dimensions, **observer_kwargs)
        self.annos = {}

    @torch.no_grad
    def update_statistics(self, x):
        for anno in ["avg_sparsity", "prev_relu", "density_per_element"]:
            try:
                self.annos[anno] = getattr(x, anno)
            except:
                self.annos.pop(anno, None)
        if self.observe:
            self.observer(x)

    def forward(self, x):
        x = super().forward(x)
        for key, value in self.annos.items():
            setattr(x, key, value)
        return x


class PrecisionConstraint:
    """A container for multiple quantizers that must share the same precision

    Reduces the size of search space when performing mixed precision optimization.
    """

    def __init__(self):
        self.members = []
        self.module = None

    def add(self, member):
        assert isinstance(member, Quantizer)
        member.assign_to_group(self)
        self.members.append(member)

    def recursively_add(self, module):
        self.module = module
        for m in module.modules():
            if isinstance(m, Quantizer):
                self.add(m)

    def update_bitwidth(self, bw_conf):
        for member in self.members:
            member._update_bitwidth(bw_conf)


def _share_observer(*quantizers):
    """Induce multiple different quantizers to share the same observer

    Quantizers[1:] will all use the same observer as Quantizers[0].
    """
    obs = quantizers[0].observer
    for q in quantizers:
        q.observer = obs


def share_observer(*modules):
    all_observers = set()
    for m in modules:
        for mm in m.modules():
            if isinstance(mm, Quantizer):
                all_observers.add(mm)
    _share_observer(*all_observers)


def enable_quantization(model, quantize=True):
    for l in model.modules():
        if isinstance(l, Quantizer):
            l.quantize = quantize
    return model


def is_quantized(model):
    N = 0
    for l in model.modules():
        if isinstance(l, Quantizer):
            N += 1
            if not l.quantize:
                return False
    if N > 0:
        return True
    else:
        return False
