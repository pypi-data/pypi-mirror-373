import torch
from torch import nn
from .sequencer import Sequencer
from .super_structures import SuperStructure
from typing import List, Tuple
from torch import Tensor
from .atomics import Identity, VVAdd, Chunk
from .functional import temporal_fold_transpose1d
from .conv import UnsupportedConvParametersError, D_BAND_FACTOR


class TemporalFoldTranspose1d(nn.Module):
    """Inverse operation to TemporalUnfold1d. TransposedConv1d can be implemented as a pointwise convolution,
    followed by a TemporalFold1d operation.

    Arguments:
        kernel_size (int): kernel size
        stride (int): stride
        dilation (int): dilation, **must be 1** (for now)

    .. warning::

        stride != 1 not yet supported
    """

    def __init__(self, kernel_size: int, stride: int = 1, dilation: int = 1):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation

        if stride != 1:
            raise ValueError("stride != 1 not yet supported in TemporalFoldTranspose1d")

    def forward(self, x):
        """
        Arguments:
            x (Tensor): tensor of shape ``(B, Cin, Lin)`` where ``Cin`` must be divisible by
                ``kernel_size``.

        Returns:
            tensor of shape ``(B, Cin // kernel_size, Lin * stride)``"""
        y = temporal_fold_transpose1d(x, self.kernel_size, self.stride, self.dilation)
        return y


class TemporalConvTranspose1d(nn.Module):
    """Temporal Transposed Conv1d. Inverse to TemporalConv1d; ensures that the sequence processing
    is causal.

    Arguments:
        in_channels (int): number of input features. Must be a multiple of 8 (compiler restriction).
        out_channels (int): number of output features. Must be a multiple of 8 (compiler restriction).
        kernel_size (int): kernel size to use in transposed convolution.
        stride (int, optional): stride to use in transposed convolution. Default 1.
        bias (int, optional): if ``True``, adds a learnable bias to outputs. Default ``True``.

    .. warning::

        stride != 1 not yet supported

        Raises:

        - UnsupportedConvParametersError: If :attr:`in_channels` or :attr:`out_channels` is not an integer multiple of 8 (this is presently a compiler restriction)

    Equivalent to:

    .. code:: python

        import torch

        kernel_size = ...
        stride = ...
        in_channels = ...
        out_channels = ...
        tconv = torch.nn.ConvTranspose1d(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = kernel_size,
            stride = stride,
            padding = 0,
            dilation = 1,
            groups = 1
        )

        length_in = 100
        x = torch.randn(8, in_channels, length_in)
        y = tconv(x)[..., :stride * length_in]
    """

    report_supported = True

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
        bias=True,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.bias = bias

        if in_channels % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"in_channels must be an integer multiple of 8, got {in_channels}"
            )
        if out_channels % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"out_channels must be an integer multiple of 8, got {out_channels}"
            )

        if stride != 1:
            raise ValueError(
                f"stride != 1 not yet supported for TemporalConvTranspose1d"
            )

        self.transposed_tcn = nn.ConvTranspose1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            dilation=1,
            bias=bias,
        )

    def forward(self, x):
        """
        Args:
            x (Tensor): shape (N, Cin, Lin)
        Returns
            y (Tensor): shape (N, Cout, Lin * stride)
        """
        length_in = x.shape[-1]
        length_out = length_in * self.stride
        y = self.transposed_tcn(x)
        y = y[..., :length_out]
        return y


class _AddBiasTranspose(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.bias = nn.Parameter(torch.randn(channels))

    def forward(self, x):
        return (x.transpose(1, 2) + self.bias).transpose(1, 2)


class FoldTemporalConvTranspose1d(nn.Module):
    """Conversion-friendly implementation of ConvTranspose1d -- used as substitution."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
        bias=True,
    ):
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.bias = bias

        self.lin = nn.Linear(in_channels, out_channels * kernel_size, bias=False)
        self.fold = TemporalFoldTranspose1d(kernel_size, stride, dilation=1)
        if self.bias:
            self.add_bias = _AddBiasTranspose(out_channels)
        else:
            self.add_bias = Identity()

    def forward(self, x):
        x = self.lin(x.transpose(1, 2)).transpose(1, 2)
        y = self.fold(x)
        y = self.add_bias(y)
        return y

    @classmethod
    def _from_torchmodule(
        cls,
        parent: TemporalConvTranspose1d,
        toplevel=None,
        inherited_name="",
        inherited_dict=dict(),
    ):
        in_channels = parent.in_channels
        out_channels = parent.out_channels
        kernel_size = parent.kernel_size

        new = cls(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=parent.stride,
            bias=parent.bias,
        )

        sd = {}
        weight = parent.transposed_tcn.weight.data
        f_reshape = lambda x: torch.reshape(
            x.transpose(1, 2), (in_channels, out_channels * kernel_size)
        ).t()
        weight = f_reshape(weight)
        sd["lin.weight"] = weight
        inherited_dict[inherited_name + "transposed_tcn.weight"] = (
            inherited_name + "lin.weight",
            f_reshape,
        )

        if parent.bias:
            bias = parent.transposed_tcn.bias.data
            sd["add_bias.bias"] = bias
            inherited_dict[inherited_name + "transposed_tcn.bias"] = (
                inherited_name + "add_bias.bias",
                None,
            )

        new.load_state_dict(sd)
        return new


class OverlapAdder(SuperStructure):
    def __init__(self, stride):
        super().__init__()
        self.stride = stride
        if self.stride > 1:
            self.adder = VVAdd()
            self.chunk = Chunk(stride, dim=1)

    def forward(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        if self.stride > 1:
            chunks = self.chunk(x)
            output = self.adder(chunks[0], state[0])
            new_state = []
            for ch, st in zip(chunks[1:], state[1:]):
                new_state.append(self.adder(ch, st))
            new_state.append(chunks[-1])
            return output, new_state
        else:
            return x, []


class OverlapAddSeq(Sequencer):
    def __init__(self, in_channels, stride):
        assert in_channels % stride == 0
        self.in_channels = in_channels
        self.out_channels = in_channels // stride
        self.stride = stride
        state_shapes = [[self.out_channels]] * (self.stride - 1)
        super().__init__(state_shapes, batch_dim=0, seq_dim=2)
        self.oadder = OverlapAdder(stride)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        return self.oadder(x_t, state)


class OverlapAdd(nn.Module):
    def __init__(self, in_channels, stride):
        super().__init__()
        self.oadd = OverlapAddSeq(in_channels, stride)

    def forward(self, x):
        y, __ = self.oadd(x)
        return y

    def __repr__(self):
        return "OverlapAdd()"
