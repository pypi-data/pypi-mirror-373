"""
Defining the atomic operators. These operators are generally parameter-less,
instead taking as input activation/parameter tensors.
"""
from typing import List, Optional, Literal, Tuple
from functools import partial
import torch
from torch import nn, Tensor
import numpy as np
from copy import copy
from fmot.precisions import Precision, int8, int16, int24
import fmot
from fmot.nn.atomics import _compute_broadcast_shape
from fmot.nn.functional import temporal_conv2d, temporal_conv1d, temporal_unfold1d

from ..annotated_tensors import (
    check_for_annotations,
    copy_annotations,
    annotate,
    copy_dim_annotations,
    set_dim_annotations,
    get_dim_annotations,
    cast_float_annotated,
    asint,
    supports_int24,
    supports_int24,
)
from . import quantizers
from ..fake_quantization import fake_quantize
from ...nn import atomics as nn_atomics
from ._utils import intitem
from ..bitwidths import fqint4, fqint8, fqint16, fqint24, Bitwidth
import torch.nn.functional as F
from fmot.functional import _apply_varname
from fmot import CONFIG, ROUND_CONFIG
import logging

logger = logging.getLogger("fmot.qat.nn.atomics")
import logging

logger = logging.getLogger("fmot.qat.nn.atomics")


class AtomicModule(nn.Module):
    def __init__(self, round=False):
        super().__init__()
        self.quantize = False
        self.round = round

    @check_for_annotations
    def forward(self, *args):
        """
        All atomic modules should implement this
        """
        raise NotImplementedError

    def __repr__(self):
        inset = ""
        if hasattr(self, "_extra_repr"):
            inset += self._extra_repr
        if hasattr(self, "quantizer"):
            if len(inset) > 0:
                inset += ", "
            inset += f"bw={self.quantizer.bitwidth}"
        return f"Quant{type(self).__name__}({inset})"

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate, observer, **observer_kwargs):
        raise NotImplementedError

    def _get_constants(self, *args):
        return dict()


def get_time_dim(x: Tensor):
    if hasattr(x, "dimensions"):
        dims = x.dimensions
        if "T" in dims:
            return dims.index("T")
        else:
            return None

    else:
        return None


class DimensionalAtomicModule(AtomicModule):
    """Subclass of AtomicModule that adds some magic to `.dim` attribute
    to ensure that the dimension is properly updated during sequential tracing."""

    def __init__(self, dim: int, round: bool = False):
        super().__init__(round)
        self._dim = dim
        self.tracing_mode = False
        self.time_dim = None
        self.ndim = None
        self.built = False

    def _tracing_dim_filter(self, dim: int):
        if self.time_dim is not None:
            if dim < 0:
                dim = dim + self.ndim

            if self.time_dim == dim:
                raise ValueError(
                    "Cannot perform a dimensional operation along a temporal dimension!"
                )

            if dim > self.time_dim:
                dim = dim - 1

        return dim

    @property
    def dim(self):
        if not self.tracing_mode:
            return self._dim
        else:
            if isinstance(self._dim, int):
                return self._tracing_dim_filter(self._dim)
            elif isinstance(self._dim, (list, tuple)):
                dims = [self._tracing_dim_filter(d) for d in self._dim]
                dims = type(self._dim)(dims)
                return dims

    def update_dim_info(self, x: Tensor):
        if not self.built and not self.tracing_mode:
            self.time_dim = get_time_dim(x)
            self.ndim = x.ndim
            self.built = True


ACC_BW = 32


def transpose_dim(x, dim0, dim1):
    dimensions = list(x.dimensions)
    dimensions[dim0], dimensions[dim1] = dimensions[dim1], dimensions[dim0]
    x.__setattr__("dimensions", dimensions)
    return


######################################
"""
Addition Operators
"""


def _get_add_constants(x, y, z):
    """
    Get constants for expression:
    z = x + y

    shamt_x: (left) shift amount for operand x
    shamt_y: (left) shift amount for operand y
    shamt_bwred: (left) shift amount for output buffer when reducing bitwidth
    """
    constants = {}
    if all([w.quantized for w in [x, y, z]]):
        xq, yq, zq = x.quanta, y.quanta, z.quanta
        if CONFIG.lshift_qmax:
            q = torch.min(torch.as_tensor(xq), torch.as_tensor(yq))
        else:
            q = torch.max(torch.as_tensor(xq), torch.as_tensor(yq))
        constants["shamt_x"] = intitem(xq - q)
        constants["shamt_y"] = intitem(yq - q)
        constants["shamt_bwred"] = intitem(q - zq)
        constants["bw"] = z.bitwidth.bitwidth
        constants["bw_x"] = x.bitwidth.bitwidth
        constants["bw_y"] = y.bitwidth.bitwidth
    return constants


"""GENERALIZED MAC"""


