import torch
import torch.nn.utils.prune as prune
import torch.nn.functional as F
from ..utils.conv1d_utils import (
    flatten_conv_matrix,
    inv_flatten_conv_matrix,
    is_depthwise,
)

import fmot


class PencilPruning(prune.BasePruningMethod):
    """This is a Local Pruning class made to prune
    a weight matrix in a pencil-sparse manner (along the column dimension).

    """

    PRUNING_TYPE = "global"

    def __init__(self, amount, pencil_size):
        """

        Args:
            amount (float): percent of the model to prune out
            pencil_size (int): size of the pencils
        """
        super().__init__()
        self.amount = amount
        self.pencil_size = pencil_size

    def compute_mask(self, tensor, default_mask):
        # Rk: if we take 30% and the matrix has 3 pencils -> we round up to 33%

        # Verify that the tensor is 2D
        assert tensor.dim() == 2

        nrows, ncols = tensor.shape
        padding = (self.pencil_size - (nrows % self.pencil_size)) % self.pencil_size
        mask = F.pad(default_mask, (0, 0, 0, padding))

        # We slice the tensor h*w in x*pencil_size, slicing is done column-wise
        # We want to collapse on the last axis of this vector, this is shallow copy. Verify flatten
        # Thus we get the mean values per pencil-slice
        padded_tensor = F.pad(tensor, (0, 0, 0, padding))
        sliced_tensor = padded_tensor.t().flatten().view(-1, self.pencil_size)
        pencil_shrunk_tensor = torch.mean(torch.abs(sliced_tensor), -1).flatten()

        tensor_size = pencil_shrunk_tensor.nelement()
        nparams_toprune = prune._compute_nparams_toprune(self.amount, tensor_size)
        # This should raise an error if the number of units to prune is larger
        # than the number of units in the tensor
        prune._validate_pruning_amount(nparams_toprune, tensor_size)

        if nparams_toprune != 0:  # k=0 not supported
            bottom_k = torch.topk(
                pencil_shrunk_tensor.flatten(), k=nparams_toprune, largest=False
            )
            pencil_indices_toprune = bottom_k.indices
        else:
            pencil_indices_toprune = []

        # The indices to prune are the indices of the pencil once the
        # matrix is pencil-flat, so we don't have to 'expand' the mask
        mask = mask.t().flatten().view(-1, self.pencil_size)
        mask[pencil_indices_toprune, :] = 0

        # Because of the padding we need to cut off the additional rows
        mask = mask.view(padded_tensor.t().shape).t()
        mask = mask[:nrows, :ncols]

        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(PencilPruning, cls).apply(
            module, name, amount=amount, pencil_size=pencil_size
        )


def _pencil_linear_pruning(module, name, amount, pencil_size=8):
    PencilPruning.apply(module, name, amount, pencil_size)

    return module


class Conv1dPencilPruning(PencilPruning):
    """This is a Local Pruning class made to prune a Conv1D weight matrix in a manner that will
    result in pencil-sparse patterns once the layer is ported to the hardware.
    """

    PRUNING_TYPE = "global"

    def compute_mask(self, tensor, default_mask):
        assert tensor.dim() == 3

        out_channels, in_channels, kernel_size = tensor.shape
        flatten_tensor = flatten_conv_matrix(
            tensor, out_channels, in_channels, kernel_size
        )
        flatten_mask = flatten_conv_matrix(
            default_mask, out_channels, in_channels, kernel_size
        )

        # Apply the new mask
        flatten_mask = super().compute_mask(flatten_tensor, flatten_mask)

        mask = inv_flatten_conv_matrix(
            flatten_mask, out_channels, in_channels, kernel_size
        )

        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(Conv1dPencilPruning, cls).apply(
            module, name, amount=amount, pencil_size=pencil_size
        )


def _pencil_conv1d_pruning(module, name, amount, pencil_size=8):
    # Depthwise Conv are not prune because they are mapped to point-wise op
    if is_depthwise(module):
        pass
    else:
        Conv1dPencilPruning.apply(module, name, amount, pencil_size)

    return module


