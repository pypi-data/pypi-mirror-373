import torch
from torch import nn, Tensor
from fmot.nn import Sequencer, SuperStructure, GMACv2, Identity
from fmot.nn.fft.stft import STFTBuffer
from fmot.beta.signal24.fft_decomp import RFFT, IRFFT
from fmot.precisions import Precision, int16, int8, int24
from fmot.beta.signal24.gmac_wrappers import Cast16, Multiply
from fmot.nn.fft.fft import auto_n_stages


class CatLastDim(nn.Module):
    def forward(self, tensors: list[Tensor]):
        return torch.cat(tensors, -1)


class WindowMul(nn.Module):
    def __init__(self, window_fn: Tensor, act_precision: Precision, bits_headroom=0):
        super().__init__()
        self.window_fn = nn.Parameter(window_fn, requires_grad=False)
        self.gmac = GMACv2(act_precision, bits_headroom=bits_headroom)

    def forward(self, x):
        return self.gmac([x], [self.window_fn], [])


class STFT(SuperStructure):
    """Short-Time Fourier Transform

    Arguments:
        n_fft (int): size of FFT, in samples
        hop_size (int): hop size, in samples
        n_stages (int): number of power-of-2 cooley-tukey decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Must satisfy ``n_stages < floor(log2(n_fft))``
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
        window_size (int): window size, in samples. If ``None``, defaults to ``n_fft``
        window_fn (Tensor): Optional window function. Should be a 1D of length ``n_fft``

    This layer returns two versions of the re/im STFT coefficients,
    stored into two tuples:
        - (re_hp, im_hp): high-precision STFT coefficients --> cannot at this time
            be directly consumed by DNN operations, but we can apply a complex
            mask and ISTFT to these
        - (re_16, im_16): int16 STFT coefficients (a cast-down version of the _hp
            coefficents), suitable for DNN operations.

    """

    def __init__(
        self,
        n_fft: int,
        hop_size: int,
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        window_size: int = None,
        n_stages: int = "auto",
        window_fn: Tensor = None,
    ):
        super().__init__()
        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)
        self.n_fft = n_fft
        self.hop_size = hop_size
        if window_size is None:
            window_size = n_fft
        self.window_size = window_size
        self.n_stages = n_stages

        if window_fn is not None:
            self.window_mul = WindowMul(window_fn, act_precision)
        else:
            self.window_mul = Identity()

        if window_size < n_fft:
            raise NotImplementedError("n_fft > window_size not yet supported in STFT")
        elif window_size > n_fft:
            raise ValueError("window_size cannot exceed n_fft")
        else:
            self.zero_catter = Identity()

        self.buffer = STFTBuffer(window_size, hop_size)
        self.rfft = RFFT(
            n_fft,
            n_stages=n_stages,
            act_precision=act_precision,
            weight_precision=weight_precision,
        )

        if act_precision == int24:
            self.cast = Cast16()
        else:
            self.cast = Identity()

    def forward(self, x):
        x, _ = self.buffer(x)
        x = self.window_mul(x)
        x = self.zero_catter(x)
        re, im = self.rfft(x)

        re16, im16 = self.cast(re), self.cast(im)
        return (re, im), (re16, im16)


