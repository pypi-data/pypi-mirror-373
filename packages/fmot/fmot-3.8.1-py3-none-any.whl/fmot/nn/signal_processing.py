import torch
import math
from torch import nn
import fmot
import numpy as np
from typing import List, Tuple
from torch import Tensor
from fmot.functional import cos_arctan
from . import atomics
from . import Sequencer
from .composites import TuningEpsilon
from python_speech_features.base import get_filterbanks
from .super_structures import SuperStructure


def _get_norm(normalized):
    norm = None
    if normalized:
        norm = "ortho"
    return norm


def get_rfft_matrix(size, normalized=False):
    weight = np.fft.rfft(np.eye(size), norm=_get_norm(normalized))
    w_real, w_imag = np.real(weight), np.imag(weight)
    return torch.tensor(w_real).float(), torch.tensor(w_imag).float()


def get_irfft_matrix(size, normalized=False):
    in_size = size // 2 + 1
    w_real = np.fft.irfft(np.eye(in_size), n=size, norm=_get_norm(normalized))
    w_imag = np.fft.irfft(np.eye(in_size) * 1j, n=size, norm=_get_norm(normalized))
    return torch.tensor(w_real).float(), torch.tensor(w_imag).float()


def get_mel_matrix(sr, n_dft, n_mels=128, fmin=0.0, fmax=None, **kwargs):
    mel_matrix = get_filterbanks(
        nfilt=n_mels, nfft=n_dft, samplerate=sr, lowfreq=fmin, highfreq=fmax
    )
    return torch.tensor(mel_matrix, dtype=torch.float32)


def get_dct_matrix(n, n_out=None, dct_type=2, normalized=False):
    N = n
    if n_out is None:
        n_out = n
    K = n_out

    if K > N:
        raise ValueError(
            f"DCT cannot have more output features ({K}) than input features ({N})"
        )
    matrix = None
    if dct_type == 1:
        ns = np.arange(1, N - 1)
        ks = np.arange(K)
        matrix = np.zeros((N, K))
        matrix[0, :] = 1
        matrix[-1, :] = -(1**ks)
        matrix[1:-1, :] = 2 * np.cos(
            (np.pi * ks.reshape(1, -1) * ns.reshape(-1, 1)) / (N - 1)
        )
    elif dct_type == 2:
        ns = np.arange(N).reshape(-1, 1)
        ks = np.arange(K).reshape(1, -1)
        matrix = 2 * np.cos(np.pi * ks * (2 * ns + 1) / (2 * N))
        if normalized:
            matrix[:, 0] /= np.sqrt(4 * N)
            matrix[:, 1:] /= np.sqrt(2 * N)
    elif dct_type == 3:
        ns = np.arange(1, N).reshape(-1, 1)
        ks = np.arange(K).reshape(1, -1)
        matrix = np.zeros((N, K))
        matrix[0, :] = 1
        matrix[1:, :] = 2 * np.cos(np.pi * (2 * ks + 1) * ns / (2 * N))
        if normalized:
            matrix[0, :] /= np.sqrt(N)
            matrix[1:, :] /= np.sqrt(2 * N)
    elif dct_type == 4:
        ns = np.arange(N).reshape(-1, 1)
        ks = np.arange(K).reshape(1, -1)
        matrix = 2 * np.cos(np.pi * (2 * ks + 1) * (2 * ns + 1) / (4 * N))
        if normalized:
            matrix /= np.sqrt(2 * N)
    else:
        raise ValueError(f"DCT type {dct_type} is not defined.")
    return torch.tensor(matrix).float()