class GMACv2(AtomicModule):
    def __init__(
        self,
        bits_out: Precision,
        scalar_multipliers: Optional[Tensor] = None,
        bits_headroom: int = 0,
    ):
        super().__init__(round=False)

        self.bits_out = bits_out

        bw = {8: fqint8, 16: fqint16, 24: fqint24}[bits_out.bitwidth]

        self.quantizer = quantizers.Quantizer(
            bitwidth=bw,
            observer=partial(quantizers.MinMaxObserver, bits_headroom=bits_headroom),
            rounded=False,
        )

        if scalar_multipliers is not None:
            self.register_buffer("scalar_multipliers_orig", scalar_multipliers)
            scalar_multipliers, scalar_quantas = self._quantize_multipliers(
                scalar_multipliers, bits_out.bitwidth
            )
            self.register_buffer("scalar_multipliers", scalar_multipliers)
            self.scalar_quantas = scalar_quantas
        else:
            self.scalar_multipliers = None
            self.scalar_quantas = None

        self._n_vv = None
        self._n_vi = None

    @torch.no_grad()
    def _quantize_multipliers(
        self, scalar_multipliers: Tensor, bits: int
    ) -> Tuple[Tensor, list[int]]:
        """Returns the quantized multipliers and quanta for each multiplier.
        Note that unlike typical quantization, here we quantize each multiplier independently
        """
        multipliers = []
        quantas = []
        for x in scalar_multipliers:
            if x != 0:
                q_opt = torch.ceil(torch.log2(x.abs())) + 1 - bits
            else:
                q_opt = 0
            x_quant = torch.round(x / 2**q_opt)
            if x_quant == 2 ** (bits - 1):
                x_quant = x_quant / 2
                q_opt += 1
            assert -(2 ** (bits - 1)) <= x_quant < 2 ** (bits - 1), f"{x_quant=}"
            x_quant = x_quant * 2**q_opt

            multipliers.append(x_quant)
            quantas.append(intitem(q_opt))
        multipliers = torch.stack(multipliers)
        return multipliers, quantas

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x_vv: List[Tensor], y_vv: List[Tensor], x_vi: List[Tensor]):
        assert len(x_vv) == len(y_vv)
        self._n_vv = len(x_vv)
        self._n_vi = len(x_vi)

        dimensions = get_dim_annotations(*x_vv, *y_vv, *x_vi)

        bshape = _compute_broadcast_shape([x.shape for x in x_vv + y_vv + x_vi])
        x_vv = list(map(lambda x: torch.broadcast_to(x, bshape), x_vv))
        y_vv = list(map(lambda x: torch.broadcast_to(x, bshape), y_vv))
        x_vi = list(map(lambda x: torch.broadcast_to(x, bshape), x_vi))

        if len(x_vv) > 0:
            x_vv = torch.stack(x_vv, dim=-1).double()
            y_vv = torch.stack(y_vv, dim=-1).double()

            z = torch.sum(x_vv * y_vv, -1)

        else:
            z = 0
            assert len(y_vv) == 0

        if self.scalar_multipliers is not None:
            assert len(x_vi) == len(self.scalar_multipliers)
            x_vi = torch.stack(x_vi, dim=-1).double()
            z += torch.sum(x_vi * self.scalar_multipliers, dim=-1)

        z = self.quantizer(z)
        z = set_dim_annotations(dimensions, z)
        z = cast_float_annotated(z)

        return z

    def _get_constants(
        self, x_vv: List[Tensor], y_vv: List[Tensor], x_vi: List[Tensor]
    ):
        logger.debug(
            f"tracing GMACv2 with {len(x_vv)=} {len(y_vv)=} {len(x_vi)=} {self.scalar_multipliers=} {self._n_vi=}"
        )
        z = self.forward(x_vv, y_vv, x_vi)
        quanta_out = z.quanta

        shamts_vv = []
        for x, y in zip(x_vv, y_vv):
            partial_quanta = x.quanta + y.quanta
            shamts_vv.append(intitem(partial_quanta - quanta_out))

        immediates_vi = []
        shamts_vi = []
        for i, x in enumerate(x_vi):
            q_imm = self.scalar_quantas[i]
            partial_quanta = x.quanta + q_imm
            imm = self.scalar_multipliers[i] / 2**q_imm

            shamts_vi.append(intitem(partial_quanta - quanta_out))
            immediates_vi.append(intitem(imm))

        return {
            "shamts_vv": shamts_vv,
            "shamts_vi": shamts_vi,
            "immediates_vi": immediates_vi,
            "bits_out": [
                self.bits_out.bitwidth,
            ],
        }

    def _getargnames(self):
        assert self._n_vv is not None
        assert self._n_vi is not None

        for i in range(self._n_vv):
            yield f"x_vv_{i}"
        for i in range(self._n_vv):
            yield f"y_vv_{i}"
        for i in range(self._n_vi):
            yield f"x_vi_{i}"

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(
            bits_out=parent.bits_out,
            scalar_multipliers=parent.scalar_multipliers,
            bits_headroom=parent.bits_headroom,
        )


