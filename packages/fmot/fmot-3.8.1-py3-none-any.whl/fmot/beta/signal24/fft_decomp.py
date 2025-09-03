"""int24 RFFT and IRFFT implementations, based on GMACv2"""
import torch
from torch import nn, Tensor
from fmot.nn import SuperStructure
import numpy as np
from .higher_precision_matmul import get_higher_precision_matmul
from fmot.nn import GMACv2
from fmot.precisions import int8, int16, int24, Precision
from fmot.qat.annotated_tensors import copy_annotations
from typing import Union, Literal
from fmot.nn.fft.fft import auto_n_stages


class FFTGradientBypass(torch.autograd.Function):
    """Hack: gradient bypass to enable efficient and accurate FFT gradients"""

    @staticmethod
    def forward(ctx, input, re, im):
        # Save the size of the FFT (last dimension) for use in backward.
        ctx.N = input.shape[-1]
        return re, im

    @staticmethod
    def backward(ctx, grad_re, grad_im):
        # Retrieve the FFT length.
        N = ctx.N
        # The gradient w.r.t. the input is given by the conjugate transpose of the FFT matrix,
        # which is equivalent to an IFFT. Since torch.fft.ifft includes a 1/N normalization,
        # we multiply by N to get the correct gradient.
        grad_output = grad_re + 1j * grad_im
        grad_input: torch.Tensor = torch.fft.ifft(grad_output) * N
        grad_input = grad_input.real

        return grad_input, None, None


class IRFFTGradBypass(torch.autograd.Function):
    """Hack: gradient bypass to enable efficient and accurate IRFFT gradients"""

    @staticmethod
    def forward(ctx, output, re, im, n):
        ctx.N = n  # Save the output length for the backward pass.
        return output

    @staticmethod
    def backward(ctx, grad_output):
        n = ctx.N
        # The adjoint of irfft is rfft with the same output length and an extra 1/n factor.
        grad_input = torch.fft.rfft(grad_output, n=n) / n
        grad_re = grad_input.real
        grad_im = grad_input.imag

        # No gradient for the integer n.
        # Bypass gradient directy to re, im
        return None, grad_re, grad_im, None


def get_fft_matrices(n_fft, dtype=torch.float32):
    mat = np.fft.fft(np.eye(n_fft))
    m_real = torch.tensor(mat.real, dtype=dtype)
    m_imag = torch.tensor(mat.imag, dtype=dtype)
    return m_real, m_imag


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
    """
    Applies N-sample DFT to real signal, returning real and imaginary parts as separate tensors.
    Applies the DFT at higher precision (specified via act_precision and weight_precision)

    Arguments:
        n_fft (int): FFT size
        act_precision (Precision): activation precision, int16 or int24
        weight_precision (Precision): DFT matrix precision, int8 or int16
    """

    def __init__(
        self,
        n_fft: int,
        act_precision: Precision,
        weight_precision: Precision,
        bits_headroom=0,
    ):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = get_higher_precision_matmul(
            fft_real,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )
        self.fft_imag = get_higher_precision_matmul(
            fft_imag,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )

    def forward(self, x):
        y_real = self.fft_real(x)
        y_imag = self.fft_imag(x)
        return y_real, y_imag


class IDFT(nn.Module):
    """
    Applies N-sample IDFT to real/imag channes, returning a real-valued waveform.
    Applies the IDFT at higher precision (specified via act_precision and weight_precision)

    Arguments:
        n_fft (int): FFT size
        act_precision (Precision): activation precision, int16 or int24
        weight_precision (Precision): DFT matrix precision, int8 or int16
    """

    def __init__(
        self,
        n_fft,
        act_precision: Precision,
        weight_precision: Precision,
        bits_headroom=0,
    ):
        super().__init__()
        self.n_fft = n_fft
        fft_real, fft_imag = get_ifft_matrices(n_fft, dtype=torch.float32)
        self.fft_real = get_higher_precision_matmul(
            fft_real,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )
        self.fft_imag = get_higher_precision_matmul(
            fft_imag,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )
        self.add = GMACv2(
            act_precision, torch.tensor([1, 1]), bits_headroom=bits_headroom
        )
        self.sub = GMACv2(
            act_precision, torch.tensor([1, -1]), bits_headroom=bits_headroom
        )

    def forward(self, re, im):
        y_real = self.sub([], [], [self.fft_real(re), self.fft_imag(im)])
        y_imag = self.add([], [], [self.fft_imag(re), self.fft_real(im)])
        return y_real, y_imag


