import torch
from torch import nn
from torch import Tensor
from typing import *


class TemporalUnfold1d(nn.Module):
    """
    Extract sliding window from an input tensor.

    Applies temporal padding as appropriate for TemporalConv1d and
    SlidingWindowCausalAttention

    `input` is a tensor of shape `(N, C, T)`, where `N` is the
    batch size, `C` is the channel dimension, and `T` is the sequence length.

    It outputs a tensor of shape `(N, C*kernel_size, T)`. Each output flattens
    each `kernel_size`-sized sliding block over the input sequence.
    """

    report_supported = True

    def __init__(self, kernel_size: int, dilation: int = 1):
        super().__init__()
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.buffsize = (self.kernel_size - 1) * self.dilation
        self._unfold = torch.nn.Unfold((1, kernel_size), (1, dilation))

    def forward(self, x: Tensor) -> Tensor:
        B, C, T = x.shape

        gathers = [
            self.kernel_size * torch.arange(0, C, device=x.device) + k
            for k in range(self.kernel_size)
        ]
        gathers = torch.cat(gathers, 0)
        gathers = gathers.reshape(1, -1, 1)
        gathers = gathers.expand(B, self.kernel_size * C, T)

        buffer = torch.zeros((B, C, self.buffsize), device=x.device)

        x = torch.cat([buffer, x], dim=-1)
        x = torch.unsqueeze(x, -2)
        x = self._unfold(x)
        x = x.gather(1, gathers)

        return x