class PrecisionSplit(AtomicModule):
    def __init__(self, bitwidths: list[int], precisions: list[int]):
        super().__init__(round=False)

        self.bitwidths = bitwidths
        self.precisions = []
        for prec in precisions:
            if prec == 8:
                self.precisions.append(fqint8)
            elif prec == 16:
                self.precisions.append(fqint16)
            else:
                raise ValueError(f"Invalid precision {prec}, not 8 or 16")

        # total bitwidth
        #  all lower subtensors will have an unused sign-bit,
        #  so we subtract these sign bits from the useable bitwidth
        self.total_bw = sum(bitwidths) - len(bitwidths) + 1

        self.num_outputs = len(self.bitwidths)

    def get_quanta_plan(self, bw_orig: int, quanta_orig: Tensor):
        """
        Defines a list of quantas for each of the subvectors, based on
        information about the input bitwidth and quanta
        """

        # set the quanta for the highest output (msb) so that
        # the dynamic range is matched.
        #   x_orig_max = 2**(bw_orig - 1 + quanta_orig)
        #   x_hi_max = 2**(bw_hi - 1 + quanta_hi)
        # therefore, need quanta_hi = bw_orig - bw_hi + quanta_orig

        quanta_hi = bw_orig + quanta_orig.clone() - self.bitwidths[-1]

        # fill out the quantas in reverse order:
        quantas = [quanta_hi]
        curr_q = quanta_hi
        for bw in self.bitwidths[:-1][::-1]:
            curr_q = curr_q.clone() - bw + 1
            quantas += [curr_q]
        return quantas[::-1]

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x: Tensor) -> list[Tensor]:
        # come up with a plan for the quantas
        if x.quantized:
            quanta_orig = x.quanta
            bw_orig = x.bitwidth.bitwidth
            quantas = self.get_quanta_plan(bw_orig, quanta_orig)
        else:
            quantas = [None] * self.num_outputs

        # build the output in reverse order (from msbs to lsbs)
        x_curr = x.double()
        outputs_rev = []
        for i in list(range(self.num_outputs))[::-1]:
            bw = self.bitwidths[i]
            prec = self.precisions[i]
            quanta = quantas[i]
            if quanta is not None:
                curr = fake_quantize(x_curr, quanta, bw, rounded=False)
            else:
                curr = x_curr

            curr = annotate(
                curr,
                bitwidth=prec,
                quanta=quanta,
                quantized=quanta is not None,
                dimensions=x.dimensions,
            )
            x_curr = x_curr - curr
            curr = cast_float_annotated(curr)
            outputs_rev.append(curr)

        return outputs_rev[::-1]

    def _get_constants(self, x: Tensor):
        return {
            "shamts_vv": [],
            "shamts_vi": [self.total_bw - x.bitwidth.bitwidth],
            "immediates_vi": [1],
            "bits_out": self.bitwidths,
        }

    def _getargnames(self):
        yield "x_vi_0"

    @classmethod
    def _from_float(
        cls,
        parent,
        **kwargs,
    ):
        return cls(bitwidths=parent.bws, precisions=parent.precisions)


