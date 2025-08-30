import torch
from torch import nn, Tensor
from fmot.nn.functional import temporal_conv2d, temporal_conv1d, temporal_unfold1d
import math
from torch.nn import init

# d_band_in and d_band_out must be a multiple of 1
# now all d_band is supported
D_BAND_FACTOR = 1


class UnsupportedConvParametersError(Exception):
    pass


class TemporalConv2d(nn.Module):
    """
    Applies a temporal 2D conv over a signal. Note that the input sequence is 3D, not 4D.

    Arguments:

        d_band_in (int): number of features per input band
        n_band_in (int): number of input bands
        d_band_out (int): number of features per output band
        kernel_band (int): kernel-size along the band-axis
        kernel_t (int): kernel-size along the time-axis
        dilation_band (int, optional): dilation along the band-axis. Default 1
        dilation_t (int, optional): dilation along the time-axis. Default 1
        padding_band (int, optional): zero-padding amount along the band-axis (symmetrically applied). Default 0
        stride_band (int, optional): stride along the band-axis. Default 1
        stride_t (int, optional): stride along the time-axis. Default 1.
        bias (bool, optional): If True, add a learnable bias of size :attr:`d_band_out` to each output band
        groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1.
            Currently only support `groups = 1` (full matrix-vector kernel) and `groups = d_band_in = d_band_out`
            (depthwise kernel).

    .. warning::

        :attr:`stride_t != 1` not yet supported

        Raises:

        - UnsupportedConvParametersError: If :attr:`in_channels` or :attr:`out_channels` is not an integer multiple of 8 (this is presently a compiler restriction)

    Temporal Conv2d Definition:
    ----------------------------------

    Input signals are 3D tensors of shape :attr:`(batch_size, n_band_in * d_band_in, sequence_length)`.

    The channel dimension, of size :attr:`n_band_in * d_band_in`, is split into :attr:`n_band_in`
    contiguous, non-overlapping bands, each of size :attr:`n_band_in`.

    A temporally-padded Conv2D operation is then applied to the tensor of shape
    :attr:`(batch_size, d_band_in, n_band_in, sequence_length)`, yielding a tensor of shape
    :attr:`(batch_size, d_band_out, n_band_out, sequence_length)`. This is then reshaped to
    size :attr:`(batch_size, d_band_out * n_band_out, sequence_length)`.

    We have chosen this format to reduce ambiguity regarding which convolutional axis is temporal vs.
    holding multi-band features.

    .. note::

        Comparison to :attr:`fmot.nn.TemporalConv1d`

        When :attr:`n_band_in = 1`, the layer behaves identically to :attr:`fmot.nn.TemporalConv1d`.

        .. code:: python

            from fmot.nn import TemporalConv2d, TemporalConv1d
            import torch
            from torch import nn

            Din, Dout, K = (16, 16, 3)
            model = TemporalConv2d(
                d_band_in=Din,
                n_band_in=1,
                d_band_out=Dout,
                kernel_band=1,
                kernel_t=K)
            equiv = TemporalConv1d(
                in_channels=Din,
                out_channels=Dout,
                kernel_size=K,
                groups=1)

            # note that the outputs will not match because weights are different at initialization
            x = torch.randn(8, Din, 100)
            y0 = model(x)
            y1 = equiv(x)

        When :attr:`n_band_in != 1` and `kernel_band = 1`, the layer behaves like a :attr:`fmot.nn.TemporalConv1d` layer
        that is reused after extracting bands, followed by concatenation.

        .. code:: python

            Din, Dout, Kt, Nband = (16, 16, 3, 8)
            model = TemporalConv2d(
                d_band_in=Din,
                n_band_in=Nband,
                d_band_out=Dout,
                kernel_band=1,
                kernel_t=Kt)

            class MultiBandReusedTemporalConv1d(nn.Module):
                def __init__(self, d_band_in, n_band_in, d_band_out, kernel_t):
                    super().__init__()
                    self.conv = TemporalConv1d(
                        in_channels=d_band_in,
                        out_channels=d_band_out,
                        kernel_size=kernel_t,
                        groups=1
                    )
                    self.n_band_in = n_band_in

                def forward(self, x):
                    in_bands = torch.chunk(x, self.n_band_in, dim=1)
                    out_bands = []
                    for in_band in in_bands:
                        out_band = self.conv(in_band)
                        out_bands.append(out_bands)
                    out_bands = torch.cat(out_bands, dim=1)
                    return output_bands

            equiv = MultiBandReusedTemporalConv1d(Din, Nband, Dout, Kt)

            # note that the outputs will not match because weights are different at initialization
            x = torch.randn(8, Din*Nband, 100)
            y0 = model(x)
            y1 = equiv(x)


        When :attr:`kernel_band != 1`, there is no possibility of replicating the same behavior with
        :attr:`fmot.nn.TemporalConv1d` layers.

    """

    report_supported = True

    def __init__(
        self,
        d_band_in: int,
        n_band_in: int,
        d_band_out: int,
        kernel_t: int,
        kernel_band: int,
        dilation_band: int = 1,
        dilation_t: int = 1,
        padding_band: int = 0,
        stride_band: int = 1,
        stride_t: int = 1,
        bias: bool = True,
        groups: int = 1,
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

        # pre-compute number of output bands
        self.n_band_out = (
            n_band_in + 2 * padding_band - dilation_band * (kernel_band - 1) - 1
        )
        self.n_band_out = int(math.floor(self.n_band_out / stride_band + 1))

        if d_band_in % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"d_band_in must be an integer multiple of 8, got {d_band_in}"
            )
        if d_band_out % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"d_band_out must be an integer multiple of 8, got {d_band_out}"
            )

        if groups != 1:
            if self.d_band_in != self.d_band_out or self.groups != self.d_band_in:
                raise ValueError(
                    f"Only full (groups = 1) or depthwise (groups == d_band_in == d_band_out) currently supported\n"
                    f"got {groups = } with {d_band_in = } and {d_band_out = }"
                )

        if stride_t != 1:
            raise ValueError(f"stride_t != 1 not yet supported for TemporalConv2d")

        self.weight = nn.Parameter(
            torch.empty(d_band_out, d_band_in // groups, kernel_band, kernel_t)
        )
        if bias:
            self.bias = nn.Parameter(torch.empty(d_band_out))
        else:
            self.bias = None

        self.reset_parameters()

    def reset_parameters(self) -> None:
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(k), 1/sqrt(k)), where k = weight.size(1) * prod(*kernel_size)
        # For more details see: https://github.com/pytorch/pytorch/issues/15314#issuecomment-477448573
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            if fan_in != 0:
                bound = 1 / math.sqrt(fan_in)
                init.uniform_(self.bias, -bound, bound)

    def forward(self, x):
        """
        Performs causal 2D convolutions on the input sequence.

        Arguments:
            x (Tensor): Tensor of shape :attr:`(batch, d_band_in * n_band_in, seq_length)`.

        Returns:
            Tensor of shape :attr:`(batch, d_band_out * n_band_out, seq_length)`
        """
        return temporal_conv2d(
            x,
            self.weight,
            self.dilation_t,
            self.dilation_band,
            self.padding_band,
            self.stride_band,
            self.stride_t,
            self.bias,
            groups=self.groups,
        )


