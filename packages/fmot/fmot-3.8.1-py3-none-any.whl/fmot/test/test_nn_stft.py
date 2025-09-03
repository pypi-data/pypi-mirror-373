import torch
from torch import nn
import fmot
from typing import *
from fmot.nn.fft.stft import STFTBuffer, STFT
import pytest


@pytest.mark.xfail
def test_bad_size_buff():
    buff = STFTBuffer(130, 128)


def test_good_size_buff():
    buff = STFTBuffer(256, 128)


@torch.no_grad()
def test_buffer_runs():
    buff = STFTBuffer(256, 128)
    x = torch.randn(1, 5, 128)
    y, __ = buff(x)
    assert y.shape[0] == 1
    assert y.shape[1] == 5
    assert y.shape[2] == 256

    cmodel = fmot.ConvertedModel(buff, seq_dim=1)
    y, __ = cmodel(x)
    cmodel.quantize([torch.randn(1, 5, 128) for _ in range(4)])
    graph = cmodel.trace()
    print(graph)

    assert True


@torch.no_grad()
def test_stft():
    stft = STFT(256, 128, window_fn=torch.hann_window(256))
    x = torch.randn(1, 5, 128)
    y, __ = stft(x)
    assert y.shape[0] == 1
    assert y.shape[1] == 5
    assert y.shape[2] == 129

    cmodel = fmot.ConvertedModel(stft, seq_dim=1)
    print(cmodel)
    y, __ = cmodel(x)
    cmodel.quantize([torch.randn(1, 5, 128) for _ in range(4)])
    graph = cmodel.trace()
    print(graph)

    assert True


if __name__ == "__main__":
    test_stft()