class VVAdd(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=ROUND_CONFIG.vvadd)
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        if self.quantize:
            try:
                xq, yq = x.quanta, y.quanta
            except:
                print(f"{hasattr(x, 'quanta')=}, {hasattr(y, 'quanta')=}")
                raise

            if xq is not None and yq is not None:
                if CONFIG.lshift_qmax:
                    q = torch.min(torch.as_tensor(xq), torch.as_tensor(yq))
                else:
                    q = torch.max(torch.as_tensor(xq), torch.as_tensor(yq))

                y = fake_quantize(y, q, ACC_BW, rounded=False)
                x = fake_quantize(x, q, ACC_BW, rounded=False)
        return self.quantizer(set_dim_annotations(dimensions, x + y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        constants = _get_add_constants(x, y, z)
        constants.update({"rounded": self.round})
        return constants


class VIAdd(AtomicModule):
    def __init__(self, imm, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=ROUND_CONFIG.viadd)
        if isinstance(imm, torch.Tensor):
            imm = imm.clone().detach()
        else:
            imm = torch.tensor(imm)
        self.imm = nn.Parameter(imm, requires_grad=False)
        self.imm_quantizer = quantizers.ParameterQuantizer(bitwidth)
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        dimensions = get_dim_annotations(x)
        device = x.device
        y = self.imm_quantizer(copy_dim_annotations(x, self.imm.to(device)))
        if self.quantize:
            xq, yq = x.quanta, y.quanta
            if xq is not None and yq is not None:
                _, zq = self.quantizer.get_bits_quanta()
                if CONFIG.lshift_qmax:
                    q = torch.min(torch.as_tensor(xq), torch.as_tensor(yq))
                else:
                    q = torch.max(torch.as_tensor(xq), torch.as_tensor(yq))
                y = fake_quantize(y, q, y.bitwidth.bitwidth, rounded=False)
                x = fake_quantize(x, q, x.bitwidth.bitwidth, rounded=False)
        return self.quantizer(set_dim_annotations(dimensions, x + y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(imm=parent.imm, bitwidth=bw_conf.activations, observer=observer)

    @property
    def _extra_repr(self):
        return f"imm={self.imm.item():.3f}"

    def _get_constants(self, x):
        y = self.imm_quantizer(self.imm)
        z = self.forward(x)
        constants = _get_add_constants(x, y, z)
        if y.quantized:
            constants["y"] = asint(y).cpu().item()
        constants["rounded"] = self.round
        return constants


class VVSub(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=ROUND_CONFIG.vvadd)
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        if self.quantize:
            xq, yq = x.quanta, y.quanta
            if xq is not None and yq is not None:
                if CONFIG.lshift_qmax:
                    q = torch.min(torch.as_tensor(xq), torch.as_tensor(yq))
                else:
                    q = torch.max(torch.as_tensor(xq), torch.as_tensor(yq))
                x, y = tuple(
                    fake_quantize(arg, q, ACC_BW, rounded=False) for arg in (x, y)
                )
        return self.quantizer(set_dim_annotations(dimensions, x - y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        constants = _get_add_constants(x, y, z)
        constants["rounded"] = self.round
        return constants


class Neg(AtomicModule):
    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        y = -x
        if x.quanta is not None:
            y = fake_quantize(y, x.quanta, x.bitwidth.bitwidth, rounded=self.round)
        copy_annotations(x, y)
        y.avg_sparsity = 0.0
        y.density_per_element = None
        y.prev_relu = False
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls()

    def _get_constants(self, x):
        constants = {}
        if x.quantized:
            constants["bw"] = x.bitwidth.bitwidth
        return constants


#######################################
"""
Multiply Operators
"""


def _get_mul_constants(x, y, z):
    constants = {}

    xq, yq, zq = [w.quanta for w in [x, y, z]]
    if all(q is not None for q in [xq, yq, zq]):
        buffer_quanta = xq + yq
        constants["shamt_bwred"] = intitem(buffer_quanta - zq)
        constants["bw"] = z.bitwidth.bitwidth
    else:
        raise ValueError(
            f"Error in _get_mul_constants: not all inputs had non-None quanta:\n"
            f"{x.quanta=} {y.quanta=} {z.quanta=}\n"
            f"{x.shape=} {y.shape=} {z.shape=}"
        )
    return constants


class VVMul(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=ROUND_CONFIG.vvmul)
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        return self.quantizer(set_dim_annotations(dimensions, x * y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        constants = _get_mul_constants(x, y, z)
        constants.update({"rounded": self.round})
        return constants


class VIMul(AtomicModule):
    def __init__(self, imm, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=ROUND_CONFIG.vimul)
        if isinstance(imm, torch.Tensor):
            imm = imm.clone().detach()
        else:
            imm = torch.tensor(imm)
        self.imm = nn.Parameter(imm, requires_grad=False)
        self.imm_quantizer = quantizers.ParameterQuantizer(
            bitwidth, observer=quantizers.MinMaxObserver
        )
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        device = x.device
        y = self.imm_quantizer(copy_dim_annotations(x, self.imm.to(device)))
        return self.quantizer(copy_dim_annotations(x, x * y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(imm=parent.imm, bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        z = self.forward(x)
        y = self.imm_quantizer(self.imm)
        constants = _get_mul_constants(x, y, z)
        if y.quantized:
            constants["y"] = asint(y).cpu().item()
        constants["rounded"] = self.round
        return constants


def is_sparse(*tensors):
    return [x.avg_sparsity != 0 for x in tensors]


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


####################################
"""
Reduction
"""


class Sum(DimensionalAtomicModule):
    def __init__(
        self, dim, keepdim, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]
    ):
        super().__init__(dim=dim, round=False)
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )
        self.keepdim = keepdim
        if not keepdim:
            raise ValueError("Sum with keepdim=False not supported at this time")

    @check_for_annotations
    @supports_int24(False, reason="int24 inputs not supported in Sum at this time")
    def forward(self, x):
        self.update_dim_info(x)
        y = torch.sum(x, dim=self.dim, keepdim=self.keepdim)
        y = self.quantizer(copy_dim_annotations(x, y))
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(
            dim=parent.dim,
            keepdim=parent.keepdim,
            bitwidth=bw_conf.activations,
            observer=observer,
        )

    def _get_constants(self, x):
        dim = self.dim
        if isinstance(dim, list):
            dim = tuple(dim)
        constants = {"dim": dim, "keepdim": self.keepdim}
        y = self.forward(x)
        if x.quantized and y.quantized:
            xq, yq = x.quanta, y.quanta
            constants["shamt_bwred"] = intitem(xq - yq)
            constants["bw"] = y.bitwidth.bitwidth
        return constants

    @property
    def _extra_repr(self):
        return f"dim={self.dim}"


####################################
"""
Activation Functions
"""


class ReLU(AtomicModule):
    def __init__(self, alpha=0.95):
        super().__init__(round=False)
        self.alpha = alpha
        self.register_buffer("avg_sparsity", None)
        # self.register_buffer('density_per_element', None)

    @torch.no_grad()
    def update_sparsity(self, x):
        if x.dimensions is not None:
            f_dim = x.dimensions.index("F")
            dims = list(range(x.ndim))
            dims.remove(f_dim)
            density_per_element = (x != 0).float().mean(dims)
            sparsity = 1 - density_per_element.mean()
            if self.avg_sparsity is None:
                self.avg_sparsity = sparsity
                self.density_per_element = density_per_element
            else:
                self.avg_sparsity = ReLU._lpf_update(
                    self.alpha, self.avg_sparsity, sparsity
                )
                # self.density_per_element = ReLU._lpf_update(
                #     self.alpha, self.density_per_element, density_per_element)
        else:
            sparsity = (x == 0).float().mean()
            if self.avg_sparsity is None:
                self.avg_sparsity = sparsity
            else:
                self.avg_sparsity = ReLU._lpf_update(
                    self.alpha, self.avg_sparsity, sparsity
                )

    @staticmethod
    def _lpf_update(s, old, new):
        return s * old + (1 - s) * new

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        y = x.relu()
        y.dimensions = x.dimensions
        self.update_sparsity(y)
        y = copy_annotations(x, y)
        y.avg_sparsity = self.avg_sparsity
        y.density_per_element = None
        y.prev_relu = True
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls()

    def __repr__(self):
        repr = super().__repr__()
        if self.avg_sparsity is not None:
            repr += " (Act. Sparsity: {:.0f}%)".format(self.avg_sparsity * 100)

        return repr


class Identity(AtomicModule):
    @check_for_annotations
    @supports_int24(True)
    def forward(self, x):
        return x

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls()


class TagVarname(AtomicModule):
    def __init__(self, varname: str):
        super().__init__()
        self.varname = varname

    @check_for_annotations
    def forward(self, x):
        return _apply_varname(x, self.varname)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(parent.varname)


class OnesLike(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__(round=False)
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        y = torch.ones_like(x)
        return self.quantizer(copy_dim_annotations(x, y))

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        y = self.forward(x)
        constants = {}
        if x.quantized:
            constants = {"imm": asint(y).flatten()[0].cpu().item()}
        return constants


class Table:
    def __init__(self, x, y, name):
        assert len(x) == len(y)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        self.name = name
        self.x = x
        self.y = y
        self.N = len(self.x)

    def __eq__(self, other):
        assert isinstance(other, Table)
        if self.N == other.N:
            return np.all(self.y == other.y)
        else:
            return False

    def __lt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.name < other.name

    def __gt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.name > other.name

    def __repr__(self):
        return f"<{self.name}>"


class BareLUT(AtomicModule):
    def __init__(
        self,
        function,
        bitwidth,
        limits=None,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__(round=False)
        self.function = function
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        if x.quantized:
            assert x.bitwidth == fqint8
        y = self.function(x)
        return self.quantizer(copy_dim_annotations(x, y))

    def get_table(self, x):
        bits, quanta = x.bitwidth.bitwidth, x.quanta
        levels = 2**bits
        min_x = -(2 ** (bits + quanta - 1))
        max_x = (2 ** (bits - 1) - 1) * 2**quanta
        y = torch.linspace(min_x, max_x, levels, device=x.device)
        y = self.quantizer(copy_dim_annotations(x, self.function(y)))
        x_int = np.linspace(-levels // 2, levels // 2 - 1, levels, dtype=int)
        y_int = asint(y).cpu().numpy()
        return Table(x=x_int, y=y_int, name=self.function.__name__)

    def _get_constants(self, x):
        constants = {}
        if x.quantized:
            constants["shamt_address"] = 0
            constants["bw_address"] = 8
            constants["table"] = self.get_table(x)
        constants["function"] = self.function.__name__
        return constants


####################
"""
Tensor slicing and joining
"""


class Chunk(DimensionalAtomicModule):
    def __init__(self, chunks, dim=0):
        super().__init__(round=False, dim=dim)
        self.chunks = chunks

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x: Tensor):
        self.update_dim_info(x)
        z = torch.chunk(x, self.chunks, self.dim)
        return [copy_annotations(x, zz) for zz in z]

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(chunks=parent.chunks, dim=parent.dim)

    def _get_constants(self, x):
        return {"chunks": self.chunks, "dim": self.dim}

    @property
    def _extra_repr(self):
        return f"chunks={self.chunks}, dim={self.dim}"


class Split(DimensionalAtomicModule):
    def __init__(self, split_sizes: List[int], dim=0):
        super().__init__(round=False, dim=dim)
        self.split_sizes = split_sizes

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x):
        self.update_dim_info(x)
        z = torch.split(x, self.split_sizes, self.dim)
        return [copy_annotations(x, zz + 0) for zz in z]

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(split_sizes=parent.split_sizes, dim=parent.dim)

    def _get_constants(self, x):
        return {"lengths": self.split_sizes, "dim": self.dim}

    @property
    def _extra_repr(self):
        return f"split_sizes={self.split_sizes}, dim={self.dim}"


class BareCat(DimensionalAtomicModule):
    def __init__(self, dim=0):
        super().__init__(round=False, dim=dim)

    @check_for_annotations
    @supports_int24(True)
    def forward(self, *tensors):
        self.update_dim_info(tensors[0])
        z = torch.cat(tensors, self.dim)
        return copy_annotations(tensors[0], z)

    def _get_constants(self, *x):
        return {"dim": self.dim}

    def _getargnames(self):
        i = 0
        while True:
            yield f"x{i}"
            i += 1


class Cat(nn.Module):
    def __init__(self, dim, bitwidth, observer):
        super().__init__()
        self.cat = BareCat(dim)
        self.requantizers = nn.ModuleList()
        self.q_group = quantizers.PrecisionConstraint()
        self._built = False
        self._obs = observer
        self._bw = bitwidth

    def _build(self, N):
        for __ in range(N):
            req = Requantize(self._bw, self._obs)
            self.requantizers.append(req)
            self.q_group.recursively_add(req)
        quantizers.share_observer(self.requantizers)
        self._built = True

    @check_for_annotations
    @supports_int24(True)
    def forward(self, tensors):
        if not self._built:
            N = len(tensors)
            self._build(N)
        new_tensors = [req(t) for req, t in zip(self.requantizers, tensors)]
        return self.cat(*new_tensors)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(dim=parent.dim, bitwidth=bw_conf.activations, observer=observer)


class Stack(AtomicModule):
    def __init__(self, dim=0):
        super().__init__(round=False)
        self.dim = dim

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, tensors: List[Tensor]):
        t0 = tensors[0]
        if t0.quantized:
            assert all(
                [t.quanta == t0.quanta for t in tensors]
            ), "Cannot concatenate tensors with different quanta"
        z = torch.stack(tensors, self.dim)
        return copy_annotations(tensors[0], z)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(dim=parent.dim)

    def _get_constants(self, x):
        return {"dim": self.dim}

    @property
    def _extra_repr(self):
        return f"dim={self.dim}"

    def _getargnames(self):
        i = 0
        while True:
            yield f"x{i}"
            i += 1


class Transpose(AtomicModule):
    """
    Performs a transpose on a matrix.
    """

    def __init__(self):
        super().__init__(round=False)

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        z = x.t()
        return copy_annotations(x, z)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls()

    def _get_constants(self, x):
        return {"dim0": 0, "dim1": 1}


class Reshape(AtomicModule):
    """
    Performs a transpose on a matrix.
    """

    def __init__(self, shape):
        super().__init__(round=False)
        self.shape = shape

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        z = torch.reshape(x, self.shape)
        return copy_annotations(x, z)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(parent.shape)

    def _get_constants(self, x):
        return {"shape": self.shape}


"""
Requantize
"""


class Requantize(AtomicModule):
    def __init__(
        self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"], **kwargs
    ):
        super().__init__(round=ROUND_CONFIG.vshift)
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer, **kwargs)

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x):
        if hasattr(x, "prev_relu"):
            prev_relu = x.prev_relu
        else:
            prev_relu = False
        if hasattr(x, "avg_sparsity"):
            avg_sparsity = x.avg_sparsity
        else:
            avg_sparsity = 0.0
        x_clone = x + 0
        copy_annotations(x, x_clone)
        y = self.quantizer(x_clone)
        y.avg_sparsity = avg_sparsity
        y.prev_relu = prev_relu
        y.density_per_element = x.density_per_element
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        y = self.forward(x)
        try:
            constants = {
                "shamt": intitem(x.quanta - y.quanta),
                "bw": y.bitwidth.bitwidth,
            }
        except:
            raise Exception(
                f"Requantize failed to get constants for input of shape {x.shape}"
            )
        constants["rounded"] = self.round
        return constants


class RecursiveStateHandler(Requantize):
    def observe(self, x):
        self.quantizer.bitwidth = x.bitwidth
        self.quantizer.observer.update_statistics(x)


class RequantizeFromBitwidthQuanta(AtomicModule):
    """Performs requantization with a known bitwidth and quanta (passed in to forward)"""

    def __init__(self):
        super().__init__(round=False)

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x: Tensor, bitwidth: Bitwidth, quanta: float):
        if x.quantized:
            y = fake_quantize(
                x, quanta=quanta, bits=bitwidth.bitwidth, rounded=self.round
            )
            y = annotate(y, bitwidth=bitwidth, quanta=quanta, quantized=x.quantized)
        else:
            y = x + 0
            y = copy_annotations(x, y)
            if hasattr(x, "proto"):
                y.proto = x.proto
        return y

    def _get_constants(self, x, bitwidth, quanta):
        y = self.forward(x, bitwidth, quanta)
        constants = {"shamt": intitem(x.quanta - y.quanta), "bw": y.bitwidth.bitwidth}
        constants["rounded"] = self.round
        return constants


class Shift(AtomicModule):
    def __init__(self, shamt, bitwidth):
        super().__init__(round=ROUND_CONFIG.vshift)
        self.shamt = shamt
        self.bitwidth = bitwidth

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x):
        prev_relu = x.prev_relu
        quanta = x.quanta
        avg_sparsity = x.avg_sparsity
        density_per_element = x.density_per_element
        if self.quantize:
            quanta = quanta - self.shamt
            y = fake_quantize(x, quanta, self.bitwidth.bitwidth, rounded=self.round)
        else:
            mv = torch.max(torch.abs(x))
            mvq = torch.ceil(torch.log2(mv))
            mv = 2.0**mvq
            y = torch.clamp(x, -mv * 2**-self.shamt, mv * 2**-self.shamt)
        y = annotate(
            y,
            bitwidth=self.bitwidth,
            quanta=quanta,
            quantized=True,
            avg_sparsity=avg_sparsity,
            density_per_element=density_per_element,
            prev_relu=prev_relu,
        )
        copy_dim_annotations(x, y)
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(shamt=parent.shamt, bitwidth=bw_conf.activations)

    def _get_constants(self, x):
        constants = {"shamt": self.shamt, "bw": self.bitwidth.bitwidth}
        constants["rounded"] = self.round
        return constants


class Gt0(AtomicModule):
    def __init__(self, bitwidth, pseudo_derivative=True):
        super().__init__(round=False)
        self.bitwidth = bitwidth
        self.pseudo_derivative = pseudo_derivative

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        quanta = x.quanta
        quantized = x.quantized
        avg_sparsity = x.avg_sparsity
        if not self.pseudo_derivative:
            x = x.detach()
        y = nn_atomics._diffable_gt0.apply(x)
        if self.quantize:
            quanta = quanta * 0
        y = annotate(
            y,
            bitwidth=self.bitwidth,
            quanta=quanta,
            quantized=quantized,
            avg_sparsity=avg_sparsity,
            prev_relu=True,
        )
        copy_dim_annotations(x, y)
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(
            bitwidth=bw_conf.activations, pseudo_derivative=parent.pseudo_derivative
        )

    def _get_constants(self, x):
        return {"bw": self.bitwidth.bitwidth}


class FTranspose(AtomicModule):
    """
    Performs a functional transpose on a matrix.
    """

    def __init__(self, dim0, dim1):
        super().__init__(round=False)
        self.dim0 = dim0
        self.dim1 = dim1
        self.tracing_mode = False

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        # In tracing mode, we assume that we only have an input of shape
        # (batch_size, feature_size)
        if self.tracing_mode:
            z = x
        else:
            dimensions = list(x.dimensions)
            used_dims = set([dimensions[self.dim0], dimensions[self.dim1]])
            if used_dims == {"B", "F"}:
                raise Exception(
                    f"We don't support Batch-Feature dimension swap. {dimensions=} {used_dims=}"
                )
            z = torch.transpose(x, self.dim0, self.dim1)
            z = copy_annotations(x, z)
            transpose_dim(z, self.dim0, self.dim1)
        return z

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(parent.dim0, parent.dim1)

    def _get_constants(self, x):
        return {"dim0": self.dim0, "dim1": self.dim1}


class Permute(AtomicModule):
    """
    Performs a permutation on a tensor.
    """

    def __init__(self, dims):
        super().__init__(round=False)
        self.dims = dims
        self.tracing_mode = False

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        # In tracing mode, we assume that we only have an input of shape
        # (batch_size, feature_size)
        if self.tracing_mode:
            z = x
        else:
            dimensions = x.dimensions
            if set([dimensions[self.dim0], dimensions[self.dim1]]) == {"B", "F"}:
                raise Exception("We don't support Batch-Feature dimension swap")
            z = torch.transpose(x, self.dim0, self.dim1)
            z = copy_annotations(x, z)
            transpose_dim(z, self.dim0, self.dim1)
        return z

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(parent.dim0, parent.dim1)

    def _get_constants(self, x):
        return {"dim0": self.dim0, "dim1": self.dim1}


class Dropout(AtomicModule):
    def __init__(self, p, training, inplace):
        super().__init__(round=False)
        self.p = p
        self.training = training
        self.inplace = inplace

    @check_for_annotations
    @supports_int24(True)
    def forward(self, x):
        if self.training:
            device = x.device
            mask = torch.bernoulli(torch.zeros(x.shape) + (1 - self.p)).to(device)
            z = mask * x / (1 - self.p)
            return copy_annotations(x, z)
        else:
            return x

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(p=parent.p, training=parent.training, inplace=parent.inplace)


class Squeeze(AtomicModule):
    def __init__(self, dim):
        super().__init__(round=False)
        self.dim = dim

    @check_for_annotations
    @supports_int24(False, reason="Only GMACv2 supports int24 inputs at this time")
    def forward(self, x):
        y = x.squeeze(self.dim)
        y = copy_annotations(x, y)
        dims = copy(get_dim_annotations(x))
        if dims is not None:
            del dims[self.dim]
            set_dim_annotations(dims, y)
        return y

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(parent.dim)

    def _get_constants(self, x):
        return {"dim": self.dim}


"""Conv2d"""


class F_TemporalConv2d(AtomicModule):
    def __init__(
        self,
        bitwidth,
        d_band_in: int,
        n_band_in: int,
        d_band_out: int,
        kernel_t: int,
        kernel_band: int,
        dilation_t: int = 1,
        dilation_band: int = 1,
        padding_band: int = 0,
        stride_band: int = 1,
        stride_t: int = 1,
        groups: int = 1,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__(round=False)
        self.d_band_in = d_band_in
        self.n_band_in = n_band_in
        self.d_band_out = d_band_out
        self.kernel_t = kernel_t
        self.kernel_band = kernel_band
        self.dilation_t = dilation_t
        self.dilation_band = dilation_band
        self.padding_band = padding_band
        self.stride_band = stride_band
        self.stride_t = stride_t
        self.groups = groups

        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)
        self.tracing = False

    @check_for_annotations
    @supports_int24(False, reason="TemporalConv2d does not support int24 activations")
    def forward(self, input, weight, bias):
        if not self.tracing:
            output = temporal_conv2d(
                input,
                weight,
                dilation_t=self.dilation_t,
                dilation_band=self.dilation_band,
                padding_band=self.padding_band,
                stride_band=self.stride_band,
                stride_t=self.stride_t,
                bias=bias,
                groups=self.groups,
            )
        else:
            raise ValueError("Tracing...")
        output = self.quantizer(copy_dim_annotations(input, output))
        return output

    def _get_constants(self, input, weight, bias):
        z = self.forward(input, weight, bias)

        buffer_quanta = input.quanta + weight.quanta
        if bias is not None:
            shamt_bias = intitem(bias.quanta - buffer_quanta)
        else:
            shamt_bias = 0

        constants = {}
        constants.update(_get_mul_constants(input, weight, z))
        constants["shamt_bias"] = shamt_bias
        constants["kernel_size_t"] = self.kernel_t
        constants["kernel_size_band"] = self.kernel_band
        constants["d_band_in"] = self.d_band_in
        constants["n_band_in"] = self.n_band_in
        constants["dilation_t"] = self.dilation_t
        constants["dilation_band"] = self.dilation_band
        constants["padding_band"] = self.padding_band
        constants["stride_band"] = self.stride_band
        constants["groups"] = self.groups

        return constants


class TemporalConv2d(nn.Module):
    def __init__(
        self,
        bitwidth_act,
        bitwidth_weight,
        d_band_in: int,
        n_band_in: int,
        d_band_out: int,
        kernel_t: int,
        kernel_band: int,
        dilation_t: int = 1,
        dilation_band: int = 1,
        padding_band: int = 0,
        stride_band: int = 1,
        stride_t: int = 1,
        bias: bool = False,
        groups: int = 1,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()

        self.d_band_in = d_band_in
        self.n_band_in = n_band_in
        self.d_band_out = d_band_out
        self.kernel_t = kernel_t
        self.kernel_band = kernel_band
        self.dilation_t = dilation_t
        self.dilation_band = dilation_band
        self.padding_band = padding_band
        self.stride_band = stride_band
        self.stride_t = stride_t
        self.has_bias = bias
        self.groups = groups

        self.weight = nn.Parameter(
            torch.empty(d_band_out, d_band_in // groups, kernel_band, kernel_t)
        )
        self.quant_weight = quantizers.ParameterQuantizer(bitwidth_weight, observer)
        if bias:
            self.quant_bias = quantizers.ParameterQuantizer(bitwidth_act, observer)
            self.bias = nn.Parameter(torch.empty(d_band_out))
        else:
            self.bias = None

        self.conv = F_TemporalConv2d(
            bitwidth_act,
            d_band_in,
            n_band_in,
            d_band_out,
            kernel_t,
            kernel_band,
            dilation_t,
            dilation_band,
            padding_band,
            stride_band,
            stride_t,
            groups,
            observer,
        )

    def forward(self, x):
        weight = self.quant_weight(self.weight)
        if self.has_bias:
            bias = self.quant_bias(self.bias)
        else:
            bias = None

        output = self.conv(x, weight, bias)
        return output

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)

        layer = cls(
            bitwidth_act=bw_conf.activations,
            bitwidth_weight=bw_conf.weights,
            observer=observer,
            d_band_in=parent.d_band_in,
            n_band_in=parent.n_band_in,
            d_band_out=parent.d_band_out,
            kernel_t=parent.kernel_t,
            kernel_band=parent.kernel_band,
            dilation_t=parent.dilation_t,
            dilation_band=parent.dilation_band,
            padding_band=parent.padding_band,
            stride_band=parent.stride_band,
            stride_t=parent.stride_t,
            bias=parent.has_bias,
            groups=parent.groups,
        )

        layer.weight.data = parent.weight.data
        if layer.has_bias:
            layer.bias.data = parent.bias.data

        return layer


class F_TemporalConv1d(AtomicModule):
    def __init__(
        self,
        bitwidth,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride=1,
        dilation=1,
        groups=1,
        bias=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__(round=False)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.bias = bias
        self.groups = groups

        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)
        self.tracing = False

    @check_for_annotations
    @supports_int24(False, reason="TemporalConv2d does not support int24 activations")
    def forward(self, input, weight, bias):
        if not self.tracing:
            output = temporal_conv1d(
                input,
                weight,
                dilation=self.dilation,
                stride=self.stride,
                bias=bias,
                groups=self.groups,
            )
        else:
            raise ValueError("Tracing...")
        output = self.quantizer(copy_dim_annotations(input, output))
        return output

    def _get_constants(self, input, weight, bias):
        z = self.forward(input, weight, bias)

        buffer_quanta = input.quanta + weight.quanta
        if bias is not None:
            shamt_bias = intitem(bias.quanta - buffer_quanta)
        else:
            shamt_bias = 0

        constants = {}
        constants.update(_get_mul_constants(input, weight, z))
        constants["shamt_bias"] = shamt_bias
        constants["kernel_size_t"] = self.kernel_size
        constants["kernel_size_band"] = 1
        constants["d_band_in"] = self.in_channels
        constants["n_band_in"] = 1
        constants["dilation_t"] = self.dilation
        constants["dilation_band"] = 1
        constants["padding_band"] = 0
        constants["stride_band"] = 1
        constants["groups"] = self.groups

        return constants


class TemporalConv1d(nn.Module):
    def __init__(
        self,
        bitwidth_act,
        bitwidth_weight,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride=1,
        dilation=1,
        groups=1,
        bias=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.dialtion = dilation
        self.stride = stride
        self.has_bias = bias
        self.groups = groups

        self.weight = nn.Parameter(
            torch.empty(out_channels, in_channels // groups, kernel_size)
        )
        self.quant_weight = quantizers.ParameterQuantizer(bitwidth_weight, observer)
        if bias:
            self.quant_bias = quantizers.ParameterQuantizer(bitwidth_act, observer)
            self.bias = nn.Parameter(torch.empty(out_channels))
        else:
            self.bias = None

        self.conv = F_TemporalConv1d(
            bitwidth_act,
            in_channels,
            out_channels,
            kernel_size,
            stride,
            dilation,
            groups,
            bias,
            observer,
        )

    def forward(self, x):
        weight = self.quant_weight(self.weight)
        if self.has_bias:
            bias = self.quant_bias(self.bias)
        else:
            bias = None

        output = self.conv(x, weight, bias)
        return output

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        observer = partial(observer, **kwargs)

        layer = cls(
            bitwidth_act=bw_conf.activations,
            bitwidth_weight=bw_conf.weights,
            observer=observer,
            in_channels=parent.in_channels,
            out_channels=parent.out_channels,
            kernel_size=parent.kernel_size,
            stride=parent.stride,
            dilation=parent.dilation,
            groups=parent.groups,
            bias=parent.has_bias,
        )

        layer.weight.data = parent.weight.data
        if layer.has_bias:
            layer.bias.data = parent.bias.data

        return layer