class GMAC_ADD(nn.Module):
    def __init__(self, act_precision):
        super().__init__()
        self.gmac = GMACv2(act_precision, torch.tensor([1, 1]))

    def forward(self, x, y):
        return self.gmac([], [], [x, y])


class GMAC_SUB(nn.Module):
    def __init__(self, act_precision):
        super().__init__()
        self.gmac = GMACv2(act_precision, torch.tensor([1, -1]))

    def forward(self, x, y):
        return self.gmac([], [], [x, y])


class SIMPLE_ADD(nn.Module):
    def forward(self, x, y):
        return x + y


class SIMPLE_SUB(nn.Module):
    def forward(self, x, y):
        return x - y


class GMAC_TODD(nn.Module):
    def __init__(self, act_precision: Precision):
        super().__init__()

        self.gmac = GMACv2(act_precision)

    def forward(self, x1, y1, x2, y2):
        return self.gmac([x1, x2], [y1, y2], [])


class SIMPLE_TODD(nn.Module):
    def forward(self, x1, y1, x2, y2):
        return x1 * y1 + x2 * y2


class GMAC_MUL(nn.Module):
    def __init__(self, act_precision: Precision):
        super().__init__()

        self.gmac = GMACv2(act_precision)

    def forward(self, x, y):
        return self.gmac([x], [y], [])


class SIMPLE_MUL(nn.Module):
    def forward(self, x, y):
        return x * y


class FFTwiddle(nn.Module):
    def __init__(
        self, n_fft: int, act_precision: Precision, inv=False, bits_headroom=0
    ):
        super().__init__()
        self.n_fft = n_fft
        twid_real, twid_imag = get_complex_twiddle(n_fft, inv=inv)
        self.twid_real = nn.Parameter(twid_real, requires_grad=False)
        self.twid_imag = nn.Parameter(twid_imag, requires_grad=False)
        self.neg_twid_imag = nn.Parameter(-twid_imag, requires_grad=False)

        if act_precision == int24:
            self.add = GMAC_ADD(act_precision)
            self.sub = GMAC_SUB(act_precision)
            self.todd = GMAC_TODD(act_precision)
        else:
            self.add = SIMPLE_ADD()
            self.sub = SIMPLE_SUB()
            self.todd = SIMPLE_TODD()

    def forward(self, even_real, even_imag, odd_real, odd_imag):
        # todd_real = self.twid_real * odd_real - self.twid_imag * odd_imag
        todd_real = self.todd(self.twid_real, odd_real, self.neg_twid_imag, odd_imag)
        # todd_imag = self.twid_real * odd_imag + self.twid_imag * odd_real
        todd_imag = self.todd(self.twid_real, odd_imag, self.twid_imag, odd_real)

        # upper_real = even_real + todd_real
        upper_real = self.add(even_real, todd_real)
        # upper_imag = even_imag + todd_imag
        upper_imag = self.add(even_imag, todd_imag)
        # lower_real = even_real - todd_real
        lower_real = self.sub(even_real, todd_real)
        # lower_imag = even_imag - todd_imag
        lower_imag = self.sub(even_imag, todd_imag)

        real = torch.cat([upper_real, lower_real], dim=-1)
        imag = torch.cat([upper_imag, lower_imag], dim=-1)

        return real, imag

    def extra_repr(self) -> str:
        return f"n_fft={self.n_fft}"


