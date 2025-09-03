import torch
from torch import nn, Tensor
from fmot.nn.sequencer import Sequencer
from fmot.nn.atomics import Identity
from fmot.nn.signal_processing import TuningEpsilon
from fmot.nn.super_structures import SuperStructure
from .fft import RFFT, IRFFT
from fmot.precisions import int16, Precision
import math
from collections import namedtuple
from typing import *
import logging

ISTFT_AUTO_FACTOR = 0.0005
STFT_AUTO_FACTOR = 1 / 128

logger = logging.getLogger(__name__)


class _ReciprocalErrorCorrection(nn.Module):
    """Simple method to improve initial estimate of reciprocal.

    Main goal: make x * xinv closer to 1, useful to use this method
    with invertible normalizing factors
    """

    def forward(self, x, xinv):
        one_approx_v0 = x * xinv
        xinv1 = 2 * xinv - (one_approx_v0) * xinv
        return x, xinv1


class InvertibleNormalizingFactor(nn.Module):
    def __init__(self, clamp_min=0.02):
        super().__init__()
        self.clamp_min = clamp_min
        self.error_corrector = _ReciprocalErrorCorrection()

    def forward(self, x):
        norm = torch.mean(torch.abs(x), dim=-1, keepdim=True)
        norm = torch.clamp(norm, min=self.clamp_min, max=None)
        # norm = self.tuneps(norm)
        inorm = 1 / norm

        # want norm * inorm as close as we can get to 1 to avoid gain fluctuation
        # problems. Two iterations of reciprical error correction
        norm, inorm = self.error_corrector(norm, inorm)

        return norm, inorm


class Mul(nn.Module):
    def forward(self, x, y):
        return x * y


class Cat(nn.Module):
    """Utility; exists so that STFTBUffCell can be a SuperStructure"""

    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x: List[Tensor]) -> Tensor:
        return torch.cat(x, self.dim)