class TemporalConv1d(nn.Module):
    """Applies a temporal 1D conv over a signal.

    Arguments:

        in_channels (int): number of input features
        out_channels (int): number of output features
        kernel_size (int): kernel size along the time-axis
        stride (int, optional): stride along the time-axis, default 1
        dilation (int, optional): dilation along the time-axis, default 1
        groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1.
            Currently only support `groups = 1` (full matrix-vector kernel) and `groups = d_band_in = d_band_out`
            (depthwise kernel).
        bias (bool, optional): If True, add a learnable bias of size :attr:`d_band_out` to each output band.
            Default True.

    .. warning::

        :attr:`stride != 1` not yet supported

    """

    report_supported = True

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride=1,
        dilation=1,
        groups=1,
        bias=True,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.stride = stride
        self.groups = groups
        self.has_bias = bias

        if in_channels % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"in_channels must be an integer multiple of 8, got {in_channels}"
            )
        if out_channels % D_BAND_FACTOR != 0:
            raise UnsupportedConvParametersError(
                f"out_channels must be an integer multiple of 8, got {out_channels}"
            )

        if groups != 1:
            if self.in_channels != self.out_channels or self.groups != self.in_channels:
                raise ValueError(
                    f"Only full (groups = 1) or depthwise (groups == in_channels == out_channels) currently supported\n"
                    f"got {groups = } with {in_channels = } and {out_channels = }"
                )

        if stride != 1:
            raise ValueError(f"stride != 1 not yet supported for TemporalConv1d")

        self.weight = nn.Parameter(
            torch.empty(out_channels, in_channels // groups, kernel_size)
        )
        if bias:
            self.bias = nn.Parameter(torch.empty(out_channels))
        else:
            self.bias = None

        self.reset_parameters()

    def reset_parameters(self) -> None:
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(k), 1/sqrt(k)), where k = weight.size(1) * prod(*kernel_size)
        # For more details see: https://github.com/pytorch/pytorch/issues/15314#issuecomment-477448573
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            if fan_in != 0:
                bound = 1 / math.sqrt(fan_in)
                init.uniform_(self.bias, -bound, bound)

    def forward(self, x):
        """
        Args:
            x (Tensor): shape (N, Cin, Lin)
        Returns
            y (Tensor): shape (N, Cout, Lin//stride)
        """
        return temporal_conv1d(
            x,
            self.weight,
            self.dilation,
            self.stride,
            self.bias,
            groups=self.groups,
        )


class TemporalUnfold1d(nn.Module):
    """
    Extract sliding window from an input tensor.

    Applies temporal padding as appropriate for TemporalConv1d and
    SlidingWindowCausalAttention

    `input` is a tensor of shape `(N, C, T)`, where `N` is the
    batch size, `C` is the channel dimension, and `T` is the sequence length.

    It outputs a tensor of shape `(N, C*kernel_size, T)`. Each output flattens
    each `kernel_size`-sized sliding block over the input sequence.

    Arguments:
        kernel_size (int): kernel size of the sliding window
        dilation (int, optional): dilation to use when constructing the sliding windows, default: 1
        stride (int, optional): stride, default: 1.

    .. warning::

        :attr:`stride != 1` not yet supported
    """

    report_supported = True

    def __init__(self, kernel_size: int, stride=1, dilation: int = 1):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation

        if stride != 1:
            raise ValueError(f"stride != 1 not yet supported for TemporalUnfold1d")

    def forward(self, x: Tensor) -> Tensor:
        return temporal_unfold1d(x, self.kernel_size, self.stride, self.dilation)
