import torch
from torch import nn
from .super_structures import SuperStructure
from .conv import TemporalConv2d

# HELPERS:


class ZerosLike(nn.Module):
    def forward(self, x):
        return x * 0


class CatDim1(nn.Module):
    def forward(self, tensors: list[torch.Tensor]):
        return torch.cat(tensors, dim=1)


class ChunkDim1(nn.Module):
    def __init__(self, n_chunks: int):
        super().__init__()
        self.n_chunks = n_chunks

    def forward(self, x) -> list[torch.Tensor]:
        return torch.chunk(x, self.n_chunks, dim=1)


class ConvTranspose2dBandPadder(SuperStructure):
    def __init__(
        self, n_band_in: int, stride: int, k: int, padding: int, output_padding: int
    ):
        super().__init__()
        self.chunk = ChunkDim1(n_band_in)
        self.zeros_like = ZerosLike()
        self.cat = CatDim1()

        self.n_up = (n_band_in - 1) * stride + 1
        self.pad_top = k - 1 - padding
        self.pad_bottom = self.pad_top + output_padding
        self.n_bands_padded = self.n_up + self.pad_top + self.pad_bottom
        self.stride = stride

    @torch.jit.ignore
    def forward(self, x):
        bands = self.chunk(x)
        zeros = self.zeros_like(bands[0])
        up = [zeros] * self.n_up
        up[:: self.stride] = bands
        up = ([zeros] * self.pad_top) + up + ([zeros] * self.pad_bottom)
        return self.cat(up)


class TemporalConvTranspose2d(nn.Module):
    """
    Applies a transposed temporal 2D conv over a signal. Note that the input sequence is 3D, not 4D.


    Arguments:

        d_band_in (int): number of features per input band, must be a multiple of 8 (compiler kernel restriction)
        n_band_in (int): number of input bands
        d_band_out (int): number of features per output band, must be a multiple of 8 (compiler kernel restriction)
        kernel_band (int): kernel-size along the band-axis
        kernel_t (int): kernel-size along the time-axis
        dilation_t (int, optional): dilation along the time-axis. Default 1
        padding_band (int, optional): :attr:`(kernel_band - 1) - padding_band` zero-padding will be added to both
            sides of the band dimension in the input. Default: 0
        padding_band_out (int, optional): Additional zero-padding added to one side of the output bands. Default: 0
        stride_band (int, optional): stride along the band-axis. Default 1
        bias (bool, optional): If True, add a learnable bias of size :attr:`d_band_out` to each output band. Default True.
        groups (int, optional): Number of blocked connections from input channels to output channels. Default: 1.
            Currently only support `groups = 1` (full matrix-vector kernel) and `groups = d_band_in = d_band_out`
            (depthwise kernel).

    Shape:

        - Input: :attr:`(batch, d_band_in * n_band_in, time)`
        - Output: :attr:`(batch, d_band_out * n_band_out, time)`

        Where :attr:`n_band_out = (n_band_in - 1) * stride_band + 2 * (k_band - 1 - padding_band) + padding_band_out + 1`
    """

    report_supported = True

    def __init__(
        self,
        d_band_in: int,
        n_band_in: int,
        d_band_out: int,
        kernel_band: int,
        kernel_t: int,
        dilation_t: int = 1,
        stride_band: int = 1,
        padding_band: int = 0,
        padding_band_out: int = 0,
        bias: bool = True,
        groups: int = 1,
    ):
        super().__init__()
        self.d_band_in = d_band_in
        self.n_band_in = n_band_in
        self.d_band_out = d_band_out
        self.kernel_t = kernel_t
        self.dilation_t = dilation_t
        self.kernel_band = kernel_band
        self.stride_band = stride_band
        self.padding_band = padding_band
        self.padding_band_out = padding_band_out
        self.has_bias = bias
        self.groups = groups

        self.n_up = (self.n_band_in - 1) * self.stride_band + 1
        self.pad_top = self.kernel_band - 1 - self.padding_band
        self.pad_bottom = self.pad_top + self.padding_band_out
        self.n_bands_padded = self.n_up + self.pad_top + self.pad_bottom

        needs_padding = any(
            [
                self.n_bands_padded != n_band_in,
                stride_band != 1,
                padding_band != 0,
                padding_band_out != 0,
            ]
        )

        if needs_padding:
            self.padder = ConvTranspose2dBandPadder(
                n_band_in, stride_band, kernel_band, padding_band, padding_band_out
            )
        else:
            self.padder = nn.Identity()

        self.conv = TemporalConv2d(
            d_band_in=d_band_in,
            n_band_in=self.n_bands_padded,
            d_band_out=d_band_out,
            kernel_t=kernel_t,
            kernel_band=kernel_band,
            dilation_t=dilation_t,
            padding_band=0,
            stride_band=1,
            groups=groups,
            bias=bias,
        )

        self.n_band_out = self.conv.n_band_out

    def forward(self, x):
        """
        x : (B, d_band_in * n_band_in, T)
        """
        x = self.padder(x)
        y = self.conv(x)
        return y


if __name__ == "__main__":
    ch_in = 16
    n = 8

    conv = TemporalConvTranspose2d(
        d_band_in=ch_in,
        d_band_out=ch_in,
        n_band_in=n,
        kernel_t=1,
        kernel_band=3,
        stride_band=2,
        padding_band=1,
        padding_band_out=1,
        bias=False,
    )

    x = torch.randn(8, ch_in * n, 100)
    print(x.shape)
    y = conv(x)
    print(y.shape)
