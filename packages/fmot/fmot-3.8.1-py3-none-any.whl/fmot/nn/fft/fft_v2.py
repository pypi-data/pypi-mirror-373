import torch
from torch import nn, Tensor
from .fft_v1 import (
    get_fft_matrices,
    get_reversal_matrix,
    get_irfft_matrices,
    get_ifft_matrices,
    FFTwiddle,
    FFTPermuter,
    IFFTNormalizer,
    get_rfft2fft_matrices,
)

from fmot.nn import SuperStructure
import numpy as np
from typing import *

__all__ = ["FFTv2", "RFFTv2", "IRFFTv2", "IFFTv2"]
BASE_RFFT = False
TWIDDLE_PARALLELISM = 1
DFT_PARALLELISM = 1


def quant8(x: torch.Tensor) -> torch.Tensor:
    """fake-quantize a float tensor to int8 with power-of-2 scale"""
    mv = x.abs().max()
    q = mv.log2().ceil() - 6
    xq = (x / 2**q).round()
    x_fq = xq * 2**q
    return x_fq


class Virtual16bMatmul(nn.Module):
    def __init__(self, weight: Tensor, requires_grad=False):
        super().__init__()
        assert not requires_grad

        w_upper = quant8(weight)
        w_lower = weight - w_upper

        self.weight_upper = nn.Parameter(w_upper, requires_grad=requires_grad)
        self.weight_lower = nn.Parameter(w_lower, requires_grad=requires_grad)

    def forward(self, x):
        y_upper = torch.matmul(x, self.weight_upper.T)
        y_lower = torch.matmul(x, self.weight_lower.T)
        y = y_upper + y_lower
        return y


class DFTv2(nn.Module):
    """Applies NxN DFT to real signal, returning
    real and imaginary parts as separate tensors.

    v2: Uses virtual int16 precision for weight matrix for improved performance
    """

    def __init__(self, n_fft: int):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = Virtual16bMatmul(fft_real, requires_grad=False)
        self.fft_imag = Virtual16bMatmul(fft_imag, requires_grad=False)

    def forward(self, x):
        y_real = self.fft_real(x)
        y_imag = self.fft_imag(x)
        return y_real, y_imag


class DFTFromRFFTv2(nn.Module):
    """
    Computes NxN DFT for a real signal, using RFFT matrices to simplify the computation.

    v2: Uses virtual int16 precision for weight matrix for improved performance
    """

    def __init__(self, n_fft: int):
        super().__init__()
        self.n_fft = n_fft
        self.n = n_fft // 2 + 1
        fft_real, fft_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        rfft_real = fft_real[: self.n]
        rfft_imag = fft_imag[: self.n]
        self.rfft_real = Virtual16bMatmul(rfft_real, requires_grad=False)
        self.rfft_imag = Virtual16bMatmul(rfft_imag, requires_grad=False)
        self.rev = nn.Parameter(get_reversal_matrix(n_fft), requires_grad=False)

    def forward(self, x):
        fwd_real = self.rfft_real(x)
        fwd_imag = self.rfft_imag(x)

        rev_real = torch.matmul(fwd_real, self.rev.T)
        rev_imag = torch.matmul(fwd_imag, self.rev.T)

        y_real = torch.cat([fwd_real, rev_real], dim=-1)
        y_imag = torch.cat([fwd_imag, -rev_imag], dim=-1)
        return y_real, y_imag