class Conv2dPencilPruning(prune.BasePruningMethod):
    """This is a Local Pruning class made to prune
    a weight matrix in a pencil-sparse manner (along the column dimension).

    """

    PRUNING_TYPE = "global"

    def __init__(self, amount, pencil_size):
        """

        Args:
            amount (float): percent of the model to prune out
            pencil_size (int): size of the pencils
        """
        super().__init__()
        self.amount = amount
        self.pencil_size = pencil_size

    def compute_mask(self, tensor, default_mask):
        # Rk: if we take 30% and the matrix has 3 pencils -> we round up to 33%

        assert tensor.dim() == 4

        o, i, kw, kh = tensor.shape

        # don't prune if i == 1 (depthwise)
        if i == 1:
            return torch.ones_like(tensor, dtype=default_mask.dtype)

        # put output dimension last
        mask = default_mask.permute(1, 2, 3, 0)
        tensor = tensor.permute(1, 2, 3, 0)

        # pad if output size is not a multiple of pencil_size
        padding = (self.pencil_size - (o % self.pencil_size)) % self.pencil_size
        mask = F.pad(mask, (0, padding))
        tensor = F.pad(tensor, (0, padding))

        # view as individual pencils
        mask = mask.flatten().reshape(-1, self.pencil_size)
        tensor = tensor.flatten().reshape(-1, self.pencil_size)

        # measure pencil magnitudes; make pruning decisions
        pencil_shrunk_tensor = torch.mean(torch.abs(tensor), -1)

        tensor_size = pencil_shrunk_tensor.nelement()
        nparams_toprune = prune._compute_nparams_toprune(self.amount, tensor_size)
        # This should raise an error if the number of units to prune is larger
        # than the number of units in the tensor
        prune._validate_pruning_amount(nparams_toprune, tensor_size)

        if nparams_toprune != 0:  # k=0 not supported
            bottom_k = torch.topk(
                pencil_shrunk_tensor, k=nparams_toprune, largest=False
            )
            pencil_indices_toprune = bottom_k.indices
        else:
            pencil_indices_toprune = []

        # The indices to prune are the indices of the pencil once the
        # matrix is pencil-flat, so we don't have to 'expand' the mask
        # note that this will broadcast the pruning to the full pencil
        mask[pencil_indices_toprune, :] = 0

        # Because of the padding we need to cut off the additional rows
        mask = mask.reshape(i, kw, kh, o + padding).permute(3, 0, 1, 2)
        mask = mask[:o]

        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(Conv2dPencilPruning, cls).apply(
            module, name, amount=amount, pencil_size=pencil_size
        )


def _pencil_conv2d_pruning(module, name, amount, pencil_size=8):
    Conv2dPencilPruning.apply(module, name, amount, pencil_size)

    return module


class ConvTranspose2dPencilPruning(Conv2dPencilPruning):
    PRUNING_TYPE = "global"

    def __init__(self, amount, pencil_size):
        super().__init__(amount=amount, pencil_size=pencil_size)

    def compute_mask(self, tensor, default_mask):
        # ConvTranspose2d weight: (in_channels, out_channels/groups, kH, kW)
        assert tensor.dim() == 4
        i, o_g, kH, kW = tensor.shape

        # Mirror your intended skip for transposed convs
        if o_g == 1:
            return torch.ones_like(tensor, dtype=default_mask.dtype)

        # Permute to Conv2d layout: (out, in, kH, kW)
        as_conv2d_w = tensor.permute(1, 0, 2, 3)  # (o_g, i, kH, kW)
        as_conv2d_m = default_mask.permute(1, 0, 2, 3)  # (o_g, i, kH, kW)

        # Reuse parent’s pencil logic
        mask_conv2d = super().compute_mask(as_conv2d_w, as_conv2d_m)

        # Back to ConvTranspose2d layout
        mask = mask_conv2d.permute(1, 0, 2, 3).contiguous()  # (i, o_g, kH, kW)
        return mask

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(ConvTranspose2dPencilPruning, cls).apply(
            module, name, amount=amount, pencil_size=pencil_size
        )


def _pencil_convtranspose2d_pruning(module, name, amount, pencil_size=8):
    # name should be "weight"
    ConvTranspose2dPencilPruning.apply(module, name, amount, pencil_size)
    return module


class GroupedLinearEinsumPencilPruning(PencilPruning):
    PRUNING_TYPE = "global"

    def compute_mask(self, tensor, default_mask):
        # tensor: (G, I_g, O_g) → flatten to (OUT, IN) = (G*O_g, I_g)
        assert tensor.dim() == 3
        G, I_g, O_g = tensor.shape

        flat_w = tensor.permute(0, 2, 1).reshape(G * O_g, I_g)
        flat_m = default_mask.permute(0, 2, 1).reshape(G * O_g, I_g)

        flat_m = super().compute_mask(flat_w, flat_m)

        mask = flat_m.view(G, O_g, I_g).permute(0, 2, 1)
        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(GroupedLinearEinsumPencilPruning, cls).apply(
            module, name, amount=amount, pencil_size=pencil_size
        )


def _pencil_grouped_linear_einsum_pruning(module, name, amount, pencil_size=8):
    # name should be "weight" on GroupedLinearEinsum
    GroupedLinearEinsumPencilPruning.apply(module, name, amount, pencil_size)
    return module


def pencil_pruning(module, name, amount, pencil_size=8):
    param = getattr(module, name)

    if param.dim() == 2:
        _pencil_linear_pruning(module, name, amount, pencil_size)
    elif param.dim() == 3:
        if type(module).__name__ == "GroupedLinearEinsum":
            _pencil_grouped_linear_einsum_pruning(module, name, amount, pencil_size)
        else:
            _pencil_conv1d_pruning(module, name, amount, pencil_size)
    elif param.dim() == 4:
        if isinstance(
            module,
            (torch.nn.Conv2d, fmot.nn.TemporalConv2d, fmot.qat.nn.TemporalConv2d),
        ):
            _pencil_conv2d_pruning(module, name, amount, pencil_size)
        elif isinstance(module, torch.nn.modules.conv.ConvTranspose2d):
            _pencil_convtranspose2d_pruning(module, name, amount, pencil_size)

    else:
        raise Exception(
            f"Femtostack does not support pruning for parameters of module: {type(module)}, dimension {param.dim} , "
        )