class _OverlapAdd50pct(Sequencer):
    def __init__(self, hop_size: int, act_precision: Precision, bits_headroom=0):
        super().__init__([[hop_size]], 0, 1)
        self.add = GMACv2(
            act_precision, torch.tensor([1, 1]), bits_headroom=bits_headroom
        )

    @torch.jit.export
    def step(self, x: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        x_curr, x_next = torch.chunk(x, 2, -1)
        (s_curr,) = state
        x = self.add([], [], [x_curr, s_curr])
        return x, [x_next]


class OverlapAdd50pct(nn.Module):
    """50% Overlap-Add Decoding. Takes overlapping waveforms and performs
    overlap-add
    """

    report_supported = True

    def __init__(self, hop_size: int, act_precision: Precision, bits_headroom=0):
        super().__init__()
        self.ola = _OverlapAdd50pct(
            hop_size, act_precision, bits_headroom=bits_headroom
        )

    def forward(self, x):
        y, __ = self.ola(x)
        return y


class WindowMulParam(nn.Module):
    def __init__(self, window_fn: Tensor, act_precision: Precision, bits_headroom=0):
        super().__init__()
        self.window_fn = nn.Parameter(window_fn, requires_grad=False)
        self.mul = GMACv2(act_precision, bits_headroom=bits_headroom)

    def forward(self, x):
        return self.mul([x], [self.window_fn], [])


class MulHalf(nn.Module):
    def __init__(self, act_precision: Precision, bits_headroom=0):
        super().__init__()
        self.mul = GMACv2(
            act_precision, torch.tensor([0.5]), bits_headroom=bits_headroom
        )

    def forward(self, x):
        return self.mul([], [], [x])


def get_synthesis_window(analysis_window: Tensor, hop_length: int):
    analysis_window = analysis_window[-2 * hop_length :]

    cola_tgt = torch.hann_window(2 * hop_length, device=analysis_window.device)

    synth_window = cola_tgt / analysis_window
    # mask out division-by-zero effects
    synth_window.masked_fill_(analysis_window == 0, 0)
    synth_window.masked_fill_(torch.isnan(synth_window), 0)
    synth_window.masked_fill_(torch.isinf(synth_window), 0)

    return synth_window


class ISTFT(nn.Module):
    """Inverse Short-Time Fourier Transform

    Arguments:
        n_fft (int): size of FFT, in samples
        hop_size (int): hop size, in samples
        n_stages (int): number of power-of-2 cooley-tukey decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the IDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
        act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
            int24.
        weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
            int8.
        window_size (int): window size, in samples. If ``None``, defaults to ``n_fft``
        window_fn (Tensor): Optional window function. Should be a 1D of length ``n_fft``


    .. seealso:

        `scipy.signal.stft <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.istft.html>`_ has
        good documentation explaining OLA (see the Note at the bottom of the page)

    .. warning:

        Presently, restricted to the 50% overlap case where ``n_fft == window_size == 2*hop_size``
    """

    report_supported = True

    def __init__(
        self,
        n_fft: int,
        hop_size: int,
        n_stages: int,
        act_precision: Precision = int16,
        weight_precision: Precision = int16,
        window_size: int = None,
        window_fn: Tensor = None,
    ):
        super().__init__()
        if n_stages == "auto":
            n_stages = auto_n_stages(n_fft)
        self.n_fft = n_fft
        self.hop_size = hop_size
        if window_size is None:
            window_size = n_fft

        assert window_size == n_fft, "window_size != n_fft not yet supported in ISTFT"
        assert (
            window_size == 2 * hop_size
        ), r"ISTFT with overlap other than 50% not yet supported in ISTFT"

        self.irfft = IRFFT(
            n_fft,
            n_stages=n_stages,
            act_precision=act_precision,
            weight_precision=weight_precision,
        )
        if window_fn is None:
            self.window_mul = MulHalf(act_precision)
        else:
            synth_window = get_synthesis_window(window_fn, hop_size)
            self.window_mul = WindowMulParam(synth_window, act_precision)
        self.ola = OverlapAdd50pct(hop_size, act_precision)

        if act_precision == int24:
            self.cast = Cast16()
        else:
            self.cast = Identity()

    def forward(self, re: Tensor, im: Tensor) -> Tensor:
        """Compute the ISTFT given tensors holding the real and imaginary spectral components.

        Arguments:
            re (Tensor): real-part of the STFT to invert, shape ``(batch, N, n_fft//2 + 1)``
            im (Tensor): imaginary-part of the STFT to invert, shape ``(batch, N, n_fft//2 + 1)``

        Returns:
            Tensor, real-valued inversion of the input STFT, with overlap-add inversion.
            shape: (batch, N, hop_size)
        """
        winsig = self.irfft(re, im)
        sig = self.window_mul(winsig)
        x = self.ola(sig)
        x = self.cast(x)
        return x


class ReciprocalErrorCorrection(nn.Module):
    """Trick to reduce quantization error on a reciprocal,
    by enforcing that x * approx(1/x) = 1"""

    def forward(self, x, xinv):
        one_approx_v0 = x * xinv
        xinv1 = 2 * xinv - (one_approx_v0) * xinv
        return xinv1


class Abs(nn.Module):
    def forward(self, x):
        return torch.abs(x)


# class L1NormAndInverse(nn.Module):
#     """Computes the L1 Norm of the given tensor, along with its inverse.
#     Clamps the norm between [clamp_dbfs, 0] (in dB) to avoid numerical issues
#     with the reciprocal.

#     Arguments:
#         clamp_dbfs (float): The L1-normalized signal intensity (poor-man's substitute
#             for signal RMS level) will be clamped above this intensity (measured in dBFS)
#             before being normalized. Assuming that the maximum intensity is 0dBFS,
#             this directly relates to the amount of gain that is provided by this stage.
#             Default -35 (dBFS)
#     """

#     def __init__(self, clamp_dbfs: float = -35):
#         super().__init__()
#         self.gmin = 10 ** (clamp_dbfs / 20)
#         self.error_correction = ReciprocalErrorCorrection()
#         self.abs = Abs()

#     def forward(self, x):
#         """
#         Returns:
#          - 1/L1(x)
#          - L1(x)
#         """
#         # compute L1 norm of the signal
#         norm = torch.mean(self.abs(x), dim=-1, keepdim=True)

#         # restrict the norm between gmin and 1 (e.g. 0.1 - 1.0)
#         norm = torch.clamp(norm, self.gmin, 1.0)

#         # pre-compute the inverse gain
#         inorm = 1 / norm

#         # perform error correction (2 iterations) on the inverse signal
#         # inorm = self.error_correction(norm, inorm)
#         # inorm = self.error_correction(norm, inorm)

#         return inorm, norm


# class NormedSTFT(nn.Module):
#     """This STFT layer performs pre-normalization of the waveform before computing the RFFT
#     to improve STFT quantization.

#     Arguments:
#         n_fft (int): size of FFT, in samples
#         hop_size (int): hop size, in samples
#         n_stages (int): number of power-of-2 cooley-tukey decomposition stages. ``n_stages = 0`` yields a
#             dense matrix implementation of the IDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
#         act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
#             int24.
#         weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
#             int8.
#         window_size (int, optional): window size, in samples. If ``None``, defaults to ``n_fft``
#         window_fn (Tensor, optional): Optional window function. Should be a 1D of length ``n_fft``
#         max_norm_db (float, optional): Maximum amount of gain to apply to the input waveform
#             in the pre-normalization stage, in dB. Default is 35.
#     """

#     def __init__(
#         self,
#         n_fft: int,
#         hop_size: int,
#         n_stages: int,
#         act_precision: Precision = int16,
#         weight_precision: Precision = int16,
#         window_size: int = None,
#         window_fn: Tensor = None,
#         max_norm_db: float = 35,
#     ):
#         super().__init__()
#         self.n_fft = n_fft
#         self.hop_size = hop_size
#         if window_size is None:
#             window_size = n_fft
#         self.window_size = window_size
#         self.n_stages = n_stages

#         self.prenorm = L1NormAndInverse(clamp_dbfs=max_norm_db)

#         if window_fn is not None:
#             self.window_mul = WindowMul(window_fn, int16)
#         else:
#             self.window_mul = Identity()

#         if window_size < n_fft:
#             raise NotImplementedError("n_fft > window_size not yet supported in STFT")
#         elif window_size > n_fft:
#             raise ValueError("window_size cannot exceed n_fft")
#         else:
#             self.zero_catter = Identity()

#         self.buffer = STFTBuffer(window_size, hop_size)
#         self.rfft = RFFT(n_fft, n_stages, act_precision, weight_precision)

#         if act_precision == int24:
#             self.cast16 = Cast16()
#         else:
#             self.cast16 = Identity()
#         self.apply_norm = Multiply(act_precision)
#         self.apply_gain = Multiply(int16)

#     def forward(self, x) -> tuple[tuple[Tensor, Tensor, Tensor], tuple[Tensor, Tensor]]:
#         x, _ = self.buffer(x)

#         xwin = self.window_mul(x)
#         xwin_16 = self.cast16(xwin)
#         gain, igain = self.prenorm(xwin_16)
#         xwin_n = self.apply_norm(xwin, gain)

#         xwin_n = self.zero_catter(xwin_n)
#         re_normed, im_normed = self.rfft(xwin_n)

#         re = self.apply_gain(re_normed, igain)
#         im = self.apply_gain(im_normed, igain)

#         return (re_normed, im_normed, igain), (re, im)


# class NormedISTFT(nn.Module):
#     """Inverse to NormedSTFT.

#     Arguments:
#         n_fft (int): size of FFT, in samples
#         hop_size (int): hop size, in samples
#         n_stages (int): number of power-of-2 cooley-tukey decomposition stages. ``n_stages = 0`` yields a
#             dense matrix implementation of the IDFT. Must satisfy ``n_stages < floor(log2(n_fft))``
#         act_precision (Precision, optional): Activation precision, default int16. Supports int16 or
#             int24.
#         weight_precision (Precision, optional): FFT weights precision, default int16. Supports int16 or
#             int8.
#         window_size (int, optional): window size, in samples. If ``None``, defaults to ``n_fft``
#         window_fn (Tensor, optional): Optional window function. Should be a 1D of length ``n_fft``
#     """

#     def __init__(
#         self,
#         n_fft: int,
#         hop_size: int,
#         n_stages: int,
#         act_precision: Precision = int16,
#         weight_precision: Precision = int16,
#         window_size: int = None,
#         window_fn: Tensor = None,
#     ):
#         super().__init__()
#         self.n_fft = n_fft
#         self.hop_size = hop_size
#         if window_size is None:
#             window_size = n_fft

#         assert window_size == n_fft, "window_size != n_fft not yet supported in ISTFT"
#         assert (
#             window_size == 2 * hop_size
#         ), r"ISTFT with overlap other than 50% not yet supported in ISTFT"

#         self.irfft = IRFFT(n_fft, n_stages, act_precision, weight_precision)
#         if window_fn is None:
#             self.window_mul = MulHalf(act_precision)
#         else:
#             synth_window = get_synthesis_window(window_fn, hop_size)
#             self.window_mul = WindowMulParam(synth_window, act_precision)
#         self.ola = OverlapAdd50pct(hop_size, act_precision)

#         if act_precision == int24:
#             self.cast = Cast16()
#         else:
#             self.cast = Identity()

#         self.mul_denorm = Multiply(act_precision)

#     def forward(self, re: Tensor, im: Tensor, igain: Tensor) -> Tensor:
#         """Compute the ISTFT given tensors holding the real and imaginary spectral components.

#         Arguments:
#             re (Tensor): real-part of the STFT to invert, shape ``(batch, N, n_fft//2 + 1)``
#             im (Tensor): imaginary-part of the STFT to invert, shape ``(batch, N, n_fft//2 + 1)``

#         Returns:
#             Tensor, real-valued inversion of the input STFT, with overlap-add inversion.
#             shape: (batch, N, hop_size)
#         """
#         winsig_n = self.irfft(re, im)
#         # de-normalize
#         winsig = self.mul_denorm(winsig_n, igain)
#         sig = self.window_mul(winsig)
#         x = self.ola(sig)
#         x = self.cast(x)
#         return x


# if __name__ == "__main__":
#     import fmot

#     stft = NormedSTFT(128, 64, 3, int16, int16, window_fn=torch.hann_window(128))
#     x = torch.randn(8, 10, 64)

#     stft(x)

#     cmodel = fmot.ConvertedModel(stft, batch_dim=0, seq_dim=1)
#     cmodel(x)

#     cmodel.quantize([torch.randn(8, 10, 64) for _ in range(4)])

#     graph = cmodel.trace()