class DCT(nn.Module):
    r"""
    Discrete Cosine Transformation.

    Performs the DCT on an input by multiplying it with the DCT matrix.
    DCT Types :attr:`1`, :attr:`2`, :attr:`3`, and :attr:`4` are implemented. See
    `scipy.fftpack.dct <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.dct.html>`_
    for reference about the different DCT types. Type :attr:`2` is default.

    Args:
        in_features (int): Length of input signal that is going through the DCT
        out_features (int): Number of desired output DCT features. Default is :attr:`in_features`.
            Must satisfy :math:`\text{out_features} \leq \text{in_features}`
        dct_type (int): Select between types :attr:`1`, :attr:`2`, :attr:`3`, and :attr:`4`.
            Default is :attr:`2`.
        normalized (bool): If True and :attr:`dct_type` is :attr:`2`, :attr:`3`, or :attr:`4`,
            the DCT matrix will be normalized. Has no effect for :attr:`dct_type=1`.
            Setting normalized to True is equivalent to :attr:`norm="orth"` in
            `scipy.fftpack.dct <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.dct.html>`_

    Shape:
        - Input: :math:`(*, N)` where :math:`N` is :attr:`in_features`
        - Output: :math:`(*, K)` where :math:`K` is :attr:`out_features`, or :attr:`in_features` if
          :attr:`out_features` is not specified.
    """
    report_supported = True

    def __init__(self, in_features, out_features=None, dct_type=2, normalized=True):
        super().__init__()
        weight = get_dct_matrix(
            n=in_features, n_out=out_features, dct_type=dct_type, normalized=normalized
        )
        self.weight = nn.Parameter(weight, requires_grad=False)

    def forward(self, x):
        r"""
        Args:
            x (Tensor): Input, of shape :math:`(*, N)`
        Returns:
            - Output, of shape :math:`(*, K)` where :math:`K` is :attr:`out_features`,
                or :attr:`in_features` if :attr:`out_features` is not specified.
        """
        return torch.matmul(x, self.weight)


class MaxMin(nn.Module):
    def __init__(self):
        super().__init__()
        self.gt0 = atomics.Gt0()

    def forward(self, x, y):
        x_g = self.gt0(x - y)
        y_g = 1 - x_g
        max_els = x_g * x + y_g * y
        min_els = y_g * x + x_g * y
        return max_els, min_els


class LogEps(nn.Module):
    r"""
    Natural logarithm with a minimum floor. Minimum floor is automatically
    tuned when exposed to data. The minimum floor ensures numerical stability.

    Arguments:
        eps: relative epsilon in TuningEpsilon, must be >= 2**-13.
    
    Returns:

        .. math::

            \text{output} = \begin{cases}
                \log(x) & x > \epsilon \\
                \log(\epsilon) & x \leq \epsilon
            \end{cases}
    """
    report_supported = True

    def __init__(self, eps=2 ** (-13)):
        super().__init__()

        if eps < 2**-13:
            raise ValueError(
                "LogEps eps parameter must be >= 2^-13 to avoid numerical issues."
            )

        self.add_eps = TuningEpsilon(eps)

    def forward(self, x):
        """ """
        x = self.add_eps(x)
        return torch.log(x)


class Magnitude(nn.Module):
    r"""
    Computes magnitude from real and imaginary parts.

    Mathematically equivalent to

    .. math::

        \text{mag} = \sqrt{\text{Re}^2 + \text{Im}^2},

    but designed to compress the signal as minimally as possible when quantized:

    .. math::

        &a_{max} = \text{max}(|\text{Re}|, |\text{Im}|) \\
        &a_{min} = \text{min}(|\text{Re}|, |\text{Im}|) \\
        &\text{mag} = a_{max}\sqrt{1 + \frac{a_{min}}{a_{max}}^2}

    .. note::

        .. math::

            \sqrt{1 + x^2} = \cos{\arctan{x}}
    """
    report_supported = True

    def __init__(self):
        super().__init__()
        self.add_epsilon = TuningEpsilon()
        self.max_min = MaxMin()
        self.mul = atomics.VVMul()

    def forward(self, real, imag):
        """
        Args:
            real (Tensor): Real part of input
            imag (Tensor): Imaginary part of input

        Returns:
            - Magnitude
        """
        a, b = self.max_min(real.abs(), imag.abs())
        eta = b / self.add_epsilon(a)
        eta_p = cos_arctan(eta)
        return self.mul(a, eta_p)


