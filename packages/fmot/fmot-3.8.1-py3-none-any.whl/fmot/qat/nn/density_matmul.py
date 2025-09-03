from functools import partial
from collections import defaultdict

import torch
from .atomics import AtomicModule, _get_mul_constants, ACC_BW
from ._utils import intitem
from . import quantizers
from ..annotated_tensors import (
    check_for_annotations,
    set_dim_annotations,
    get_dim_annotations,
    annotate,
)
from ..fake_quantization import fake_quantize
from copy import deepcopy
from fmot import ROUND_CONFIG


def is_sparse(*tensors):
    """Returns a boolean list -- whether each tensor has a nonzero average sparsity"""
    return [x.prev_relu for x in tensors]


def nb_elem(shape_list):
    numel = 1
    for shape in shape_list:
        numel *= shape

    return numel


class _diffable_pos(torch.autograd.Function):
    """Returns the mask x > 0 as a FloatTensor

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


class _MMBase(AtomicModule):
    """Base atomic class for matmul operator

    Measures a variety of different types of activation/lookup densities. By default, no density
    metrics will be tracked (this is for computational and memory efficiency). Density metrics can
    be easily enabled and disabled.

    Args:
        matcol_dim: for fanout, we need to know which column to collapse
            for the matrix, when we rewrite the matmul as W*x. This dimension is the matcol_dim

    Attributes:
        delta: per-element average density vector for this matmul operation.
        nb_iter: the nb of times the matmul is called during exec.
            (including batch and time repetitions)
        mat: a pointer to the matrix used in the matmul operation.
        batch_dim: batch dimension of the input of the matmul.
        act_density: activation density for the matmul operation
        lookup density: lookup density for the matmul operation
        fanout_density: fanout density for the matmul operation

    """

    def __init__(self, matcol_dim=None):
        super().__init__(round=ROUND_CONFIG.matmul)
        self.matcol_dim = matcol_dim
        self.has_sparse_input = False

        # Factors that are updated after forward pass
        self.register_buffer("delta", None)
        self.nb_iter = None
        self.register_buffer("mat", None)
        self.batch_dim = None

        # Factors that are updated when metrics are computed
        self.register_buffer("_fanout", None)

        self.register_buffer("act_density", None)
        self.register_buffer("lookup_density", None)
        self.register_buffer("fanout_density", None)

    def _update_factors(self, delta_updt, mat, nb_iter_updt):
        """Private method: updates internal store of factors to
        compute activations density metrics later.

        Args:
            delta (tensor): Per-element average vector density,
                which is a tensor that has same size as the act. vector.
        """
        if self.delta is None:
            self.delta = delta_updt / nb_iter_updt
            # print(self.delta.device)
        else:
            # TODO:handle that better. Why is to() method not called from Linear?
            # print(self.delta.device)
            # print(delta_updt.device)
            # self.delta = self.delta.to(delta_updt.device)
            self.delta = (self.nb_iter * self.delta + delta_updt) / (
                self.nb_iter + nb_iter_updt
            )

        if self.nb_iter is None:
            self.nb_iter = nb_iter_updt
        else:
            self.nb_iter += nb_iter_updt

        # Save pointer to mat for later computations
        self.mat = mat

    def reset_act_densities(self):
        """Resets all activation density counters to zero"""
        self.delta = None
        self.nb_iter = None
        self.mat = None
        self._fanout = None
        self.act_density = None
        self.lookup_density = None
        self.fanout_density = None

    def _check_for_sparsity(self, *tensors):
        sparse = is_sparse(*tensors)
        self.has_sparse_input = any(sparse)

        return self.has_sparse_input

    def _register_density_factors(self, x, y):
        """Register the activation-specific factors that are needed for
        the computation of the activation densities. Densities are
        averaged on all dimensions but the last one (feature dimension).
        """
        sparse = is_sparse(x, y)
        assert any(sparse), "Activation density not measureable"
        if all(sparse):
            raise ValueError("Both inputs are sparse; undefined behavior")
        if sparse[0]:
            vec, mat = x, y
        else:
            vec, mat = y, x
        self.batch_dim = vec.dimensions.index("B")
        if self.matcol_dim is None:
            self.matcol_dim = 0 if (self.batch_dim == 1) else 1

        # In linear layers, inputs are of shape (N, *, Hin)
        # So we need to reduce all dimensions but the last one to get densities
        red_idx = [i for i in range(len(vec.shape) - 1)]
        nb_iter = nb_elem(x.shape[:-1])
        delta = _diffable_pos.apply(vec).sum(red_idx).float()

        self._update_factors(delta, mat, nb_iter)

    def fanout(self):
        # We consider that fanout only changes between
        # forward method calls
        if self._fanout is not None:
            return self._fanout

        assert self.mat is not None, (
            "Inputs need to have been passed "
            "through the model in order to compute activation sparsity"
        )
        self._fanout = (self.mat != 0).sum(self.matcol_dim).float()

        return self._fanout

    def measure_act_density(self):
        """Computes and store the layer's
        activation density"""
        if self.delta is None:
            return None
        layer_density = self.delta.mean() * self.nb_iter
        layer_weight = self.nb_iter
        self.act_density = layer_density / layer_weight

        return layer_density, layer_weight

    def measure_lookup_density(self):
        """Computes and store the layer's
        lookup activation density"""
        if self.delta() is None:
            return None
        layer_lookup = self.delta.dot(self.fanout()) * self.nb_iter
        layer_weight = self.numel() * self.nb_iter
        self.lookup_density = layer_lookup / layer_weight

        return layer_lookup, layer_weight

    def measure_fanout_density(self):
        """Computes and store the layer's
        fanout activation density"""
        if self.delta() is None:
            return None
        layer_fanout = self.delta.dot(self.fanout()) * self.nb_iter
        layer_weight = self.fanout().sum() * self.nb_iter
        self.lookup_density = layer_fanout / layer_weight

        return layer_fanout, layer_weight


class Matmul(_MMBase):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__()
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

    @check_for_annotations
    def forward(self, x, y):
        if self._check_for_sparsity(x, y):
            self._register_density_factors(x, y)
        dimensions = get_dim_annotations(x, y)

        return self.quantizer(set_dim_annotations(dimensions, torch.matmul(x, y)))

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

    @check_for_annotations
    def _get_constants(self, x, y):
        constants = {"rounded": self.round}
        z = self.forward(x, y)
        constants.update(_get_mul_constants(x, y, z))

        if self.quantize:
            constants["bw_out"] = z.bitwidth.bitwidth
            if "bw" in constants:
                del constants["bw"]
        return deepcopy(constants)


class NoShiftMM(_MMBase):
    def __init__(self, bitwidth):
        super().__init__()
        self.bitwidth = bitwidth

    @check_for_annotations
    def forward(self, x, y):
        if self._check_for_sparsity(x, y):
            self._register_density_factors(x, y)

        dimensions = get_dim_annotations(x, y)
        z = torch.matmul(x, y)
        quanta = None
        quantized = False
        if self.quantize:
            quantized = True
            quanta = x.quanta + y.quanta
            z = fake_quantize(z, quanta, self.bitwidth.bitwidth, rounded=self.round)
        return annotate(z, self.bitwidth, quanta, quantized, dimensions=dimensions)

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        return cls(bitwidth=bw_conf.activations)

    def _get_constants(self, x, y):
        constants = {}
        z = self.forward(x, y)
        if self.quantize:
            xq, yq, zq = [w.quanta for w in [x, y, z]]
            buffer_quanta = xq + yq
            constants["shamt_bwred"] = intitem(buffer_quanta - zq)
            constants["bw_out"] = z.bitwidth.bitwidth
        return constants


class AddMM(_MMBase):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS["default"]):
        super().__init__()
        self.quantizer = quantizers.Quantizer(
            bitwidth, observer=observer, rounded=self.round
        )

    @check_for_annotations
    def forward(self, bias, x, y):
        # requantize bias vector to match the buffer
        dimensions = get_dim_annotations(x, y)
        if self._check_for_sparsity(x, y):
            self._register_density_factors(x, y)

        if self.quantize:
            buffer_quanta = x.quanta + y.quanta
            bias = fake_quantize(bias, buffer_quanta, ACC_BW, rounded=self.round)
        if x.dim() == 2 and y.dim() == 2:
            try:
                z = torch.addmm(bias, x, y)
            except Exception as e:
                print(f"input dimensions: {x.dimensions}, input shape: {x.shape}")
                raise e
        else:
            z = torch.matmul(x, y) + bias
        return self.quantizer(set_dim_annotations(dimensions, z))

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

    def _get_constants(self, bias, x, y):
        constants = {"rounded": self.round}
        z = self.forward(bias, x, y)
        if self.quantize:
            bq, xq, yq, zq = [w.quanta for w in [bias, x, y, z]]
            buffer_quanta = xq + yq
            constants["shamt_bwred"] = intitem(buffer_quanta - zq)
            constants["shamt_bias"] = intitem(bq - buffer_quanta)
            constants["bw_out"] = z.bitwidth.bitwidth
        return constants