class _STFTBuffCell(SuperStructure):
    """Handles the data orchestration inside of STFT Buffer (with arb. kernel size)"""

    def __init__(self):
        super().__init__()
        self.cat = Cat(-1)

    @torch.jit.export
    def forward(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        y_t = self.cat(state + [x_t])
        state = state[1:] + [x_t]
        return y_t, state


class STFTBuffer(Sequencer):
    """Manages the internal buffer of an STFT and concatenates inputs with past inputs
    to fill the window-size.

    window_size must be an integer multiple of hop_size."""

    def __init__(self, window_size: int, hop_size: int):
        k = window_size / hop_size
        assert k % 1 == 0, "window_size must be an integer multiple of hop_size"
        k = int(k)

        super().__init__(state_shapes=[[hop_size]] * (k - 1), batch_dim=0, seq_dim=1)
        self.cell = _STFTBuffCell()

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        return self.cell(x_t, state)


class GeneralSTFTBuffer(Sequencer):
    """Manages the internal buffer of an STFT and concatenates inputs with past inputs
    to fill the window-size.

    Supports the general case when window_size is not an integer multiple of hop_size.
    """

    def __init__(self, window_size: int, hop_size: int):
        k = int(math.ceil(window_size / hop_size))

        super().__init__(state_shapes=[[hop_size]] * (k - 1), batch_dim=0, seq_dim=1)
        self.cell = _STFTBuffCell()

        # in the general case, we need to discard the beginning of the buffer
        n_buffer = k * hop_size
        self.n_discard = n_buffer - window_size
        self.n_keep = window_size

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        buff_full, state = self.cell(x_t, state)
        _, buff = torch.split(buff_full, [self.n_discard, self.n_keep], -1)
        return buff, state


class WindowMul(nn.Module):
    def __init__(self, window, requires_grad=False):
        super().__init__()
        self.window = nn.Parameter(window, requires_grad=requires_grad)

    def forward(self, x):
        return x * self.window


class ConstantMul(nn.Module):
    """Multiply by a scalar constant"""

    def __init__(self, cnst: float):
        super().__init__()
        self.cnst = cnst

    def forward(self, x):
        return self.cnst * x


class ZeroPadder(nn.Module):
    """For padded STFTs -- pads a given number of zeros to the
    end of a tenor, along dimension -1. Performs this via matrix-multiplication,
    though other more efficient kernels should be possible.

    Arguments:
        n_pre (int): size of the vector before padding at dim -1
        n_pad (int): number of zeros to pad at dim -1
    """

    def __init__(self, n_pre, n_pad):
        super().__init__()
        weight = torch.zeros(n_pre, n_pre + n_pad)
        weight[:n_pre, :n_pre] = torch.eye(n_pre)

        self.weight = nn.Parameter(weight, requires_grad=False)

    def forward(self, x):
        return torch.matmul(x, self.weight)


class ZeroSplitter(nn.Module):
    """Removes zeros from the end of dim -1 of a vector.
     Useful to de-pad vectors after IRFFT in ISTFT.

    Arguments:
        window_length (int): number of samples before padding
        n_padding (int): number of padding samples
    """

    def __init__(self, window_length: int, n_padding: int):
        super().__init__()
        self.window_length = window_length
        self.n_padding = n_padding

    def forward(self, x):
        x, _ = torch.split(x, [self.window_length, self.n_padding], dim=-1)
        return x


class STFT(SuperStructure):
    """Short-Time Fourier Transform

    Arguments:
        n_fft (int): size of FFT, in samples
        hop_size (int): hop size, in samples
        window_size (int, optional): window size, in samples. If ``None``, defaults to ``n_fft``. Default :attr:`None`
        window_fn (Tensor, optional): Optional window function. Should be a 1D of length ``n_fft``. Default :attr:`None`
        n_stages (int | "auto", optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Default is "auto", in which case the function :attr:`auto_n_stages`
            is called to find the optimal number of decomposition stages.
        weight_precision (int | Precision, optional): precision to use for FFT weights. Valid options
            are :attr:`8` / :attr:`fmot.precisions.int8` to specify int8 weights, or :attr:`16` / :attr:`fmot.precisions.int16` to
            specify int16 weights. Default is :attr:`fmot.precisions.int16`,
            which yields the best quantized accuracy at the cost of 2x higher memory overhead and computatate cost.
        norm_min (float | "auto" | None, optional): Internal normalizing factor, used to reduce quantization error when input signals
            have a wide dynamic range. Before taking the IFFT, the complex signal is normalized by dividing by
            :attr:`max(l1_norm(x), norm_min)`. After taking the IFFT, the waveform is multiplied by the inverse factor.
            Options:
                - :attr:`None`: no normalization is performed.
                - :attr:`"auto"`: norm_min is set to `0.01`, to automatically scale this value
                    based on the magnitude of the STFT components (which changes depending on the IFFT size)
                - :attr:`float`: if a float value is provided, this is used directly to set the norm_min value.
            Default: :attr:`"auto"`.
        window_requires_grad (bool, optional): If `True`, `window_fn` will have `requires_grad=True`, allowing it to
            be learned during training. Note, an initial non-None window_fn is required for `window_requires_grad=True`.


    .. note::

        Compared to the PyTorch builtin, the input must be reshaped into non-overlapping hops,
        and the output is returned as two separate tensors containing the real
        and imaginary parts. We do not automatically convert :attr:`torch.stft` into :attr:`fmot.nn.STFT`.

        **Comparison with torch.stft**

        .. code:: python

            import torch
            import fmot

            hop_length = 128
            window_length = 256
            window_fn = torch.hann_window(window_length)

            x = torch.randn(8, 16000)

            # using built-in torch.stft
            y_torch = torch.stft(x, n_fft=window_length, hop_length=hop_length,
                window_fn=window_fn, return_complex=True)
            re_torch = y_torch.real
            im_torch = y_torch.imag

            # using fmot.nn.STFT
            stft = fmot.nn.STFT(n_fft=window_length, hop_size=hop_length, n_stages="auto",
                window_fn=window_fn)
            # input needs to be reshaped into non-overlapping hops
            x_reshaped = x.reshape(8, 125, 128)
            re_fmot, im_fmot = stft(x_reshape)

    """

    report_supported = True

    def __init__(
        self,
        n_fft: int,
        hop_size: int,
        window_size: int = None,
        window_fn: Tensor = None,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
        norm_min: Optional[Union[float, Literal["auto"]]] = "auto",
        window_requires_grad: bool = False,
    ):
        super().__init__()
        self.n_fft = n_fft
        self.hop_size = hop_size
        if window_size is None:
            window_size = n_fft
        self.window_size = window_size
        self.n_stages = n_stages

        if window_fn is not None:
            self.window_mul = WindowMul(window_fn, requires_grad=window_requires_grad)
        else:
            if window_requires_grad:
                raise ValueError(
                    "In STFT, window_requires_grad=True requires a non-None initial window_fn"
                )
            self.window_mul = None

        if window_size < n_fft:
            self.catter = ZeroPadder(window_size, n_fft - window_size)
        elif window_size > n_fft:
            raise ValueError("window_size cannot exceed n_fft")
        else:
            self.catter = None

        if window_size % hop_size == 0:
            logger.debug("using STFTBuffer")
            self.buffer = STFTBuffer(window_size, hop_size)
        else:
            logger.debug("using GeneralSTFTBuffer")
            self.buffer = GeneralSTFTBuffer(window_size, hop_size)
        self.rfft = RFFT(n_fft, n_stages, weight_precision)

        if norm_min is not None:
            if norm_min == "auto":
                norm_min = STFT_AUTO_FACTOR

            if not isinstance(norm_min, (int, float)):
                raise ValueError(
                    f'Expected norm_min to be a float or "auto", got {norm_min}'
                )

            self.normalizer = InvertibleNormalizingFactor(norm_min)
            self.mul_inorm = Mul()
            self.mul_norm = Mul()
        else:
            self.normalizer = None

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        # concatenate with previous frames
        x_stack, __ = self.buffer(x)

        # optionally apply window_fn:
        if self.window_mul is not None:
            x_stack = self.window_mul(x_stack)

        # compute L1 norm and its inverse
        if self.normalizer is not None:
            norm, inorm = self.normalizer(x_stack)
            x_stack = self.mul_inorm(x_stack, inorm)

        # optionally pad with zeros:
        if self.catter is not None:
            x_stack = self.catter(x_stack)

        # apply the RFFT
        re_out, im_out = self.rfft(x_stack)

        # apply the norm
        if self.normalizer is not None:
            re_out = self.mul_norm(re_out, norm)
            im_out = self.mul_norm(im_out, norm)

        return re_out, im_out


# LEGACY...
class SynthesisWindow50PctOverlap(nn.Module):
    """Convert an analysis window into a synthesis window,
    assuming 50% overlap.
    """

    def __init__(self, analysis_window: torch.Tensor, requires_grad=False):
        super().__init__()
        wa, wb = analysis_window.chunk(2, 0)
        den = wa**2 + wb**2
        assert torch.all(den > 0), "Window function must satisfy the COLA constraint"
        den = torch.cat([den, den])
        self.window = nn.Parameter(analysis_window / den, requires_grad=requires_grad)

    def forward(self, x):
        return self.window * x


class _OverlapAdd50pct(Sequencer):
    def __init__(self, hop_size: int):
        super().__init__([[hop_size]], 0, 1)

    @torch.jit.export
    def step(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        x_curr, x_next = torch.chunk(x, 2, -1)
        (s_curr,) = state
        x = x_curr + s_curr
        return x, [x_next]


# LEGACY... need to keep for now
class OverlapAdd50Pct(nn.Module):
    """50% Overlap-Add Decoding. Takes overlapping waveforms and performs
    overlap-add, multiplying by a constant or time-varying factor if a window-function
    is used.
    """

    report_supported = True

    def __init__(
        self, hop_size: int, window: Tensor = None, window_requires_grad=False
    ):
        super().__init__()
        if window is not None:
            self.synthesis_window = SynthesisWindow50PctOverlap(
                window, requires_grad=window_requires_grad
            )

        else:
            self.synthesis_window = ConstantMul(0.5)
        self.ola = _OverlapAdd50pct(hop_size)

    def forward(self, x):
        x = self.synthesis_window(x)
        y, __ = self.ola(x)
        return y


COLAResult = namedtuple(
    "COLAResult",
    field_names=["is_cola", "is_nola", "multiplier", "overlap_added_weight"],
)


def check_cola(window: Tensor, hop_size: int, tol: float = 1e-6):
    """Check that the given window satisfies the COLA (Constant Overlap Add) condition.
    Also checks the NOLA (Nonzero Overlap Add) condition.

    Arguments:
        window (Tensor): window function
        hop_size (int): hop-size
        tol (float, optional): tolerance when checking COLA condition

    Returns:
        COLAResult:
            - is_cola (bool): `True` if the window satisfies the COLA condition, otherwise `False`
            - is_nola (bool): `True` if the window satisfies the NOLA condition, otherwise `False`
            - multiplier (float): the constant multiplier applied by the window function if `is_cola`,
                otherwise `None`.
            - overlap_added_weight (Tensor): per-sample weights applied by the window function. Should be
                a constant if `is_cola`, otherwise will reflect the per-sample weight variations for non-COLA
                window-functions.
    """
    assert window.ndim == 1
    L = window.shape[0]
    assert L % hop_size == 0
    n_segments = L // hop_size
    assert n_segments >= 2

    winseg = window.reshape(n_segments, hop_size)
    ola_sum = winseg.sum(0)

    is_nola = torch.all(ola_sum != 0)
    if is_nola:
        c = ola_sum[0]
        is_cola = torch.all((ola_sum - c).abs() / torch.max(ola_sum) < tol)
    else:
        c = None
        is_cola = False

    if not is_cola:
        c = None

    return COLAResult(is_cola, is_nola, c, ola_sum)


def check_wola(
    analysis_window: Tensor,
    synthesis_window: Tensor,
    hop_size: int,
    lookahead: int = 0,
    tol=1e-6,
):
    """Check that the given analysis-syntheis window pair satisfies the WOLA (Weighted Overlap Add) condition.
    Also checks the NOLA (Nonzero Overlap Add) condition.

    Arguments:
        analysis_window (Tensor): analysis window function used in the STFT
        synthesis_window (Tensor): synthesis window function used in the ISTFT
        hop_size (int): hop-size
        lookahead (int, optional): Number of **extra** analysis samples that must be buffered before
            the synthesis region begins.  Equivalently, the gap (in samples) between the **final sample** of the analysis window and the
            **first sample** of the synthesis window. A value of 0 means the synthesis window starts exactly where the
            analysis window ends (:attr:`ola_delay = synthesis_window_size - hop_size`). Otherwise, the delay is given by
            :attr:`ola_delay = synthesis_window_size - hop_size + lookahead`. Must be positive. Default :attr:`0`.
        tol (float, optional): tolerance when checking COLA condition

    Returns:
        COLAResult:
            - is_cola (bool): `True` if the window satisfies the COLA condition, otherwise `False`
            - is_nola (bool): `True` if the window satisfies the NOLA condition, otherwise `False`
            - multiplier (float): the constant multiplier applied by the window function if `is_cola`,
                otherwise `None`.
            - overlap_added_weight (Tensor): per-sample weights applied by the window function. Should be
                a constant if `is_cola`, otherwise will reflect the per-sample weight variations for non-COLA
                window-functions.
    """
    anal_size = len(analysis_window)
    synth_size = len(synthesis_window)

    # extract the synthesis region from analysis_window
    start = anal_size - synth_size - lookahead
    end = start + synth_size
    if start < 0:
        raise ValueError(
            f"len(analysis_window) must be greater than len(synthesis_window) + lookahead."
        )
    analysis_window = analysis_window[start:end]

    # check cola condition on analysis_window * synth_window
    winprod = analysis_window * synthesis_window

    return check_cola(winprod, hop_size, tol)


def design_wola(
    analysis_window: torch.Tensor,
    hop_size: int,
    synthesis_window_size: int,
    lookahead: int = 0,
    tol: float = 1e-6,
) -> torch.Tensor:
    r"""
    Design a synthesis window for a given analysis window such that the product
    satisfies the COLA condition while avoiding huge gains when the analysis window tapers.

    Instead of the elementwise reciprocal, this method computes, for each residue r (modulo hop_size),
    the minimum-energy synthesis window that satisfies:

    .. math::

        \sum_{i \in I(r)} a[i]*s[i] = 1,

    by setting:

    .. math::

        s_{i} = \frac{a_{i}}{\displaystyle\sum_{j \in I(r)} a_{j}^{2}}

    for each index i in the residue group I(r).

    Arguments:
        analysis_window (Tensor): analysis window function.
        hop_size (int): hop-size.
        synthesis_window_size (int): desired length for the synthesis window.
        lookahead (int, optional): Number of **extra** analysis samples that must be buffered before
            the synthesis region begins.  Equivalently, the gap (in samples) between the **final sample** of the analysis window and the
            **first sample** of the synthesis window. A value of 0 means the synthesis window starts exactly where the
            analysis window ends (:attr:`ola_delay = synthesis_window_size - hop_size`). Otherwise, the delay is given by
            :attr:`ola_delay = synthesis_window_size - hop_size + lookahead`. Must be positive. Default :attr:`0`.
        tol (float, optional): tolerance to avoid division by very small numbers.

    Returns:
        Tensor: Designed synthesis window.

    Raises:
        ValueError: if the synthesis region is too short or has near-zero energy in any residue group.
    """
    anal_size = len(analysis_window)
    synth_size = synthesis_window_size

    # Extract synthesis region from analysis_window.
    start = anal_size - synth_size - lookahead
    end = start + synth_size
    if start < 0:
        raise ValueError(
            "len(analysis_window) must be > len(synthesis_window) + lookahead."
        )
    analysis_segment = analysis_window[start:end].clone()

    # The synthesis window will be computed group-wise.
    synthesis_window = analysis_segment.clone()
    n_segments = synth_size // hop_size  # number of segments along the synthesis region

    synthesis_window = synthesis_window.reshape(n_segments, hop_size)
    synthesis_window = synthesis_window / torch.sum(
        synthesis_window**2, dim=0, keepdim=True
    )
    synthesis_window = synthesis_window.flatten()

    # Verify that the window product meets COLA.
    result = check_wola(analysis_window, synthesis_window, hop_size, lookahead, tol)
    if not result.is_cola:
        raise RuntimeError(
            f"The designed synthesis window does not satisfy the COLA condition.\n{result}"
        )

    return synthesis_window


class Add(nn.Module):
    def forward(self, x, y):
        return x + y


class ChunkN(nn.Module):
    def __init__(self, n_chunks: int):
        super().__init__()
        self.n_chunks = n_chunks

    def forward(self, x):
        return torch.chunk(x, self.n_chunks, dim=-1)


class GeneralOverlapAdd(Sequencer, SuperStructure):
    def __init__(self, synth_size: int, hop_size: int):
        assert synth_size % hop_size == 0
        n_hops = synth_size // hop_size
        assert n_hops >= 2

        super().__init__([[hop_size]] * (n_hops - 1))
        self.add = Add()
        self.chunk = ChunkN(n_hops)

    @torch.jit.export
    def step(self, x_t: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        x_chunks = self.chunk(x_t)

        new_state = []
        for x_in, s_in in zip(x_chunks[:-1], state):
            new_state.append(self.add(x_in, s_in))

        new_state.append(x_chunks[-1])

        return new_state[0], new_state[1:]


class SynthMul(nn.Module):
    def __init__(self, window: Tensor, requires_grad=False):
        super().__init__()
        self.window = nn.Parameter(window, requires_grad=requires_grad)

    def forward(self, x):
        return self.window * x


class Split(nn.Module):
    def __init__(self, sizes: list[int]):
        super().__init__()
        self.sizes = sizes

    def forward(self, x):
        return torch.split(x, self.sizes, dim=-1)


class SynthesisRegionExtractor(SuperStructure):
    """
    1. Remove zero padding: remove `n_fft - window_size` samples from the end of the vector
    2. Remove lookahead: remove `lookahead` samples from the end of the vector
    3. Asymmetric case: remove `window_size - synth_window_size - lookahead` samples from the beginning

    Overall: break the vector into three regions, where active is the active synthesis region
        [pre, active, post]
        - `len(pre) = window_size - synth_window_size - lookahead` (error if negative)
        - `len(active) = synth_window_size`
        - `len(post) = n_fft - window_size + lookahead`
    """

    def __init__(
        self, n_fft: int, window_size: int, synth_window_size: int, lookahead: int
    ):
        super().__init__()
        self.pre_len = window_size - synth_window_size - lookahead
        assert self.pre_len >= 0
        self.active_len = synth_window_size
        self.post_len = n_fft - window_size + lookahead

        if self.pre_len != 0:
            if self.post_len != 0:
                self.extractor = Split([self.pre_len, self.active_len, self.post_len])
                self.extract_idx = 1
            else:
                self.extractor = Split([self.pre_len, self.active_len])
                self.extract_idx = 1
        elif self.post_len != 0:
            self.extractor = Split([self.active_len, self.post_len])
            self.extract_idx = 0
        else:
            self.extractor = Identity()
            self.extract_idx = None

    def forward(self, x):
        extracted = self.extractor(x)
        if self.extract_idx is None:
            return extracted
        else:
            return extracted[self.extract_idx]


class ISTFT(SuperStructure):
    r"""Inverse Short-Time Fourier Transform (ISTFT)

    The ISTFT class reconstructs a time-domain signal from its Short-Time Fourier Transform (STFT)
    representation. It implements an inverse Real FFT (IRFFT) and uses a weighted overlap-add (WOLA)
    scheme to recombine the overlapping time-domain segments produced by the inverse transform.
    This implementation offers a variety of configuration options that allow for fine-tuning
    the reconstruction quality, computational performance, and delay. Asymmetric windowing schemes
    can be implemented by tuning the `synthesis_window_size` and other parameters.


    The reconstruction procedure involves the following steps:
      1. **Optional Normalization:**
         The complex STFT components are optionally normalized to mitigate quantization errors stemming
         from wide variations in the signal's dynamic range. A normalization factor is computed based on
         the L1 norm of the input and a specified minimum threshold, ensuring numerical stability.
      2. **Inverse FFT:**
         The normalized frequency-domain representation is transformed into the time domain using an
         efficient Inverse Real FFT implementation (IRFFT) that utilizes a power-of-2 decomposition for improved
         performance.
      3. **Synthesis Region Extraction:**
         Only the relevant portion of the inverse FFT output (the synthesis region) is retained, based on
         the specified window size, synthesis window size, and lookahead.
      4. **Synthesis Windowing:**
         A synthesis window function is applied to the extracted region. The synthesis function is either provided
         or automatically designed (via the WOLA condition) to ensure that, when overlapping and adding
         successive frames, the contributions sum to a constant (the COLA condition), thereby ensuring
         perfect reconstruction.
      5. **Overlap-Add (OLA):**
         Finally, the windowed segments are recombined using an overlap-add procedure to produce
         the final reconstructed time-domain signal.

    Attributes:
        ola_delay (int): Overall number of samples of delay performed by the ISTFT. Equal to :attr:`ola_delay = synthesis_window_size - hop_size + lookahead`

    Arguments:
        n_fft (int): Size of FFT, in samples.
        hop_size (int): Hop size between consecutive STFT frames, in samples.
        window_size (int, optional): Size of the analysis window, in samples. Defaults to :attr:`n_fft` if not provided.
        synthesis_window_size (int, optional): Size of the synthesis window, in samples.
            If not provided, it defaults to the value of :attr:`window_size`.
        window_fn (Tensor, optional): Analysis window function. Expected to be a 1D tensor of length window_size.
        synthesis_window_fn (Tensor, optional): Predefined synthesis window function. Must be a 1D tensor of length synthesis_window_size.
            When provided, it is checked for compliance with the WOLA condition. If it passes, it is adjusted by its COLA multiplier.
            If `synthesis_window_fn=None`, :attr:`design_wola` will be called to automatically design an appropriate synthesis window.
            Defualt: :attr:`None`.
        lookahead (int, optional): Number of **extra** analysis samples that must be buffered before
            the synthesis region begins.  Equivalently, the gap (in samples) between the **final sample** of the analysis window and the
            **first sample** of the synthesis window. A value of 0 means the synthesis window starts exactly where the
            analysis window ends (:attr:`ola_delay = synthesis_window_size - hop_size`). Otherwise, the delay is given by
            :attr:`ola_delay = synthesis_window_size - hop_size + lookahead`. Must be positive. Default :attr:`0`.
        n_stages (int or "auto", optional): Number of power-of-2 decomposition stages used by the IRFFT. A value of 0 results in
            a dense matrix implementation of the DFT. When set to "auto", the optimal number of stages is automatically determined.
        weight_precision (int or Precision, optional): Quantization precision for FFT weights. Valid options are:
            - 8 or fmot.precisions.int8: Lower memory footprint and faster computation.
            - 16 or fmot.precisions.int16: Higher quantized accuracy at the cost of increased memory and computational requirements.
            The default is fmot.precisions.int16.
        norm_min (float or "auto" or None, optional): Normalization parameter to reduce quantization error when the input signal has a
            wide dynamic range. This parameter is used to compute a normalizing factor in the pre-IFFT stage.
            Options:
                - None: No normalization is performed.
                - "auto": Automatically sets norm_min to 0.01 * n_fft.
                - float: A user-specified value.
            The default is "auto".
        window_requires_grad (bool, optional): If True, enables gradient computation with respect to the synthesis window.
            This is useful when the synthesis window is subject to learning or optimization. Default is False.

    Raises:
        ValueError: If synthesis_window_size is not an integer multiple of hop_size.
        ValueError: If synthesis_window_size is less than twice the hop_size.
        ValueError: If :attr:`lookahead + synthesis_window_size > window_size`.
        ValueError: If a provided synthesis_window_fn does not satisfy the WOLA condition.
        ValueError: If any region in the analysis window (used for synthesis window design) has near-zero energy,
                    making a stable inversion impossible.

    Methods:
        forward(re, im):
            Reconstruct the time-domain signal from the real (re) and imaginary (im) parts of the STFT.
            The process involves:
              1. Optionally normalizing the STFT components.
              2. Computing the inverse FFT (IRFFT) to obtain the windowed signal.
              3. Extracting the synthesis region from the windowed signal.
              4. Applying the synthesis window (either provided or automatically designed).
              5. Performing the overlap-add operation to reconstruct the final time-domain signal.

    Example:
        >>> istft = ISTFT(n_fft=1024, hop_size=256, window_size=1024)
        >>> reconstructed_signal = istft(re_stft, im_stft)

    Time-Alignment:

        When using fmot.nn.STFT and fmot.nn.ISTFT, it is important to know that the output of ISTFT is time delayed
        by :attr:`ISTFT.ola_delay` samples. When comparing the output signal to targets, it is important to time-align the reconstructed signal
        with the target signal.

        The total algorithmic delay is :attr:`ola_delay = synthesis_window_size - hop_size + lookahead`.
        :attr:`lookahead = 0` gives the minimum latency for a given analysis / synthesis pair; increasing it
        trades additional latency for the ability to place a narrow synthesis window deeper inside a long asymmetric
        analysis window (useful for low-latency, high-resolution designs).

        The example below demonstrates this for a simple identity system:

        .. code:: python

            import torch
            from torch import nn
            import fmot

            class fmotIdentityOLA(nn.Module):
                def __init__(self, window_size: int, hop_size: int):
                    super().__init__()
                    window_fn = torch.hann_window(window_size)
                    self.stft = fmot.nn.STFT(window_size, hop_size, window_fn=window_fn)
                    self.istft = fmot.nn.ISTFT(window_size, hop_size, window_fn=window_fn)

                def forward(self, x):
                    re, im = self.stft(x)
                    y = self.istft(re, im)
                    return y

            # test on a random waveform
            BATCH = 8
            HOP = 32
            WIN = 64

            ola = fmotIdentityOLA(WIN, HOP)

            ola_delay = ola.istft.ola_delay

            x = torch.randn(BATCH, HOP * 100)
            x_hopped = x.reshape(BATCH, 100, HOP)
            y_hopped = ola(x_hopped)

            y = y_hopped.reshape(BATCH, -1)

            # compare reconstructed signal to original x
            error = torch.norm(x[:,:-ola_delay] - y[:, ola_delay:])
            print(error)
            >> tensor(2.2300e-05)

        Asymmetric Windowing:

            `ISTFT` provides a high degree of flexibility to meet low-latency requirements through asymmetric windowing schemes.

            In the example below, we will design a low-latency STFT/ISTFT scheme with high frequency resolution.

            .. code:: python

                import torch
                from torch import nn
                import fmot

                class fmotAsymmetricOLA(nn.Module):
                    def __init__(self, window_size: int, synthesis_size: int, hop_size: int):
                        super().__init__()

                        # design an asymmetric hann window
                        size_falling = synthesis_size // 2
                        size_rising = window_size - size_falling

                        window_fn = torch.cat([
                            torch.hann_window(2*size_rising)[:size_rising],
                            torch.hann_window(2 * size_falling)[size_falling:]]
                        )

                        # use fmot tools to design a synthesis window that satisfies the WOLA condition
                        synth_window_fn = fmot.nn.design_wola(
                            window_fn,
                            hop_size,
                            synthesis_size
                        )

                        self.stft = fmot.nn.STFT(window_size, hop_size, window_fn=window_fn)
                        self.istft = fmot.nn.ISTFT(window_size, hop_size, synthesis_window_size=synthesis_size,
                                    window_fn=window_fn, synthesis_window_fn=synth_window_fn)

                    def forward(self, x):
                        re, im = self.stft(x)
                        y = self.istft(re, im)
                        return y

                # test on a random waveform
                BATCH = 8
                HOP = 32
                WIN = 256
                SYNTH_WIN = 64

                ola = fmotAsymmetricOLA(WIN, SYNTH_WIN, HOP)

                ola_delay = ola.istft.ola_delay

                x = torch.randn(BATCH, HOP * 100)
                x_hopped = x.reshape(BATCH, 100, HOP)
                y_hopped = ola(x_hopped)

                y = y_hopped.reshape(BATCH, -1)

                # compare reconstructed signal to original x
                error = torch.norm(x[:,:-ola_delay] - y[:, ola_delay:])
                print(error)
                >> tensor(1.7786e-05)

    See Also:
        - :attr:`STFT`: Module for performing Short Time Fourier Transform.
        - :attr:`IRFFT`: Module for performing the inverse Fast Fourier Transform.
        - :attr:`check_wola`: Function to verify that an analysis-synthesis window pair meets the WOLA condition.
        - :attr:`check_cola`: Function to verify that an analysis window meets the COLA condition without the need for a non-rectangular synthesis window.
        - :attr:`design_wola`: Function to automatically design a synthesis window that satisfies the WOLA condition.
    """
    report_supported = True

    def __init__(
        self,
        n_fft: int,
        hop_size: int,
        window_size: int = None,
        synthesis_window_size: int = None,
        window_fn: Tensor = None,
        synthesis_window_fn: Tensor = None,
        lookahead: int = 0,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
        norm_min: Optional[Union[float, Literal["auto"]]] = "auto",
        window_requires_grad: bool = False,
    ):
        super().__init__()
        # extract window / hop sizes
        self.n_fft = n_fft
        self.hop_size = hop_size
        if window_size is None:
            self.window_size = n_fft
        else:
            self.window_size = window_size
        if synthesis_window_size is None:
            self.synthesis_window_size = self.window_size
        else:
            self.synthesis_window_size = synthesis_window_size
        self.lookahead = lookahead
        self.ola_delay = self.synthesis_window_size - self.hop_size + self.lookahead

        # check legality
        if self.synthesis_window_size % self.hop_size != 0:
            raise ValueError(
                "Synthesis window must be an integer multiple of the hop_size"
            )
        n_overlap = self.synthesis_window_size // self.hop_size
        if n_overlap < 2:
            raise ValueError(
                "Synthesis window size must be at least 2x the hop_size, got "
                f"{self.synthesis_window_size=} and {self.hop_size=}"
            )
        if self.lookahead + self.synthesis_window_size > self.window_size:
            raise ValueError(f"lookahead + synthesis_window_size must be < window_size")

        # test/design the synthesis window
        synth_window = self._init_synth_window(
            window_fn=window_fn, synthesis_window_fn=synthesis_window_fn
        )
        self.synthesis_window = SynthMul(
            synth_window, requires_grad=window_requires_grad
        )

        # init irfft
        self.irfft = IRFFT(n_fft, n_stages, weight_precision)

        # pulling out the relevant part of the signal before windowing / OLA
        self.synthesis_region_extractor = SynthesisRegionExtractor(
            self.n_fft,
            self.window_size,
            self.synthesis_window_size,
            self.lookahead,
        )

        self.ola = GeneralOverlapAdd(self.synthesis_window_size, self.hop_size)

        # optional normalization
        if norm_min is not None:
            if norm_min == "auto":
                norm_min = ISTFT_AUTO_FACTOR * n_fft

            if not isinstance(norm_min, (float, int)):
                raise ValueError(
                    f'Expected norm_min to be a float or "auto", got {norm_min}'
                )

            self.normalizer = InvertibleNormalizingFactor(clamp_min=norm_min)
            self.cat = Cat(dim=-1)
            self.mul_norm = Mul()
            self.mul_inorm = Mul()
        else:
            self.normalizer = None

    def _init_synth_window(
        self, window_fn: Optional[Tensor], synthesis_window_fn: Optional[Tensor]
    ) -> Tensor:
        if window_fn is None:
            # assume that the user is using a rectangular synthesis window
            window_fn = torch.ones(self.window_size)

        if synthesis_window_fn is not None:
            assert synthesis_window_fn.ndim == 1
            assert len(synthesis_window_fn) == self.synthesis_window_size

            wola_result = check_wola(
                window_fn, synthesis_window_fn, self.hop_size, self.lookahead
            )
            if wola_result.is_cola:
                return synthesis_window_fn / wola_result.multiplier
            else:
                raise ValueError(
                    f"The given synthesis window does not satisfy the WOLA condition.\n{wola_result}"
                )

        else:
            # design wola window for the given window_fn

            # check if the window is already cola
            synth_rect = torch.ones(self.synthesis_window_size)
            cola_check = check_wola(
                window_fn, synth_rect, self.hop_size, self.lookahead
            )

            if cola_check.is_cola:
                return synth_rect / cola_check.multiplier

            else:
                # need to design a wola window
                synthesis_window_fn = design_wola(
                    window_fn,
                    self.hop_size,
                    self.synthesis_window_size,
                    self.lookahead,
                )
                return synthesis_window_fn

    def forward(self, re, im):
        # optional pre-normalization
        if self.normalizer is not None:
            norm, inorm = self.normalizer(self.cat([re, im]))
            re = self.mul_inorm(re, inorm)
            im = self.mul_inorm(im, inorm)

        # irfft
        winsig = self.irfft(re, im)
        # extract synthesis region
        winsig = self.synthesis_region_extractor(winsig)
        if self.normalizer is not None:
            winsig = self.mul_norm(winsig, norm)
        # multiply by the synthesis window function
        sig = self.synthesis_window(winsig)
        # perform overlap-add
        y, _ = self.ola(sig)

        return y