class BarniMagnitude(nn.Module):
    """An approximation to the magnitude of cartesian r/i complex numbers.

    Uses the Barni approximation:

        L2(a0, a1) = d * (k0 * |a0| + k1 * |a1|)

    where the elements a0 and a1 are sorted such that |a0| >= |a1|.

    The coefficients d, k0, k1 are solve the minimax problem over the unit circle.
    Equivalently, they are chosen to minimize the maximum relative error.
    """

    report_supported = True

    def __init__(self):
        super().__init__()

        k0 = 1
        k1 = math.sqrt(2) - 1
        d = 2 / (1 + math.sqrt(k0**2 + k1**2))

        self.c0 = d * k0
        self.c1 = d * k1

    def forward(self, re, im):
        r = torch.abs(re)
        i = torch.abs(im)

        # a0 = max(r, i)
        # a1 = min(r, i)
        ramp = torch.relu(r - i)
        a0 = i + ramp
        a1 = r - ramp

        res = self.c0 * a0 + self.c1 * a1
        return res


POLAR_MAG_CLASS = Magnitude


class _EMA(Sequencer):
    """Sequencer implementation of EMA"""

    def __init__(self, features: int, alpha: float, dim: int):
        super().__init__([[features]], 0, seq_dim=dim)
        assert 0 < alpha < 1
        self.alpha = alpha
        self.om_alpha = 1 - alpha

    @torch.jit.export
    def step(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        (y,) = state
        y = self.alpha * y + self.om_alpha * x
        return y, [y]


class EMA(nn.Module):
    """Exponential Moving Average

    Arguments:
        features (int): number of input features
        alpha (float): smoothing coefficient, between 0 and 1. Time constant is ``-1/log(alpha)`` frames
        dim (int): dimension to apply exponential moving average to. Should be the temporal/sequential dimension
    """

    report_supported = True

    def __init__(self, features: int, alpha: float, dim: int):
        super().__init__()
        self.ema = _EMA(features, alpha, dim)

    def forward(self, x):
        x, __ = self.ema(x)
        return x


class _FirstFrameBiasedEMA(Sequencer):
    """Use an additional status variable to track whether the current frame is the
    first frame or not.

    for the first frame:
        y[0] = x[0]

    for all subsequent frames:
        y[t] = alpha * y[t-1] + (1-alpha) * x[t]
    """

    def __init__(self, num_channels, alpha, seq_dim=1):
        super().__init__([[num_channels], [1]], batch_dim=0, seq_dim=seq_dim)
        self.alpha = alpha
        self.om_alpha = 1 - alpha

    @torch.jit.export
    def step(self, x: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        y_prev, not_first_frame = state

        y_updated = self.alpha * y_prev + self.om_alpha * x
        y_next = not_first_frame * y_updated + (1 - not_first_frame) * x
        not_first_frame = 1 + 0 * not_first_frame

        return y_next, [y_next, not_first_frame]


class FirstFrameBiasedEMA(nn.Module):
    def __init__(self, num_channels: int, alpha: float, dim=1):
        super().__init__()
        self.ema = _FirstFrameBiasedEMA(num_channels, alpha, seq_dim=dim)

    def forward(self, x):
        y, _ = self.ema(x)
        return y


class _AsymmetricEMA(Sequencer):
    """Use a different smoothing coefficient depending on whether the signal is rising or falling."""

    def __init__(self, num_channels, alpha_rise, alpha_fall, seq_dim=1):
        super().__init__([[num_channels], [1]], batch_dim=0, seq_dim=seq_dim)
        self.alpha_rise = alpha_rise
        self.alpha_fall = alpha_fall

        self.gt0 = atomics.Gt0()

    @torch.jit.export
    def step(self, x: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        y_prev, not_first_frame = state

        falling = self.gt0(y_prev - x)
        alpha = falling * self.alpha_fall + (1 - falling) * self.alpha_rise
        om_alpha = 1 - alpha

        y_updated = alpha * y_prev + om_alpha * x
        y_next = not_first_frame * y_updated + (1 - not_first_frame) * x
        not_first_frame = 1 + 0 * not_first_frame

        return y_next, [y_next, not_first_frame]


class AsymmetricEMA(nn.Module):
    def __init__(self, num_channels: int, alpha_rise: float, alpha_fall: float, dim=1):
        super().__init__()
        self.ema = _AsymmetricEMA(
            num_channels, alpha_rise=alpha_rise, alpha_fall=alpha_fall, seq_dim=dim
        )

    def forward(self, x):
        y, _ = self.ema(x)
        return y


class MelFilterBank(nn.Module):
    r"""
    Project FFT bins into Mel-Frequency bins.

    Applies a linear transformation to project FFT bins into Mel-frequency bins.

    Args:
        sr (int): audio sampling rate (in Hz)
        n_fft (int): number of FFT frequencies
        n_mels (int): number of mel-frequencies to create
        fmin (float): lowest frequency (in Hz), default is 0
        fmax (float): maximum frequency (in Hz). If :attr:`None`, the Nyquist frequency
            :attr:`sr/2.0` is used. Default is :attr:`None`.
        **kwargs: keyword arguments to pass to
            `librosa.filters.mel <https://librosa.org/doc/latest/generated/librosa.filters.mel.html>`_
            when generating the mel transform matrix

    Shape:
        - Input: :math:`(*, C_{in})` where :math:`*` is any number of dimensions and
          :math:`C_{in} = \lfloor \text{n_dft}/2 + 1 \rfloor`
        - Output: :math:`(*, \text{n_mels})`
    """
    report_supported = True

    def __init__(self, sr, n_fft, n_mels=128, fmin=0.0, fmax=None, **kwargs):
        super().__init__()
        weight = get_mel_matrix(sr, n_fft, n_mels, fmin, fmax, **kwargs)
        self.weight = nn.Parameter(weight.t(), requires_grad=False)

    def forward(self, x):
        """"""
        return torch.matmul(x, self.weight)


class InverseMelFilterBank(nn.Module):
    """
    Implements the Inverse Mel Filter Bank, which converts the Mel scale spectrogram back into the linear frequency domain.

    Attributes:
        weight (nn.Parameter): The weight matrix, computed using the inverse of the Mel filter bank matrix.
    """

    report_supported = True

    def __init__(
        self,
        sr: int,
        n_fft: int,
        n_mels: int = 128,
        fmin: float = 0.0,
        mode: str = "transpose",
        fmax: float = None,
        **kwargs,
    ):
        """
        Initializes the InverseMelFilterBank.

        Args:
            sr (int): Sample rate of the input audio signal.
            n_fft (int): Number of FFT points in the STFT.
            n_mels (int, optional): Number of Mel filters. Defaults to 128.
            fmin (float, optional): Minimum frequency of the Mel filter bank. Defaults to 0.0.
            mode (str, optional): The method to use for computing the inverse Mel filter bank matrix.
                                  Options: 'transpose', 'pinv'. Defaults to 'transpose'.
            fmax (float, optional): Maximum frequency of the Mel filter bank. Defaults to None.
        """
        super().__init__()
        mel_matrix = get_mel_matrix(
            sr, n_fft, n_mels, fmin, fmax, **kwargs
        ).T  # (N_FFTS, N_MELS)

        if mode == "transpose":
            inv_mel_matrix = mel_matrix.T  # (N_MELS, N_FFT)
        elif mode == "transpose_stft_norm":
            inv_mel_matrix = mel_matrix.T  # (N_MELS, N_FFT)
            inv_mel_matrix = self.normalize_inverse_mel_matrix_columns(
                inv_mel_matrix=inv_mel_matrix
            )  # (N_MELS, N_FFT)
        elif mode == "pinv":
            inv_mel_matrix = torch.linalg.pinv(mel_matrix)  # (N_MELS, N_FFT)

        self.weight = nn.Parameter(
            inv_mel_matrix, requires_grad=False
        )  # (N_MELS, N_FFT)

    @staticmethod
    def normalize_inverse_mel_matrix_columns(inv_mel_matrix, eps=1e-7):
        """
        Normalize the columns of the inverse Mel matrix. This is done to ensure that a Mel-domain
        matrix of all ones is transformed to a STFT-domain matrix of all ones. In essence,
        it scales each column of the matrix so that the sum of its elements is equal to 1.

        This normalization step is important in the context of spectrogram inversion,
        where the Mel matrix is used to map a STFT (Short-Time Fourier Transform) spectrogram
        to a Mel spectrogram and vice versa. The normalization ensures the consistency of this mapping.

        Args:
            inv_mel_matrix (torch.Tensor): Shape: (N_MELS, N_FFTS). The original inverse Mel matrix. This is a 2-D tensor
            where each column represents a frequency band of the Mel scale.
            Shape: (N_MELS, N_FFTS)

        Returns:
            torch.Tensor: Shape: (N_MELS, N_FFTS). The normalized inverse Mel matrix. This matrix has the same dimensions
            as the input but each column of the matrix has been scaled so that the sum of its
            elements is equal to 1.
        """
        # figure out which columns have sum=0. for thos columns, add a small value (eps)
        column_sums = torch.sum(inv_mel_matrix, dim=0)  # Shape:  (N_FFT,)
        zero_cols = torch.where(column_sums == 0)[0]
        inv_mel_matrix[:, zero_cols] = eps

        # Compute the sum of each column in the inverse Mel matrix.
        column_sums = torch.sum(inv_mel_matrix, dim=0)

        # Find the indices of the columns that do not sum to 1.
        non_one_columns = torch.where(column_sums != 1)[0]

        # Normalize each column that does not sum to 1.
        for column in non_one_columns:
            inv_mel_matrix[:, column] = inv_mel_matrix[:, column] / (
                torch.sum(inv_mel_matrix[:, column]) + eps
            )

        return inv_mel_matrix

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Applies the inverse Mel filter bank transformation to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_length, n_mels).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, seq_length, n_fft//2 + 1).
        """
        return torch.matmul(x, self.weight)


class MelTranspose(nn.Linear):
    r"""
    Project Mel-Frequency bins back into FFT bins.

    Args:
        sr (int): audio sampling rate (in Hz)
        n_fft (int): number of FFT frequencies
        n_mels (int): number of mel-frequencies to create
        fmin (float): lowest frequency (in Hz), default is 0
        fmax (float): maximum frequency (in Hz). If :attr:`None`, the Nyquist frequency
            :attr:`sr/2.0` is used. Default is :attr:`None`.

    Shape:
        - Input: :math:`(*, C_{in})` where :math:`*` is any number of dimensions and
          :math:`C_{in} = \lfloor \text{n_dft}/2 + 1 \rfloor`
        - Output: :math:`(*, \text{n_mels})`
    """
    report_supported = True

    def __init__(self, sr, n_fft, n_mels, fmin=0.0, fmax=None):
        super().__init__(out_features=n_fft // 2 + 1, in_features=n_mels, bias=False)
        mat = get_mel_matrix(sr, n_fft, n_mels, fmin, fmax).T
        self.weight = nn.Parameter(mat, requires_grad=False)


class _Atan2(nn.Module):
    """Element-wise arctangent of ``y / x`` with consideration of the quadrant. Returns a new tensor with the
    signed angles in radians between vector ``(x, y)`` and vector ``(1, 0)``. Useful in computation of complex phase.

    .. note::

        Note that input ``x``, the second input, is used as the x-coordinate, while ``y``, the first input, is used as the
        y-coordinate.

    .. note::

        We follow the convention that ``atan2(0, 0) = 0``, which is consistent with PyTorch's behavior

        See https://en.wikipedia.org/wiki/Atan2 for mathematical definition of Atan2.

    """

    def __init__(self):
        super().__init__()
        self.gt0 = fmot.nn.Gt0(pseudo_derivative=False)
        self.pi_halves = math.pi / 2
        self.two_pi = 2 * math.pi
        self.pi = math.pi
        self.eps = fmot.nn.TuningEpsilon(eps=2**-14)

    def forward(self, y, x):
        xgt0 = self.gt0(x)
        ygt0 = self.gt0(y)
        xlte0 = 1 - xgt0

        # offset = { 0,   x > 0
        #          { pi,  x<=0, y > 0
        #          { -pi, x<=0, y <=0
        offset = xlte0 * (self.two_pi * ygt0 - self.pi)

        # compute using just positive values
        # using arctan(-x) = -arctan(x)
        sign = (2 * xgt0 - 1) * (2 * ygt0 - 1)

        # take advantage of arctan(a/b) = -arctan(b/a) + pi/2 for positive b, a
        # to flip the ratio to avoid small denominators

        y_abs = torch.abs(y)
        x_abs = torch.abs(x)

        xgty = self.gt0(x_abs - y_abs)
        ygtex = 1 - xgty
        flip_offset = self.pi_halves * ygtex
        flip_sign = 2 * xgty - 1
        num = y_abs * xgty + x_abs * ygtex
        den = x_abs + y_abs - num

        # res = sign * torch.atan(torch.abs(y) / torch.abs(x)) + offset
        res = (
            sign * (flip_sign * torch.atan(num / self.eps(den)) + flip_offset) + offset
        )

        return res


class _Atan2ViaHalfAngle(nn.Module):
    """Employs arctan half-angle identity to simplify computation. Not
    used due to high numerical error when quantized."""

    def __init__(self):
        super().__init__()
        self.mag = Magnitude()
        self.re_gt0 = fmot.nn.Gt0(pseudo_derivative=False)
        self.im_gt0 = fmot.nn.Gt0(pseudo_derivative=False)
        self.eps = fmot.nn.TuningEpsilon(eps=2**-13)
        self.pi = math.pi

    def forward(self, re, im):
        mag = self.mag(re, im)
        re_gt0 = self.re_gt0(re)
        num = im * re_gt0 + (mag - re) * (1 - re_gt0)
        den = (mag + re) * re_gt0 + im * (1 - re_gt0)

        atan = torch.atan(num / (self.eps(den)))

        im_neq0 = self.im_gt0(im.abs())

        return 2 * atan * im_neq0 + self.pi * (1 - im_neq0)


class _MagNormalizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.mag = POLAR_MAG_CLASS()
        self.eps = TuningEpsilon(eps=2**-14)

    def forward(self, x, y):
        mag = self.mag(x, y)
        rmag = torch.reciprocal(self.eps(mag))
        x = x * rmag
        y = y * rmag
        return x, y


class Atan2(SuperStructure):
    """Element-wise arctangent of ``y / x`` with consideration of the quadrant. Returns a new tensor with the
    signed angles in radians between vector ``(x, y)`` and vector ``(1, 0)``. Useful in computation of complex phase.

    Arguments:
        norm (bool, optional): Whether to normalize inputs ``x`` and ``y`` by sqrt(x^2 + y^2) before performing atan2.
            This does not change the result, but reduces quantization error for small magnitude inputs. Default True.

    .. note::

        Note that input ``x``, the second input, is used as the x-coordinate, while ``y``, the first input, is used as the
        y-coordinate.

    .. note::

        We follow the convention that ``atan2(0, 0) = 0``, which is consistent with PyTorch's behavior

    """

    def __init__(self, norm=True):
        super().__init__()
        self.norm = norm

        if norm:
            self.normalizer = _MagNormalizer()

        self.atan = _Atan2()

    @torch.jit.ignore()
    def forward(self, y, x):
        if self.norm:
            y, x = self.normalizer(y, x)
        return self.atan(y, x)


class MagPhase(nn.Module):
    """Computes elementwise magnitude and phase (in radians) of a complex tensor"""

    report_supported = True

    def __init__(self):
        super().__init__()
        self.mag = POLAR_MAG_CLASS()
        self.eps = TuningEpsilon(eps=2**-14)
        self.atan2 = Atan2(norm=False)

    def forward(self, re: Tensor, im: Tensor) -> Tuple[Tensor, Tensor]:
        mag = self.mag(re, im)
        rmag = torch.reciprocal(self.eps(mag))

        re = re * rmag
        im = im * rmag

        phase = self.atan2(im, re)
        return mag, phase


class Phase(nn.Module):
    """Computes the phase (in radians) of a complex number"""

    report_supported = True

    def __init__(self):
        super().__init__()
        self.atan2 = Atan2(norm=True)

    def forward(self, re, im):
        return self.atan2(im, re)


class PolarToRect(nn.Module):
    """Converts a polar representation of a complex number
    to rectangular form (inverse to MagPhase)."""

    report_supported = True

    def forward(self, mag: Tensor, phase: Tensor) -> Tuple[Tensor, Tensor]:
        re = torch.cos(phase) * mag
        im = torch.sin(phase) * mag
        return re, im
