import torch
from torch import Tensor
from torch.nn import functional as F
from typing import Optional


def temporal_conv2d(
    input: Tensor,
    weight: Tensor,
    dilation_t: int = 1,
    dilation_band: int = 1,
    padding_band: int = 0,
    stride_band: int = 1,
    stride_t: int = 1,
    bias: Optional[Tensor] = None,
    groups: int = 1,
):
    """
    Arguments:
        input (Tensor): Tensor of shape (*, d_band_in * n_band_in, time)
        weight (Tensor): Tensor of shape (d_band_out, d_band_in OR 1, kernel_band, kernel_time)
        dilation_t (int): dilation along the time-axis
        dilation_band (int): band dilation
        padding_band (int): number of bands of padding (applied symmetrically)
        stride_band (int): stride along the band axis
        stride_t (int): stride along the time axis
        groups (int): number of input feature groups to use in convolution.
    """
    d_band_out, d_band_in, kernel_band, kernel_t = weight.shape
    if bias is not None:
        assert bias.shape[0] == d_band_out
    d_band_in = d_band_in * groups

    tracing = input.ndim == 2
    if tracing:
        input = input.unsqueeze(-1)

    batch, channels_in, time = input.shape

    assert channels_in % d_band_in == 0
    num_bands = channels_in // d_band_in

    input = input.reshape(batch, num_bands, d_band_in, time)
    input = input.transpose(1, 2)

    # causal temporal padding
    pad_amount = (kernel_t - 1) * dilation_t
    input = F.pad(input, (pad_amount, 0))

    output = F.conv2d(
        input,
        weight,
        bias,
        stride=(stride_band, stride_t),
        dilation=(dilation_band, dilation_t),
        padding=(padding_band, 0),
        groups=groups,
    )
    output = output.transpose(1, 2)

    output = output.reshape(batch, -1, time)

    if tracing:
        output = output.squeeze(-1)

    return output


def temporal_conv1d(
    input: Tensor,
    weight: Tensor,
    dilation: int = 1,
    stride: int = 1,
    bias: Optional[Tensor] = None,
    groups: int = 1,
):
    d_out, d_in, kernel = weight.shape
    if bias is not None:
        assert bias.shape[0] == d_out

    d_in = d_in * groups

    tracing = input.ndim == 2
    if tracing:
        input = input.unsqueeze(-1)

    batch, channels_in, time = input.shape

    assert channels_in == d_in

    # causal temporal padding
    pad_amount = (kernel - 1) * dilation
    input = F.pad(input, (pad_amount, 0))

    output = F.conv1d(
        input,
        weight,
        bias,
        stride=stride,
        dilation=dilation,
        padding=0,
        groups=groups,
    )

    if tracing:
        output = output.squeeze(-1)

    return output


def temporal_unfold1d(x: Tensor, kernel_size: int, stride: int = 1, dilation: int = 1):
    B, C, T = x.shape

    buffsize = (kernel_size - 1) * dilation

    gathers = [
        kernel_size * torch.arange(0, C, device=x.device) + k
        for k in range(kernel_size)
    ]
    gathers = torch.cat(gathers, 0)
    gathers = gathers.reshape(1, -1, 1)
    gathers = gathers.expand(B, kernel_size * C, T // stride)

    buffer = torch.zeros((B, C, buffsize), device=x.device)

    x = torch.cat([buffer, x], dim=-1)
    x = torch.unsqueeze(x, -2)
    x = F.unfold(
        x,
        kernel_size=(1, kernel_size),
        dilation=(1, dilation),
        padding=0,
        stride=(1, stride),
    )
    x = x.gather(1, gathers)
    return x


def temporal_fold_transpose1d(
    input: Tensor, kernel_size: int, stride: int = 1, dilation: int = 1
):
    """Base implementation of the transposed-fold-1d operation.

    Arguments:
        input (Tensor): input time-series to apply transposed fold, shape ``(B, Cin, Lin)``
            where ``Cin`` is divisible by kernel_size
        kernel_size (int): kernel size
        stride (int): stride
        dilation (int): dilation, **must be 1** (for now)

    Returns:
        tensor of shape ``(B, Cin // kernel_size, Lin * stride)``

    Steps at time t: (this isn't the implementation here, but an equivalent algorithm)
    `k`: kernel-size
    `s`: stride
    `m`: buffer-size, `m = max(k - s, 0)`
    1. input x is chunked into `kernel_size` subvectors [x_1, ..., x_k]
    2. add buffer to the first `m` subvectors: {x_i = x_i + b_i; i = 1, ..., m}
    3. the first `s` subvectors are output: {y_{t*s + i} = x_i, i = 1, ..., s}
    4. the remaining `m` subvectors are stored as new values for the buffer: {b_i <- x_{s + i}, i = 1, ..., m}

    Examples:

    k = 4, s = 2

        y  | b' || x  | b  |||   eq'n
        ------------------------
        y0 | -- || x0 | b0 ||| y0 = x0 + b0
        y1 | -- || x1 | b1 ||| y1 = x1 + b1
        -- | b0 || x2 | -- ||| b0 = x2
        -- | b1 || x3 | -- ||| b1 = x3

    k = 4, s = 1

        y  | b' || x  | b  |   eq'n
        ------------------------
        y0 | -- || x0 | b0 ||| y0 = x0 + b0
        -- | b0 || x1 | b1 ||| b0 = x1 + b1
        -- | b1 || x2 | b2 ||| b1 = x2 + b2
        -- | b2 || x3 | -- ||| b2 = x3

    k = 4, s = 3

        y  | b' || x  | b  |   eq'n
        ------------------------
        y0 | -- || x0 | b0 ||| y0 = x0 + b0
        y1 | -- || x1 | -- ||| y1 = x1
        y2 | -- || x2 | -- ||| y2 = x2
        -- | b0 || x3 | -- ||| b0 = x3

    """
    assert dilation == 1, f"dilation != 1 not yet supported for FoldTranspose1d."
    buffsize = int(max(kernel_size - stride, 0))

    batch, ch_in, length = input.shape

    assert (
        ch_in % kernel_size == 0
    ), f"Input channels ({ch_in}) must be divisible by kernel_size ({kernel_size})"

    dtype = input.dtype
    device = input.device

    ch_out = ch_in // kernel_size
    buffer = torch.zeros(batch, buffsize * ch_out, dtype=dtype, device=device)

    length_out = length * stride

    outs = torch.empty((batch, length_out, ch_out), dtype=dtype, device=device)

    for i, x in enumerate(input.unbind(dim=2)):
        bpad = torch.nn.functional.pad(buffer, (0, (kernel_size - buffsize) * ch_out))
        x = x + bpad
        y, buffer = torch.split(x, [stride * ch_out, buffsize * ch_out], dim=1)
        outs[:, i * stride : (i + 1) * stride, :] = y.reshape(batch, stride, ch_out)

    outs = outs.transpose(1, 2)
    return outs
