import torch
from torch import nn
from . import fft_v1, fft_v2
from fmot.precisions import Precision, int16, int8, get_precision
import warnings
from typing import Literal, Union

__all__ = ["FFT", "RFFT", "IFFT", "IRFFT", "auto_n_stages"]


def _count_factors_of_2(n: int) -> int:
    """Returns the number of times 2 divides n."""
    assert n > 0

    count = 0
    while n % 2 == 0 and n > 0:
        n //= 2
        count += 1
    return count


def auto_n_stages(n: int):
    """Automatically determine optimal number of stages for FFT decomposition."""

    assert isinstance(n, int), f"expected {n=} to be an integer, got {type(n)}"

    assert n % 1 == 0, f"n must be an integer, got {n}"

    n_pows_2 = _count_factors_of_2(n)

    rem_size = n // 2**n_pows_2

    while rem_size < 8 and n_pows_2 > 0:
        n_pows_2 -= 1
        rem_size *= 2

    if rem_size > 128:
        warnings.warn(
            f"n_fft={n} is divisible by {n_pows_2} powers of 2, leaving a remainder of size {rem_size}."
            " Consider padding the signal to a length that is divisible by more factors of 2 "
            "to reduce overheads."
        )

    return min(n_pows_2, 3)


def generic_fft_constructor(
    n_fft: int,
    n_stages: Union[int, Literal["auto"]],
    weight_precision: Union[Literal[8, 16], Precision],
    i8_cls: type[nn.Module],
    i16_cls: type[nn.Module],
):
    if isinstance(weight_precision, int):
        weight_precision = get_precision(weight_precision)
    if not isinstance(weight_precision, Precision):
        raise ValueError(
            f"weight_precision must be int or fmot.precision.Precision, got {type(weight_precision)}"
        )

    if n_stages == "auto":
        n_stages = auto_n_stages(n_fft)
    if not isinstance(n_stages, int):
        raise ValueError(f'n_stages={n_stages}, expected an int or "auto".')

    if weight_precision == int8:
        return i8_cls(n_fft, n_stages)
    elif weight_precision == int16:
        return i16_cls(n_fft, n_stages)
    else:
        raise ValueError(
            f"weight_precision {weight_precision} not supported at this time for FFT"
        )


class FFT(nn.Module):

    """Performs an FFT along final dimension (dim = -1)

    Arguments:
        n_fft (int): signal length
        n_stages (int | "auto", optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Default is "auto", in which case the function :attr:`auto_n_stages`
            is called to find the optimal number of decomposition stages.
        weight_precision (int | Precision, optional): precision to use for FFT weights. Valid options
            are :attr:`8` / :attr:`fmot.precisions.int8` to specify int8 weights, or :attr:`16` / :attr:`fmot.precisions.int16` to
            specify int16 weights. Default is :attr:`fmot.precisions.int16`,
            which yields the best quantized accuracy at the cost of 2x higher memory overhead and computatate cost.
    """

    def __new__(
        cls,
        n_fft: int,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
    ):
        return generic_fft_constructor(
            n_fft, n_stages, weight_precision, fft_v1.FFT, fft_v2.FFTv2
        )


class IFFT(nn.Module):
    """Performs an IFFT along final dimension (dim = -1)

    Arguments:
        n_fft (int): signal length
        n_stages (int | "auto", optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Default is "auto", in which case the function :attr:`auto_n_stages`
            is called to find the optimal number of decomposition stages.
        weight_precision (int | Precision, optional): precision to use for FFT weights. Valid options
            are :attr:`8` / :attr:`fmot.precisions.int8` to specify int8 weights, or :attr:`16` / :attr:`fmot.precisions.int16` to
            specify int16 weights. Default is :attr:`fmot.precisions.int16`,
            which yields the best quantized accuracy at the cost of 2x higher memory overhead and computatate cost.
    """

    def __new__(
        cls,
        n_fft: int,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
    ):
        return generic_fft_constructor(
            n_fft, n_stages, weight_precision, fft_v1.IFFT, fft_v2.IFFTv2
        )


class RFFT(nn.Module):
    """Performs an RFFT (real FFT) along final dimension (dim = -1)

    Arguments:
        n_fft (int): signal length
        n_stages (int | "auto", optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Default is "auto", in which case the function :attr:`auto_n_stages`
            is called to find the optimal number of decomposition stages.
        weight_precision (int | Precision, optional): precision to use for FFT weights. Valid options
            are :attr:`8` / :attr:`fmot.precisions.int8` to specify int8 weights, or :attr:`16` / :attr:`fmot.precisions.int16` to
            specify int16 weights. Default is :attr:`fmot.precisions.int16`,
            which yields the best quantized accuracy at the cost of 2x higher memory overhead and computatate cost.
    """

    def __new__(
        cls,
        n_fft: int,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
    ):
        return generic_fft_constructor(
            n_fft, n_stages, weight_precision, fft_v1.RFFT, fft_v2.RFFTv2
        )


class IRFFT(nn.Module):
    """Performs an IRFFT (inverse real FFT) along final dimension (dim = -1)

    Arguments:
        n_fft (int): signal length
        n_stages (int | "auto", optional): number of power-of-2 decomposition stages. ``n_stages = 0`` yields a
            dense matrix implementation of the DFT. Default is "auto", in which case the function :attr:`auto_n_stages`
            is called to find the optimal number of decomposition stages.
        weight_precision (int | Precision, optional): precision to use for FFT weights. Valid options
            are :attr:`8` / :attr:`fmot.precisions.int8` to specify int8 weights, or :attr:`16` / :attr:`fmot.precisions.int16` to
            specify int16 weights. Default is :attr:`fmot.precisions.int16`,
            which yields the best quantized accuracy at the cost of 2x higher memory overhead and computatate cost.
    """

    def __new__(
        cls,
        n_fft: int,
        n_stages: Union[int, Literal["auto"]] = "auto",
        weight_precision: Union[Literal[8, 16], Precision] = int16,
    ):
        return generic_fft_constructor(
            n_fft, n_stages, weight_precision, fft_v1.IRFFT, fft_v2.IRFFTv2
        )