class FFTwiddleV2(nn.Module):
    def __init__(
        self, n_fft: int, act_precision: Precision, inv=False, bits_headroom=0
    ):
        super().__init__()
        self.n_fft = n_fft
        twid_real, twid_imag = get_complex_twiddle(n_fft, inv=inv)
        self.twid_real = nn.Parameter(twid_real, requires_grad=False)
        self.twid_imag = nn.Parameter(twid_imag, requires_grad=False)

        if act_precision == int24:
            self.add = GMAC_ADD(act_precision)
            self.sub = GMAC_SUB(act_precision)
            self.mul = GMAC_MUL(act_precision)
            self.todd = GMAC_TODD(act_precision)
        else:
            self.add = SIMPLE_ADD()
            self.sub = SIMPLE_SUB()
            self.mul = SIMPLE_MUL()
            self.todd = SIMPLE_TODD()

    def forward(self, even_real, even_imag, odd_real, odd_imag):
        # todd_real = self.twid_real * odd_real - self.twid_imag * odd_imag
        todd_real_1 = self.mul(self.twid_real, odd_real)
        todd_real_2 = self.mul(self.twid_imag, odd_imag)
        todd_real = self.sub(todd_real_1, todd_real_2)
        # todd_imag = self.twid_real * odd_imag + self.twid_imag * odd_real
        todd_imag = self.todd(self.twid_real, odd_imag, self.twid_imag, odd_real)

        # upper_real = even_real + todd_real
        upper_real = self.add(even_real, todd_real)
        # upper_imag = even_imag + todd_imag
        upper_imag = self.add(even_imag, todd_imag)
        # lower_real = even_real - todd_real
        lower_real = self.sub(even_real, todd_real)
        # lower_imag = even_imag - todd_imag
        lower_imag = self.sub(even_imag, todd_imag)

        real = torch.cat([upper_real, lower_real], dim=-1)
        imag = torch.cat([upper_imag, lower_imag], dim=-1)

        return real, imag


class FFTPermuter(nn.Module):
    def __init__(
        self, n_fft: int, n_stages: int, act_precision: Precision, bits_headroom=0
    ):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages
        self.n_chunks = 2**n_stages

        perm = get_partial_bit_reversal_matrix(n_fft, n_stages).T

        self.perm = get_higher_precision_matmul(
            perm,
            act_precision,
            weight_precision=int8,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )

    def forward(self, x):
        y = self.perm(x)
        return torch.chunk(y, self.n_chunks, dim=-1)


class IFFTNormalizer(nn.Module):
    def __init__(self, n_fft, n_stages: int, act_precision: Precision, bits_headroom=0):
        super().__init__()
        self.n_fft = n_fft
        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)
        self.n_stages = n_stages
        self.factor = 2 ** (-n_stages)
        self.gmac = GMACv2(
            act_precision, torch.tensor([self.factor]), bits_headroom=bits_headroom
        )

    def forward(self, x):
        return self.gmac([], [], [x])


class FFT(SuperStructure):
    """Sparse decomposition of FFT, with higher-precision numerical quantization.

    Arguments:
        n_fft (int): FFT size
        n_stages (int): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Must satisfy ``n_stages < floor(log2(n_fft))``.
        act_precision (Precision, optional): Activation bitwidth, int16 or int24. Default int16.
        weight_precision (Precision, optional): DFT weight matrix precision, int8 or int16. Default int16.
    """

    def __init__(
        self,
        n_fft: int,
        act_precision: Precision,
        weight_precision: Precision,
        n_stages: int = "auto",
        bits_headroom=0,
    ):
        super().__init__()

        self.n_fft = n_fft
        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)
        self.n_stages = n_stages
        assert (
            n_fft / 2**n_stages % 1 == 0
        ), f"Cannot decompose {n_fft} with {n_stages} power-of-2 stages"

        self.dft = DFT(
            n_fft=n_fft // 2**n_stages,
            act_precision=act_precision,
            weight_precision=weight_precision,
            bits_headroom=bits_headroom,
        )

        self.permuter = None
        self.twiddle_states = None

        if n_stages > 0:
            self.permuter = FFTPermuter(
                n_fft,
                n_stages,
                act_precision=act_precision,
                bits_headroom=bits_headroom,
            )
            self.twiddle_stages = nn.ModuleList()

            stage_size = n_fft // 2 ** (n_stages - 1)
            num_calls = n_fft // stage_size
            for _ in range(n_stages):
                self.twiddle_stages.append(
                    FFTwiddle(
                        stage_size,
                        act_precision=act_precision,
                        inv=False,
                        bits_headroom=bits_headroom,
                    )
                )
                stage_size = stage_size * 2
                num_calls = num_calls // 2

    @torch.jit.ignore()
    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """
        Arguments:
            x (Tensor): real-valued tensor of shape (*, n_fft)
        Returns:
            - (re, im): two tensors of shape (*, n_fft)
                The first holds the real-part, and the second holds the imaginary part
        """

        if self.permuter is None:
            real, imag = self.dft(x)

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

        # hack: gradient-bypass
        real_bp, imag_bp = FFTGradientBypass.apply(x, real, imag)

        # copy annotations:
        if hasattr(real, "quantized"):
            copy_annotations(real, real_bp)
            copy_annotations(imag, imag_bp)
        if hasattr(real, "proto"):
            real_bp.proto = real.proto
            imag_bp.proto = imag.proto

        return real_bp, imag_bp

    def extra_repr(self) -> str:
        f"n_fft: {self.n_fft} n_stages: {self.n_stages}"


