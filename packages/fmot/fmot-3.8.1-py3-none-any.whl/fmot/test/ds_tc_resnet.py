import torch
import fmot
from torch import nn

params = dict(
    input_size=32,
    channel_sizes=[128, 64, 64, 64, 128, 128],
    kernel_sizes=[11, 13, 15, 17, 29, 1],
    dilations=[1, 1, 1, 1, 2, 1],
    repeats=[1, 1, 1, 1, 1, 1],
    residuals=[0, 1, 1, 1, 0, 0],
    num_labels=16,
    scale=True,
    bias=False,
)


class DSTemporalConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation=1, bias=False):
        super().__init__()
        self.dw_conv = fmot.nn.TemporalConv1d(
            in_channels=in_channels,
            out_channels=in_channels,
            kernel_size=kernel_size,
            dilation=dilation,
            groups=in_channels,
            bias=bias,
        )
        self.pw_conv = fmot.nn.TemporalConv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=1,
            dilation=1,
            bias=bias,
        )

    def forward(self, x):
        x = self.dw_conv(x)
        x = self.pw_conv(x)
        return x


class ResidualConnection(nn.Module):
    def __init__(self, in_channels, out_channels, bias=False):
        super().__init__()
        self.pw_conv = fmot.nn.TemporalConv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=1,
            dilation=1,
            bias=bias,
        )

    def forward(self, x, resid):
        return self.pw_conv(x) + resid


class NoConnection(nn.Module):
    def __init__(self):
        super().__init__()
        self.id = fmot.nn.Identity()

    def forward(self, x, resid):
        return self.id(resid)


class ResNetBlock(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        dilation,
        repeats=1,
        residual=True,
        scale=True,
        bias=False,
        batchnorm=True,
    ):
        super().__init__()
        self.layers = nn.ModuleList()
        i = 0
        for __ in range(repeats - 1):
            self.layers.append(
                DSTemporalConv(
                    in_channels=in_channels if i == 0 else out_channels,
                    out_channels=out_channels,
                    kernel_size=kernel_size,
                    dilation=dilation,
                    bias=bias,
                )
            )
            if batchnorm:
                self.layers.append(nn.BatchNorm1d(out_channels, affine=scale))
            self.layers.append(nn.ReLU())
            i += 1
        self.layers.append(
            DSTemporalConv(
                in_channels=in_channels if i == 0 else out_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                dilation=dilation,
                bias=bias,
            )
        )
        if batchnorm:
            self.last_batchnorm = nn.BatchNorm1d(out_channels, affine=scale)
        else:
            self.last_batchnorm = fmot.nn.Identity()
        if residual:
            self.connection = ResidualConnection(in_channels, out_channels, bias=bias)
        else:
            self.connection = NoConnection()

    def forward(self, x):
        resid = x
        for layer in self.layers:
            resid = layer(resid)
        x = self.connection(x, resid)
        x = self.last_batchnorm(x).relu()
        return x


class DSTCResNet(torch.nn.Module):
    """
    Args:
        input_size (int): number of input features for sequence
        channel_sizes (List[int]): number of filters for each block
        kernel_sizes (List[int]): kernel size for each block
        dilations (List[int]): dilation for each block
        residuals (List[bool]): whether to use residual connections for each block
        scale (bool): whether to learn affine transformations for BatcNorm,
            default True
        bias (bool): whether to use a bias in conv1d, default False
    """

    def __init__(
        self,
        input_size,
        channel_sizes,
        kernel_sizes,
        dilations,
        repeats,
        residuals,
        num_labels,
        scale=True,
        bias=False,
    ):
        super().__init__()
        num_blocks = len(channel_sizes)
        assert all(
            [
                len(p) == num_blocks
                for p in [kernel_sizes, dilations, repeats, residuals]
            ]
        )
        in_channels = input_size
        self.blocks = nn.ModuleList()
        params = (channel_sizes, kernel_sizes, dilations, repeats, residuals)
        for c, k, d, rep, res in zip(*params):
            self.blocks.append(
                ResNetBlock(
                    in_channels=in_channels,
                    out_channels=c,
                    kernel_size=k,
                    dilation=d,
                    repeats=rep,
                    residual=res,
                    scale=scale,
                    bias=bias,
                )
            )
            in_channels = c
        self.lin_out = fmot.nn.TemporalConv1d(
            in_channels=in_channels,
            out_channels=num_labels,
            kernel_size=1,
            dilation=1,
            bias=True,
        )

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        x = self.lin_out(x)
        return x


def model(**kwargs):
    pars = params.copy()
    pars.update(kwargs)
    return DSTCResNet(**pars)


small_params = dict(
    input_size=32,
    channel_sizes=[128, 64, 128],
    kernel_sizes=[4, 4, 1],
    dilations=[1, 2, 1],
    repeats=[1, 1, 1],
    residuals=[1, 0, 0],
    num_labels=16,
    scale=True,
    bias=False,
)


def small_model(**kwargs):
    pars = small_params.copy()
    pars.update(kwargs)
    return DSTCResNet(**pars)


tiny_params = dict(
    input_size=32,
    channel_sizes=[32, 32],
    kernel_sizes=[2, 2],
    dilations=[1, 2],
    repeats=[1, 1],
    residuals=[1, 0],
    num_labels=16,
    scale=True,
    bias=False,
)


def tiny_model(**kwargs):
    pars = tiny_params.copy()
    pars.update(kwargs)
    return DSTCResNet(**pars)
