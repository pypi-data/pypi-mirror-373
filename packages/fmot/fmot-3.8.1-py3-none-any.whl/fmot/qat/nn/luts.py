from .atomics import *
from . import quantizers
from functools import partial, wraps
from fmot import CONFIG, ROUND_CONFIG
from fmot.qat.fake_quantization import fixed_range_fake_quantize, get_fixed_range_quanta
from typing import *
import torch


class MaskedRound(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor, mask: torch.BoolTensor):
        """
        Round x. Insert these rounded values where the mask is True,
        otherwise leave the unrounded values
        """
        rounded_x = torch.round(x)
        y = x.masked_fill(mask, 0) + rounded_x.masked_fill(torch.logical_not(mask), 0)
        return y

    @staticmethod
    def backward(ctx, grad_output):
        """
        Straight-through estimator. Ignore the impact of rounding
        on gradients.
        """
        return grad_output, None


def saturate_wrapper(function, lim_min, lim_max):
    @wraps(function)
    def wrapped(x):
        y = function(x)
        mask = torch.logical_or(x >= lim_max, x <= lim_min)
        y = MaskedRound.apply(y, mask)
        return y

    return wrapped


class LUT(nn.Module):
    def __init__(
        self,
        function,
        bitwidth,
        lut_bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits
        self.function = function
        self.input_requantizer = Requantize(
            bitwidth=lut_bitwidth,
            observer=quantizers.FixedRangeObserver,
            limits=self.limits,
        )
        self.lut = BareLUT(function, bitwidth, observer=observer)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    def forward(self, x):
        return self.lut(self.input_requantizer(x))

    def __repr__(self):
        return f"{self.function.__name__}LUT"

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        """
        Regardless of what observer is passed in, a FixedRangeObserver
        is always used.
        """
        observer = partial(observer, **kwargs)

        enabled_fast_ilut = CONFIG.fast_ilut

        if type(parent) == fmot.nn.LUT:
            # forced saturation at endpoints
            if parent.saturating and fmot.CONFIG.forced_endpoint_saturation:
                assert parent.limits is not None
                function = saturate_wrapper(
                    parent.function, parent.limits[0], parent.limits[1]
                )
                # enabled_fast_ilut = False
            else:
                function = parent.function

            kwargs = dict(
                function=function,
                lut_bitwidth=bw_conf.lut,
                bitwidth=bw_conf.activations,
                limits=parent.limits,
                observer=observer,
            )

            if bw_conf.activations == fqint16:
                if parent.telescope:
                    if CONFIG.telescope_interpolate:
                        return TILUT(**kwargs)
                    elif parent.add_identity:
                        return AddIdentityTLUT(**kwargs)
                    elif parent.mul_identity:
                        return MulIdentityTLUT(**kwargs)
                    elif parent.interpolate:
                        return TILUT(**kwargs)
                    else:
                        return TLUT(**kwargs)
                elif interpolate & parent.interpolate:
                    if enabled_fast_ilut and parent.allow_fast_ilut:
                        return FastILUT(**kwargs)
                    else:
                        return ILUT(**kwargs)
                else:
                    return cls(**kwargs)
            else:
                return cls(**kwargs)
        else:
            return cls(bitwidth=bw_conf.activations, lut_bitwidth=bw_conf.lut)


class ILUT(nn.Module):
    """
    Interpolating Lookup Table
    Technically a composite -- defined here to avoid circular imports
    """

    def __init__(
        self,
        function,
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits
        lim_obs = partial(
            quantizers.FixedRangeObserver, limits=limits, hard_maximum=True
        )
        if CONFIG.ilut_requant:
            self.requant = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_down = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_up = Requantize(bitwidth, observer=lim_obs)
        quantizers.share_observer(self.shift_up, self.shift_down)
        self.obs_in = self.shift_up.quantizer.observer
        self.add_one = VIAdd(0.0, lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.rem_muli = VIMul(1.0, bitwidth)
        self.mux_neg = Neg()
        self.mux_op = VIAdd(1.0, bitwidth)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)

        # Group all submodules into a single quantization group
        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        if CONFIG.ilut_requant:
            x = self.requant(x)
        if x.quantized:
            bw = self.shift_down.quantizer.bitwidth.bitwidth
            q_addr = self.obs_in.calculate_quanta(bw)
            self.add_one.imm.data = 2.0 ** (q_addr).detach()
            self.rem_muli.imm.data = 2.0 ** (-q_addr).detach()
        addr = copy_dim_annotations(x, self.shift_down(x))
        addr_p = self.add_one(addr)
        y0 = self.lut(addr)
        y1 = self.lut(addr_p)
        rem1 = self.rem_muli(self.rem_sub(x, self.shift_up(addr)))
        rem0 = self.mux_op(self.mux_neg(rem1))
        y = self.add(self.mul0(rem0, y0), self.mul1(rem1, y1))
        return y

    def to_simple_lut(self):
        kwargs = dict(
            function=self.lut.function,
            lut_bitwidth=self.shift_down.quantizer.bitwidth,
            bitwidth=self.shift_up.quantizer.bitwidth,
            limits=self.limits,
        )
        obs_in = self.shift_down.quantizer.observer
        obs_out = self.lut.quantizer.observer
        lut = LUT(**kwargs)
        lut.input_requantizer.quantizer.observer = obs_in
        lut.lut.quantizer.observer = obs_out

        quantizers.enable_quantization(lut, quantizers.is_quantized(self))
        return lut


class TLUT(nn.Module):
    """
    Telescoping Lookup Table -- technically a composite, defined here
    to avoid circular imports
    """

    def __init__(
        self,
        function,
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits

        lim_obs = partial(quantizers.FixedRangeObserver, limits=limits)
        self.shift_down = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.coarse_lut = BareLUT(function, bitwidth)
        self.fine_lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.not_neg = Neg()
        self.not_addi = VIAdd(1.0, lut_bitwidth)
        self.gate_shift = Shift(0, bitwidth)
        self.gt = Gt0(lut_bitwidth, pseudo_derivative=False)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        x = nan_grad_skip(x)

        addr = self.shift_down(x)
        y_coarse = self.coarse_lut(addr)
        rem = self.shift_rem(x)
        if x.quantized:
            y_fine = self.fine_lut(rem)
        else:
            y_fine = self.fine_lut(copy_annotations(x, x * 0))
        coarse = self.gt(addr)
        fine = self.not_addi(self.not_neg(coarse))
        coarse = self.gate_shift(coarse)
        fine = self.gate_shift(fine)
        y = self.add(self.mul0(coarse, y_coarse), self.mul1(fine, y_fine))

        if x.quantized:
            return y
        else:
            return y_coarse


class AddIdentityTLUT(nn.Module):
    """
    Telescoping Lookup Table; leveraging an additive identity

    Applicable when the following identity holds for all positive a, b:

    .. math::

        f(a * b) = f(a) + f(b)
    """

    def __init__(
        self,
        function,
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        self.function = function
        self.shift_down = Shift(0, lut_bitwidth)
        self.gt = Gt0(lut_bitwidth, pseudo_derivative=False)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.mul_alpha = VIMul(1.0, lut_bitwidth)
        self.is_small_neg = Neg()
        self.is_small_op = VIAdd(1.0, lut_bitwidth)
        self.mux_mul0 = VVMul(lut_bitwidth)
        self.mux_mul1 = VVMul(lut_bitwidth)
        self.mux_add = VVAdd(lut_bitwidth)
        self.is_small_shift = Shift(0, bitwidth)
        self.mul_falpha = VIMul(0.0, bitwidth)
        self.demixer = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        x = nan_grad_skip(x)
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        is_large = self.gt(addr)
        is_small = self.is_small_op(self.is_small_neg(is_large))
        rem = self.shift_rem(x)
        if x.quantized:
            alpha = 2 ** (addr.quanta - rem.quanta).detach()
            self.mul_alpha.imm.data = alpha
            self.mul_falpha.imm.data = -self.function(alpha).detach()
        rem = self.mul_alpha(rem)
        mixed_addr = self.mux_add(
            self.mux_mul0(addr, is_large), self.mux_mul1(rem, is_small)
        )
        mixed_y = self.lut(mixed_addr)
        to_add = self.mul_falpha(self.is_small_shift(is_small))
        unmixed_y = self.demixer(mixed_y, to_add)
        return unmixed_y


class MulIdentityTLUT(nn.Module):
    """
    Telescoping Lookup Table, leveraging a multiplicative identity

    Applicable when the following identity holds for all positive a, b:

    .. math::

        f(a * b) = f(a) * f(b)
    """

    def __init__(
        self,
        function,
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        self.function = function
        self.shift_down = Shift(0, lut_bitwidth)
        self.gt = Gt0(lut_bitwidth, pseudo_derivative=False)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.mul_alpha = VIMul(1.0, lut_bitwidth)
        self.is_small_neg = Neg()
        self.is_small_op = VIAdd(1.0, lut_bitwidth)
        self.mux_mul0 = VVMul(lut_bitwidth)
        self.mux_mul1 = VVMul(lut_bitwidth)
        self.mux_add = VVAdd(lut_bitwidth)
        self.is_small_shift = Shift(0, bitwidth)
        self.mul_falpha = VIMul(0.0, bitwidth)
        self.add_multipliers = VIAdd(1.0, bitwidth)
        self.demixer = VVMul(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        is_large = self.gt(addr)
        is_small = self.is_small_op(self.is_small_neg(is_large))
        rem = self.shift_rem(x)
        if x.quantized:
            alpha = 2 ** (addr.quanta - rem.quanta).detach()
            self.mul_alpha.imm.data = alpha
            self.mul_falpha.imm.data = 1 / self.function(alpha).detach() - 1
        rem = self.mul_alpha(rem)
        mixed_addr = self.mux_add(
            self.mux_mul0(addr, is_large), self.mux_mul1(rem, is_small)
        )
        mixed_addr = nan_grad_skip(mixed_addr)
        mixed_y = self.lut(mixed_addr)
        to_mul = self.add_multipliers(self.mul_falpha(self.is_small_shift(is_small)))
        unmixed_y = self.demixer(mixed_y, to_mul)
        return unmixed_y


class NanGradSkip(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, grad_fill=0):
        ctx.grad_fill = grad_fill
        return x

    @staticmethod
    def backward(ctx, grad_output):
        grad_fill = ctx.grad_fill
        grad_output = torch.masked_fill(
            grad_output, torch.isnan(grad_output), grad_fill
        )
        return grad_output, None


def nan_grad_skip(x):
    y = NanGradSkip.apply(x, 0)
    copy_annotations(x, y)
    if hasattr(x, "proto"):
        y.proto = x.proto
    return y


class TILUT(nn.Module):
    """
    Telescoping & Interpolating Lookup Table
    """

    def __init__(
        self,
        function,
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        self.shift_down = Shift(0, lut_bitwidth)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.coarse_lut = ILUT(function, lut_bitwidth, bitwidth, limits)
        self.fine_lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.not_neg = Neg()
        self.not_addi = VIAdd(1.0, lut_bitwidth)
        self.gate_shift = Shift(0, bitwidth)
        self.gt = Gt0(lut_bitwidth, pseudo_derivative=False)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        if x.quantized:
            x_coarse = nan_grad_skip(x)
        else:
            x_coarse = x
        y_coarse = self.coarse_lut(x_coarse)
        rem = nan_grad_skip(self.shift_rem(x))
        if x.quantized:
            y_fine = self.fine_lut(rem)
        else:
            y_fine = self.fine_lut(copy_annotations(x, x * 0))
        coarse = self.gt(addr)
        fine = self.not_addi(self.not_neg(coarse))
        coarse = self.gate_shift(coarse)
        fine = self.gate_shift(fine)
        y = self.add(self.mul0(coarse, y_coarse), self.mul1(fine, y_fine))
        if x.quantized:
            return y
        else:
            return y_coarse


"""
TODO: AddIdentity and MulIdentity TILUTs
"""


class RSqrtPlusEps(LUT):
    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        eps = parent.eps

        def rsqrt_peps(x):
            return torch.rsqrt(x + eps)

        config = fmot.LUTConfig(
            rsqrt_peps,
            limits=None,
            interpolate=fmot.LUT_REGISTRY["aten::reciprocal"].interpolate,
        )
        parent_obj = fmot.nn.LUT(config)
        return LUT._from_float(parent_obj, bw_conf, interpolate)


class PowFrac(LUT):
    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        power = parent.power

        def pow_frac(x):
            return torch.pow(x, power)

        if power > 1:
            config = fmot.LUTConfig(
                pow_frac,
                limits=None,
                interpolate=fmot.LUT_REGISTRY["aten::sqrt"].interpolate,
            )
        else:
            config = fmot.LUTConfig(
                pow_frac, limits=None, telescope=True, mul_identity=True
            )
        parent_obj = fmot.nn.LUT(config)
        return LUT._from_float(parent_obj, bw_conf, interpolate)


"""NEW: fast implementation of ILUT"""


class interpolating_lut(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        x: Tensor,
        c0: Tensor,
        c1: Tensor,
        addr_quanta: float,
        c1_quanta: float,
        addr_bits: int = 8,
        rounded: bool = False,
    ):
        scale = 2 ** (addr_quanta)

        neg_level = 2 ** (addr_bits - 1)  # 128 for bits = 8
        # this gives the correct clamp to match FQIR
        x = fixed_range_fake_quantize(x, addr_quanta - 8, 16, True)
        addr = torch.clamp(torch.floor(x / scale), -neg_level, neg_level - 1)
        int_addr = addr.long() + neg_level

        int_addr = torch.clamp(int_addr, 0, min(c0.shape[0], c1.shape[0]))

        f0 = c0[int_addr]
        f1 = c1[int_addr]

        delta = x - scale * addr
        y = f0 + fixed_range_fake_quantize(
            delta * f1, addr_quanta + c1_quanta, 16, True, rounded
        )

        ctx.save_for_backward(f1)
        return y

    @staticmethod
    def backward(ctx, grad_output):
        (f1,) = ctx.saved_tensors
        return grad_output * f1, None, None, None, None, None, None


class FastILUT(AtomicModule):
    def __init__(
        self,
        function: Callable[..., Tensor],
        lut_bitwidth,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        self.round_add = ROUND_CONFIG.fast_ilut_add
        self.round_mul = ROUND_CONFIG.fast_ilut_mul

        self.quantizer = quantizers.Quantizer(
            bitwidth,
            observer=observer,
            rounded=self.round_add,
        )
        self.function = function
        self.addr_bitwidth = lut_bitwidth.bitwidth
        self.output_bitwidth = bitwidth.bitwidth
        self.limits = limits
        self.quanta_in = None
        self.addr_quanta = None
        self.q0 = None
        self.q1 = None

    def get_addr_quanta(self, quanta_in):
        q_addr = quanta_in + self.output_bitwidth - self.addr_bitwidth
        if self.limits is not None:
            mv = max(abs(self.limits[0]), abs(self.limits[1]))
            q_cand = get_fixed_range_quanta(mv, self.addr_bitwidth)
            q_addr = min(q_cand, q_addr)
        return q_addr

    def set_tables(self, quanta_in: int, device=None):
        if isinstance(quanta_in, Tensor):
            quanta_in = quanta_in.detach().cpu().item()

        addr_quanta = self.get_addr_quanta(quanta_in)

        x = torch.arange(
            -(2 ** (self.addr_bitwidth - 1)),
            2 ** (self.addr_bitwidth - 1),
            device=device,
        )
        scale = 2**addr_quanta
        x = x * scale

        # simple secant method
        f_x = self.function(x)
        fp_x = (self.function(x + scale) - f_x) / scale

        f_x.masked_fill_(torch.isnan(f_x), 0)
        fp_x.masked_fill_(torch.isnan(fp_x), 0)

        q0 = get_fixed_range_quanta(torch.max(torch.abs(f_x)), self.output_bitwidth)
        q1 = get_fixed_range_quanta(torch.max(torch.abs(fp_x)), self.output_bitwidth)

        c0 = fixed_range_fake_quantize(f_x, q0, self.output_bitwidth, True, True)
        c1 = fixed_range_fake_quantize(fp_x, q1, self.output_bitwidth, True, True)

        self.register_buffer("c0", c0.to(device), persistent=True)
        self.register_buffer("c1", c1.to(device), persistent=True)

        self.addr_quanta = addr_quanta
        self.quanta_in = quanta_in
        self.q0 = q0
        self.q1 = q1

    @check_for_annotations
    def forward(self, x):
        if not x.quantized:
            y = self.function(x)
        else:
            if self.quanta_in is None or self.quanta_in != x.quanta:
                self.set_tables(x.quanta, x.device)

            x_q = fixed_range_fake_quantize(x, self.addr_quanta - 8, 16, True)
            y = interpolating_lut.apply(
                x_q,
                self.c0,
                self.c1,
                self.addr_quanta,
                self.q1,
                self.addr_bitwidth,
                self.round_mul,
            )

        y = self.quantizer(y)
        y = copy_dim_annotations(x, y)
        return y

    def _get_constants(self, x):
        return {
            "c0": (self.c0 / 2**self.q0).cpu().detach().numpy().astype(int),
            "c1": (self.c1 / 2**self.q1).cpu().detach().numpy().astype(int),
            "name": self.function.__name__,
            "q_c0": self.q0,
            "q_c1": self.q1,
            "q_addr": self.addr_quanta,
        }