class _RFFTDecompWithGMAC(nn.Module):
    def __init__(self, n_fft, n_stages, act_precision, weight_precision, bits_headroom):
        super().__init__()
        self.n_fft = n_fft
        self.n_stages = n_stages

        self.fft = FFT(
            n_fft,
            n_stages=n_stages,
            act_precision=act_precision,
            weight_precision=weight_precision,
            bits_headroom=bits_headroom,
        )
        self._split0 = int(np.floor(n_fft / 2 + 1))
        self._split1 = n_fft - self._split0

    def forward(self, x):
        yre, yim = self.fft(x)
        yre, __ = torch.split(yre, [self._split0, self._split1], -1)
        yim, __ = torch.split(yim, [self._split0, self._split1], -1)
        return yre, yim


class _RFFTDirectWithGMAC(nn.Module):
    def __init__(self, n_fft, act_precision, weight_precision, bits_headroom=0):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_fft_matrices(n_fft, dtype=torch.float32)
        n_rfft = int(np.floor(n_fft / 2 + 1))
        m_real = m_real[:n_rfft]
        m_imag = m_imag[:n_rfft]

        self.rfft_real = get_higher_precision_matmul(
            m_real,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )
        self.rfft_imag = get_higher_precision_matmul(
            m_imag,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )

    def forward(self, x):
        re = self.rfft_real(x)
        im = self.rfft_imag(x)
        return re, im


class RFFT(nn.Module):
    """Sparse decomposition of RFFT, with higher-precision numerical quantization options.

    Arguments:
        n_fft (int): FFT size
        n_stages (int, optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the RDFT. Must satisfy ``n_stages < floor(log2(n_fft))``.
            Default 0.
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
    """

    def __init__(
        self,
        n_fft: int,
        act_precision=int16,
        weight_precision=int16,
        n_stages: int = 0,
        bits_headroom=0,
    ):
        super().__init__()
        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)
        if n_stages == 0:
            self.rfft = _RFFTDirectWithGMAC(
                n_fft, act_precision, weight_precision, bits_headroom=bits_headroom
            )
        else:
            self.rfft = _RFFTDecompWithGMAC(
                n_fft,
                n_stages,
                act_precision,
                weight_precision,
                bits_headroom=bits_headroom,
            )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """
        Arguments:
            x (Tensor): real-valued tensor of shape (*, n_fft)
        Returns:
            - (re, im): two tensors of shape (*, n_freq)
                The first holds the real-part, and the second holds the imaginary part.
                Here, ``n_freq`` is ``n_fft // 2 + 1``
        """
        return self.rfft(x)


class _DenseIRFFT(nn.Module):
    """Dense IRFFT calculation, supporting higher numerical quantization options.

    Arguments:
        n_fft (int): the FFT window-size (not the number of rfft bins)
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
        window_out (int, optional): if not None, will truncate the IRFFT to only return the
            final "window_out" samples, useful for asymmetric-istft.
    """

    def __init__(
        self,
        n_fft,
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        window_out=None,
        bits_headroom=0,
    ):
        super().__init__()
        self.n_fft = n_fft
        m_real, m_imag = get_irfft_matrices(n_fft, dtype=torch.float32)

        if window_out is not None:
            m_real = m_real[:, -window_out:]
            m_imag = m_imag[:, -window_out:]

        self.irfft_real = get_higher_precision_matmul(
            m_real.T,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )
        self.irfft_imag = get_higher_precision_matmul(
            m_imag.T,
            act_precision,
            weight_precision,
            requires_grad=False,
            bits_headroom=bits_headroom,
        )

        self.add = GMACv2(
            act_precision, torch.tensor([1, 1]), bits_headroom=bits_headroom
        )

    def forward(self, re, im):
        return self.add([], [], [self.irfft_real(re), self.irfft_imag(im)])