class FFTv2(nn.Module):
    """Sparse decomposition of FFT.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Must satisfy ``n_stages < floor(log2(n_fft))``

    v2: uses virtual int16 precision for DFT weights to improve quantized performance
    """

    report_supported = True

    def __init__(self, n_fft: int, n_stages: int):
        super().__init__()

        if BASE_RFFT:
            dft_class = DFTFromRFFTv2
        else:
            dft_class = DFTv2

        self.n_fft = n_fft
        self.n_stages = n_stages
        assert (
            n_fft / 2**n_stages % 1 == 0
        ), f"Cannot decompose {n_fft} with {n_stages} power-of-2 stages"

        self.dft = dft_class(n_fft // 2**n_stages)

        self.permuter = None
        self.twiddle_states = None

        if n_stages > 0:
            self.permuter = FFTPermuter(n_fft, n_stages)
            self.twiddle_stages = nn.ModuleList()

            stage_size = n_fft // 2 ** (n_stages - 1)
            num_calls = n_fft // stage_size
            for _ in range(n_stages):
                self.twiddle_stages.append(FFTwiddle(stage_size, inv=False))
                stage_size = stage_size * 2
                num_calls = num_calls // 2

        # quantization configs
        self.observe: bool = False
        self.quantize: bool = False

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Arguments:
            x (Tensor): real-valued tensor of shape (*, n_fft)
        Returns:
            - (re, im): two tensors of shape (*, n_fft)
                The first holds the real-part, and the second holds the imaginary part
        """

        if self.permuter is None:
            return self.dft(x)

        else:
            perms = self.permuter(x)

            sub_dfts = [
                [],
                [],
                [],
                [],
            ]  # stores even_real, even_imag, odd_real, odd_imag sets

            for j, (x_even, x_odd) in enumerate(zip(perms[::2], perms[1::2])):
                ev_r, ev_i = self.dft(x_even)
                od_r, od_i = self.dft(x_odd)

                sub_dfts[0].append(ev_r)
                sub_dfts[1].append(ev_i)
                sub_dfts[2].append(od_r)
                sub_dfts[3].append(od_i)

            for twiddler in self.twiddle_stages:
                new_sub_dfts = [[], [], [], []]
                for i, (ev_r, ev_i, od_r, od_i) in enumerate(
                    zip(sub_dfts[0], sub_dfts[1], sub_dfts[2], sub_dfts[3])
                ):
                    real, imag = twiddler(ev_r, ev_i, od_r, od_i)
                    if i % 2 == 0:
                        new_sub_dfts[0].append(real)
                        new_sub_dfts[1].append(imag)
                    else:
                        new_sub_dfts[2].append(real)
                        new_sub_dfts[3].append(imag)
                sub_dfts = new_sub_dfts

            real, imag = sub_dfts[0][0], sub_dfts[1][0]
            return real, imag

    def extra_repr(self) -> str:
        f"n_fft: {self.n_fft} n_stages: {self.n_stages}"


class _RFFTDecompv2(nn.Module):
    def __init__(self, n_fft, n_stages):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages

        self.fft = FFTv2(n_fft, n_stages)
        self._split0 = int(np.floor(n_fft / 2 + 1))
        self._split1 = n_fft - self._split0

    def forward(self, x):
        yre, yim = self.fft(x)
        yre, __ = torch.split(yre, [self._split0, self._split1], -1)
        yim, __ = torch.split(yim, [self._split0, self._split1], -1)
        return yre, yim


class _RFFTDirectv2(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        n_rfft = int(np.floor(n_fft / 2 + 1))
        m_real = m_real[:n_rfft]
        m_imag = m_imag[:n_rfft]

        self.rfft_real = Virtual16bMatmul(m_real, requires_grad=False)
        self.rfft_imag = Virtual16bMatmul(m_imag, requires_grad=False)

    def forward(self, x):
        re = self.rfft_real(x)
        im = self.rfft_imag(x)
        return re, im


class RFFTv2(nn.Module):
    """Sparse decomposition of RFFT.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the RDFT. Must satisfy ``n_stages < floor(log2(n_fft))``

    v2: uses virtual int16 matrices to improve quantized performance
    """

    report_supported = True

    def __init__(self, n_fft, n_stages):
        super().__init__()
        if n_stages == 0:
            self.rfft = _RFFTDirectv2(n_fft)
        else:
            self.rfft = _RFFTDecompv2(n_fft, n_stages)

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Arguments:
            x (Tensor): real-valued tensor of shape (*, n_fft)
        Returns:
            - (re, im): two tensors of shape (*, n_freq)
                The first holds the real-part, and the second holds the imaginary part.
                Here, ``n_freq`` is ``n_fft // 2 + 1``
        """
        return self.rfft(x)


class _IRFFTDirectv2(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_irfft_matrices(n_fft, dtype=torch.float32)

        self.irfft_real = Virtual16bMatmul(m_real.T, requires_grad=False)
        self.irfft_imag = Virtual16bMatmul(m_imag.T, requires_grad=False)

    def forward(self, re, im):
        return self.irfft_real(re) + self.irfft_imag(im)


class IDFTv2(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_ifft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = Virtual16bMatmul(fft_real, requires_grad=False)
        self.fft_imag = Virtual16bMatmul(fft_imag, requires_grad=False)

    def forward(self, re, im):
        y_real = self.fft_real(re) - self.fft_imag(im)
        y_imag = self.fft_imag(re) + self.fft_real(im)
        return y_real, y_imag


class IFFTv2(nn.Module):
    """Sparse decomposition of IFFT.

    Arguments:
        n_fft (int): IFFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the IDFT. Must satisfy ``n_stages < floor(log2(n_fft))``

    v2: Uses int16 matrices for improved accuracy after quantization
    """

    report_supported = True

    def __init__(self, n_fft, n_stages):
        super().__init__()

        self.n_fft = n_fft
        self.n_stages = n_stages
        assert (
            n_fft / 2**n_stages % 1 == 0
        ), f"Cannot decompose {n_fft} with {n_stages} power-of-2 stages"

        self.idft = IDFTv2(n_fft // 2**n_stages)

        if n_stages > 0:
            self.permuter = FFTPermuter(n_fft, n_stages)
            self.twiddle_stages = nn.ModuleList()

            stage_size = n_fft // 2 ** (n_stages - 1)
            num_calls = n_fft // stage_size
            for _ in range(n_stages):
                self.twiddle_stages.append(FFTwiddle(stage_size, inv=True))
                stage_size = stage_size * 2
                num_calls = num_calls // 2

            self.normalizer = IFFTNormalizer(n_fft, n_stages)

        else:
            self.permuter = None
            self.twiddle_stages = None

        # quantization configs
        self.observe: bool = False
        self.quantize: bool = False

    def forward(self, re, im):
        if self.permuter is None:
            return self.idft(re, im)

        else:
            re_perms = self.permuter(re)
            im_perms = self.permuter(im)

            sub_dfts = [
                [],
                [],
                [],
                [],
            ]  # stores even_real, even_imag, odd_real, odd_imag sets

            for j, (x_even_re, x_odd_re, x_even_im, x_odd_im) in enumerate(
                zip(re_perms[::2], re_perms[1::2], im_perms[::2], im_perms[1::2])
            ):
                ev_r, ev_i = self.idft(x_even_re, x_even_im)
                od_r, od_i = self.idft(x_odd_re, x_odd_im)

                sub_dfts[0].append(ev_r)
                sub_dfts[1].append(ev_i)
                sub_dfts[2].append(od_r)
                sub_dfts[3].append(od_i)

            for twiddler in self.twiddle_stages:
                new_sub_dfts = [[], [], [], []]
                for i, (ev_r, ev_i, od_r, od_i) in enumerate(
                    zip(sub_dfts[0], sub_dfts[1], sub_dfts[2], sub_dfts[3])
                ):
                    real, imag = twiddler(ev_r, ev_i, od_r, od_i)
                    if i % 2 == 0:
                        new_sub_dfts[0].append(real)
                        new_sub_dfts[1].append(imag)
                    else:
                        new_sub_dfts[2].append(real)
                        new_sub_dfts[3].append(imag)
                sub_dfts = new_sub_dfts

            real, imag = sub_dfts[0][0], sub_dfts[1][0]

            real = self.normalizer(real)
            imag = self.normalizer(imag)

            return real, imag

    def extra_repr(self) -> str:
        f"n_fft: {self.n_fft} n_stages: {self.n_stages}"


class _IRFFTDecompv2(nn.Module):
    def __init__(self, n_fft: int, n_stages: int):
        super().__init__()

        mat_real, mat_imag = get_rfft2fft_matrices(n_fft)
        self.mat_real = Virtual16bMatmul(mat_real, requires_grad=False)
        self.mat_imag = Virtual16bMatmul(mat_imag, requires_grad=False)

        self.ifft = IFFTv2(n_fft, n_stages)

    def forward(self, re, im):
        re = self.mat_real(re)
        im = self.mat_imag(im)

        # run and discard the imaginary component
        y, __ = self.ifft(re, im)
        return y


class IRFFTv2(nn.Module):
    """Sparse decomposition of IRFFT.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the IRDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
    """

    report_supported = True

    def __init__(self, n_fft, n_stages: int = 0):
        super().__init__()
        self.n_fft = n_fft

        if n_stages == 0:
            self.irfft = _IRFFTDirectv2(n_fft)
        else:
            self.irfft = _IRFFTDecompv2(n_fft, n_stages)

    def forward(self, re: Tensor, im: Tensor) -> Tensor:
        """Compute the IRFFT given tensors holding the real and imaginary components.

        Arguments:
            re (Tensor): real-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``
            im (Tensor): imaginary-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``

        Returns:
            Tensor, real-valued inversion of the input RFFT.
        """
        return self.irfft(re, im)
