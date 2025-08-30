import torch
from torch import nn, Tensor
from fmot.nn import SuperStructure
import numpy as np
from typing import *

__all__ = ["FFT", "RFFT", "IRFFT", "IFFT"]
BASE_RFFT = False
TWIDDLE_PARALLELISM = 1
DFT_PARALLELISM = 1


def get_fft_matrices(n_fft, dtype=torch.float32):
    mat = np.fft.fft(np.eye(n_fft))
    m_real = torch.tensor(mat.real, dtype=dtype)
    m_imag = torch.tensor(mat.imag, dtype=dtype)
    return m_real, m_imag


def get_complex_twiddle(n_fft, dtype=torch.float32, inv=False):
    sign = -1
    if inv:
        sign = 1
    w = np.exp(sign * 2j * np.pi / n_fft)
    w = np.power(w, np.arange(n_fft // 2))
    return torch.tensor(w.real, dtype=dtype), torch.tensor(w.imag, dtype=dtype)


def get_reversal_matrix(n_fft, dtype=torch.float32):
    n = n_fft // 2 + 1
    mat = torch.zeros((n_fft - n, n), dtype=dtype)
    for k in range(n_fft - n):
        mat[k, n - k - 1 - ((n_fft + 1) % 2)] = 1
    return mat


def _get_mod_seq(order):
    mset = [0]
    for ord in range(order):
        ord = 2**ord

        new_mset = []
        for x in mset:
            new_mset.append(x)
            new_mset.append(x + ord)
        mset = new_mset

    return mset


def get_partial_bit_reversal_matrix(N, order, dtype=torch.float32):
    m = np.zeros((N, N))
    perm_set = _get_mod_seq(order)
    base = 2**order

    k = 0
    for p in perm_set:
        for j in range(N // base):
            m[j * base + p, k] = 1
            k += 1

    return torch.tensor(m, dtype=dtype)


class DFT(nn.Module):
    """Applies NxN DFT to real signal, returning
    real and imaginary parts as separate tensors.
    """

    def __init__(self, n_fft: int):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = nn.Parameter(fft_real, requires_grad=False)
        self.fft_imag = nn.Parameter(fft_imag, requires_grad=False)

    def forward(self, x):
        y_real = torch.matmul(x, self.fft_real.T)
        y_imag = torch.matmul(x, self.fft_imag.T)
        return y_real, y_imag


class DFTFromRFFT(nn.Module):
    def __init__(self, n_fft: int):
        super().__init__()
        self.n_fft = n_fft
        self.n = n_fft // 2 + 1
        fft_real, fft_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        rfft_real = fft_real[: self.n]
        rfft_imag = fft_imag[: self.n]
        self.rfft_real = nn.Parameter(rfft_real, requires_grad=False)
        self.rfft_imag = nn.Parameter(rfft_imag, requires_grad=False)
        self.rev = nn.Parameter(get_reversal_matrix(n_fft), requires_grad=False)

    def forward(self, x):
        fwd_real = torch.matmul(x, self.rfft_real.T)
        fwd_imag = torch.matmul(x, self.rfft_imag.T)

        rev_real = torch.matmul(fwd_real, self.rev.T)
        rev_imag = torch.matmul(fwd_imag, self.rev.T)

        y_real = torch.cat([fwd_real, rev_real], dim=-1)
        y_imag = torch.cat([fwd_imag, -rev_imag], dim=-1)
        return y_real, y_imag


class FFTwiddle(nn.Module):
    def __init__(self, n_fft: int, inv=False):
        super().__init__()
        self.n_fft = n_fft
        twid_real, twid_imag = get_complex_twiddle(n_fft, inv=inv)
        self.twid_real = nn.Parameter(twid_real, requires_grad=False)
        self.twid_imag = nn.Parameter(twid_imag, requires_grad=False)

    def forward(self, even_real, even_imag, odd_real, odd_imag):
        todd_real = self.twid_real * odd_real - self.twid_imag * odd_imag
        todd_imag = self.twid_real * odd_imag + self.twid_imag * odd_real

        upper_real = even_real + todd_real
        upper_imag = even_imag + todd_imag
        lower_real = even_real - todd_real
        lower_imag = even_imag - todd_imag

        real = torch.cat([upper_real, lower_real], dim=-1)
        imag = torch.cat([upper_imag, lower_imag], dim=-1)

        return real, imag

    def extra_repr(self) -> str:
        return f"n_fft={self.n_fft}"


class FFTPermuter(nn.Module):
    def __init__(self, n_fft, n_stages):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages
        self.n_chunks = 2**n_stages

        self.perm = nn.Parameter(
            get_partial_bit_reversal_matrix(n_fft, n_stages), requires_grad=False
        )

    def forward(self, x):
        y = torch.matmul(x, self.perm)
        return torch.chunk(y, self.n_chunks, dim=-1)


class FFT(nn.Module):
    """Sparse decomposition of FFT.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Must satisfy ``n_stages < floor(log2(n_fft))``
    """

    report_supported = True

    def __init__(self, n_fft: int, n_stages: int):
        super().__init__()

        if BASE_RFFT:
            dft_class = DFTFromRFFT
        else:
            dft_class = DFT

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


class _RFFTDecomp(nn.Module):
    def __init__(self, n_fft, n_stages):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages

        self.fft = FFT(n_fft, n_stages)
        self._split0 = int(np.floor(n_fft / 2 + 1))
        self._split1 = n_fft - self._split0

    def forward(self, x):
        yre, yim = self.fft(x)
        yre, __ = torch.split(yre, [self._split0, self._split1], -1)
        yim, __ = torch.split(yim, [self._split0, self._split1], -1)
        return yre, yim


class _RFFTDirect(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        n_rfft = int(np.floor(n_fft / 2 + 1))
        m_real = m_real[:n_rfft]
        m_imag = m_imag[:n_rfft]

        self.rfft_real = nn.Parameter(m_real, requires_grad=False)
        self.rfft_imag = nn.Parameter(m_imag, requires_grad=False)

    def forward(self, x):
        re = torch.matmul(x, self.rfft_real.T)
        im = torch.matmul(x, self.rfft_imag.T)
        return re, im


class RFFT(nn.Module):
    """Sparse decomposition of RFFT.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the RDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
    """

    report_supported = True

    def __init__(self, n_fft, n_stages):
        super().__init__()
        if n_stages == 0:
            self.rfft = _RFFTDirect(n_fft)
        else:
            self.rfft = _RFFTDecomp(n_fft, n_stages)

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


def get_irfft_matrices(n_fft: int, dtype=torch.float32):
    n = n_fft // 2 + 1
    m_real = np.fft.irfft(np.eye(n), n=n_fft)
    m_imag = np.fft.irfft(1j * np.eye(n), n=n_fft)
    m_real = torch.tensor(m_real, dtype=dtype)
    m_imag = torch.tensor(m_imag, dtype=dtype)
    return m_real, m_imag


def get_ifft_matrices(n_fft, dtype=torch.float32):
    mat = np.fft.ifft(np.eye(n_fft))
    m_real = torch.tensor(mat.real, dtype=dtype)
    m_imag = torch.tensor(mat.imag, dtype=dtype)
    return m_real, m_imag


class _IRFFTDirect(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_irfft_matrices(n_fft, dtype=torch.float32)

        self.irfft_real = nn.Parameter(m_real.T, requires_grad=False)
        self.irfft_imag = nn.Parameter(m_imag.T, requires_grad=False)

    def forward(self, re, im):
        return torch.matmul(re, self.irfft_real.T) + torch.matmul(im, self.irfft_imag.T)


class IDFT(nn.Module):
    def __init__(self, n_fft):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_ifft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = nn.Parameter(fft_real, requires_grad=False)
        self.fft_imag = nn.Parameter(fft_imag, requires_grad=False)

    def forward(self, re, im):
        y_real = torch.matmul(re, self.fft_real.T) - torch.matmul(im, self.fft_imag.T)
        y_imag = torch.matmul(re, self.fft_imag.T) + torch.matmul(im, self.fft_real.T)
        return y_real, y_imag


class IFFTNormalizer(nn.Module):
    def __init__(self, n_fft, n_stages):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages
        self.factor = 2 ** (n_stages)

    def forward(self, x):
        return x / self.factor


class IFFT(nn.Module):
    """Sparse decomposition of IFFT.

    Arguments:
        n_fft (int): IFFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the IDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
    """

    report_supported = True

    def __init__(self, n_fft, n_stages):
        super().__init__()

        self.n_fft = n_fft
        self.n_stages = n_stages
        assert (
            n_fft / 2**n_stages % 1 == 0
        ), f"Cannot decompose {n_fft} with {n_stages} power-of-2 stages"

        self.idft = IDFT(n_fft // 2**n_stages)

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


def get_rfft2fft_matrices(n_fft: int, dtype=torch.float32):
    """Reconstruct full FFT from RFFT via sparse matrix multiplication.

    Returns
        - mat_real: Tensor of shape (n_fft, n_rfft)
        - mat_imag: Tensor of shape (n_fft, n_rfft)

    Full FFT can be reconstructed from rfft as:

    ```python
        def rfft2fft(rfft_real, rfft_imag, mat_real, mat_imag):
            fft_real = torch.matmul(rfft_real, mat_real.t())
            fft_imag = torch.matmul(rfft_imag, mat_imag.t())
            return fft_real, fft_imag
    ```
    """
    n_rfft = n_fft // 2 + 1

    mat_real = np.zeros((n_rfft, n_fft))
    mat_imag = np.zeros((n_rfft, n_fft))

    mat_real[:n_rfft, :n_rfft] = np.eye(n_rfft)
    mat_imag[:n_rfft, :n_rfft] = np.eye(n_rfft)

    rem = n_fft - n_rfft
    m_rev = np.eye(rem)[::-1]

    mat_real[1 : rem + 1, n_rfft:] = m_rev
    mat_imag[1 : rem + 1, n_rfft:] = -m_rev

    mat_real = torch.tensor(mat_real.T, dtype=dtype)
    mat_imag = torch.tensor(mat_imag.T, dtype=dtype)
    return mat_real, mat_imag


class _IRFFTDecomp(nn.Module):
    def __init__(self, n_fft: int, n_stages: int):
        super().__init__()

        mat_real, mat_imag = get_rfft2fft_matrices(n_fft)
        self.mat_real = nn.Parameter(mat_real, requires_grad=False)
        self.mat_imag = nn.Parameter(mat_imag, requires_grad=False)

        self.ifft = IFFT(n_fft, n_stages)

    def forward(self, re, im):
        re = torch.matmul(re, self.mat_real.t())
        im = torch.matmul(im, self.mat_imag.t())

        # run and discard the imaginary component
        y, __ = self.ifft(re, im)
        return y


class IRFFT(nn.Module):
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
            self.irfft = _IRFFTDirect(n_fft)
        else:
            self.irfft = _IRFFTDecomp(n_fft, n_stages)

    def forward(self, re: Tensor, im: Tensor) -> Tensor:
        """Compute the IRFFT given tensors holding the real and imaginary components.

        Arguments:
            re (Tensor): real-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``
            im (Tensor): imaginary-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``

        Returns:
            Tensor, real-valued inversion of the input RFFT.
        """
        return self.irfft(re, im)