class _SparseIFFT(nn.Module):
    """Sparse decomposition of IFFT, supporting higher numerical quantization options.

    Arguments:
        n_fft (int): the FFT window-size (not the number of rfft bins)
        n_stages (int, optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the RDFT. Must satisfy ``n_stages < floor(log2(n_fft))``.
            Default 0.
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
    """

    def __init__(
        self,
        n_fft: int,
        n_stages: int = 0,
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        bits_headroom=0,
    ):
        super().__init__()

        self.n_fft = n_fft
        self.n_stages = n_stages
        assert (
            n_fft / 2**n_stages % 1 == 0
        ), f"Cannot decompose {n_fft} with {n_stages} power-of-2 stages"

        self.idft = IDFT(
            n_fft // 2**n_stages,
            act_precision,
            weight_precision,
            bits_headroom=bits_headroom,
        )

        if n_stages > 0:
            self.permuter = FFTPermuter(
                n_fft, n_stages, act_precision, bits_headroom=bits_headroom
            )
            self.twiddle_stages = nn.ModuleList()

            stage_size = n_fft // 2 ** (n_stages - 1)
            num_calls = n_fft // stage_size
            for _ in range(n_stages):
                self.twiddle_stages.append(
                    FFTwiddle(
                        stage_size, act_precision, inv=True, bits_headroom=bits_headroom
                    )
                )
                stage_size = stage_size * 2
                num_calls = num_calls // 2

            self.normalizer = IFFTNormalizer(
                n_fft, n_stages, act_precision, bits_headroom=bits_headroom
            )

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
    """Sparse decomposition of IRFFT, supporting higher numerical quantization options.

    Arguments:
        n_fft (int): the FFT window-size (not the number of rfft bins)
        n_stages (int, optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the RDFT. Must satisfy ``n_stages < floor(log2(n_fft))``.
            Default 0.
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
    """

    def __init__(
        self,
        n_fft: int,
        n_stages: int = 0,
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        bits_headroom=0,
    ):
        super().__init__()

        mat_real, mat_imag = get_rfft2fft_matrices(n_fft)
        self.rfft_to_fft_real = get_higher_precision_matmul(
            mat_real, act_precision, 8, requires_grad=False, bits_headroom=bits_headroom
        )
        self.rfft_to_fft_imag = get_higher_precision_matmul(
            mat_imag, act_precision, 8, requires_grad=False, bits_headroom=bits_headroom
        )

        self.ifft = _SparseIFFT(
            n_fft,
            n_stages,
            act_precision,
            weight_precision,
            bits_headroom=bits_headroom,
        )

    def forward(self, re, im):
        re = self.rfft_to_fft_real(re)
        im = self.rfft_to_fft_imag(im)

        # run and discard the imaginary component
        y, __ = self.ifft(re, im)
        return y


class IRFFT(SuperStructure):
    """Sparse decomposition of IRFFT, with support for higher numerical quantization options.

    Arguments:
        n_fft (int): FFT size
        n_stages (int, optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the IRDFT. Must satisfy ``n_stages < floor(log2(n_fft))``.
            Default 0.
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
    """

    def __init__(
        self,
        n_fft: int,
        n_stages: int = "auto",
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        bits_headroom=0,
    ):
        super().__init__()
        self.n_fft = n_fft

        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)

        if n_stages == 0:
            self.irfft = _DenseIRFFT(
                n_fft,
                act_precision,
                weight_precision,
                window_out=None,
                bits_headroom=bits_headroom,
            )
        else:
            self.irfft = _IRFFTDecomp(
                n_fft,
                n_stages,
                act_precision,
                weight_precision,
                bits_headroom=bits_headroom,
            )

    @torch.jit.ignore
    def forward(self, re: Tensor, im: Tensor) -> Tensor:
        """Compute the IRFFT given tensors holding the real and imaginary components.

        Arguments:
            re (Tensor): real-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``
            im (Tensor): imaginary-part of the RFFT to invert, shape ``(*, n_fft//2 + 1)``

        Returns:
            Tensor, real-valued inversion of the input RFFT.
        """
        output = self.irfft(re, im)
        output_bp = IRFFTGradBypass.apply(output, re, im, self.n_fft)

        # copy annotations:
        if hasattr(output, "quantized"):
            copy_annotations(output, output_bp)
        if hasattr(output, "proto"):
            output_bp.proto = output.proto

        return output_bp
