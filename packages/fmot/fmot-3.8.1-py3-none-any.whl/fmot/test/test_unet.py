"""Adapted from unet_example.py, sent to Deepak @ Starkey

An example demonstrating new fmot support for strided TemporalConv1d and 
TemporalConvTranspose1d for UNet architectures.
"""

import torch
from torch import nn, Tensor
import fmot
from fmot.nn import TemporalConv1d, TemporalConvTranspose1d
import numpy as np
from typing import *
import pytest


class UNetEncoder(nn.Module):
    def __init__(
        self,
        in_channels: int,
        expansion_factor: int,
        kernel_size: int,
        stride: int,
        num_layers: int,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.expansion_factor = expansion_factor
        self.kernel_size = kernel_size
        self.stride = stride
        self.num_layers = num_layers
        self.layers = nn.ModuleList()
        for _ in range(num_layers):
            self.layers.append(
                TemporalConv1d(
                    in_channels=in_channels,
                    out_channels=in_channels * expansion_factor,
                    kernel_size=kernel_size,
                    stride=stride,
                )
            )
            in_channels *= expansion_factor

    def forward(self, x) -> Tuple[Tensor, List[Tensor]]:
        intermediate_acts = []
        for layer in self.layers:
            x = layer(x)
            x = x.relu()
            intermediate_acts.append(x)
        return x, intermediate_acts


class UNetDecoder(nn.Module):
    def __init__(
        self,
        out_channels: int,
        expansion_factor: int,
        kernel_size: int,
        stride: int,
        num_layers: int,
    ):
        super().__init__()
        self.out_channels = out_channels
        self.expansion_factor = expansion_factor
        self.kernel_size = kernel_size
        self.stride = stride
        self.num_layers = num_layers
        self.layers = nn.ModuleList()

        in_channels = out_channels * (expansion_factor) ** (num_layers)
        for _ in range(num_layers):
            self.layers.append(
                TemporalConvTranspose1d(
                    in_channels=in_channels,
                    out_channels=in_channels // expansion_factor,
                    kernel_size=kernel_size,
                    stride=stride,
                )
            )
            in_channels //= expansion_factor

    def forward(self, x, intermediate_acts: List[Tensor]) -> Tensor:
        for i, layer in enumerate(self.layers):
            x_cache = intermediate_acts[-(i + 1)]
            x = x + x_cache
            x = layer(x)
        return x


class UNet(nn.Module):
    def __init__(
        self, channels, expansion_factor, kernel_size, stride, rnn_hidden, num_layers
    ):
        super().__init__()
        self.channels = channels
        self.expansion_factor = expansion_factor
        self.kernel_size = kernel_size
        self.stride = stride
        self.num_layers = num_layers
        self.rnn_hidden = rnn_hidden

        self.encoder = UNetEncoder(
            channels, expansion_factor, kernel_size, stride, num_layers
        )

        inter_dim = channels * expansion_factor ** (num_layers)

        self.proj_rnn_in = nn.Linear(inter_dim, rnn_hidden)
        self.rnn = nn.LSTM(rnn_hidden, rnn_hidden, batch_first=True)
        self.proj_rnn_out = nn.Linear(rnn_hidden, inter_dim)

        self.decoder = UNetDecoder(
            channels, expansion_factor, kernel_size, stride, num_layers
        )

    def forward(self, x):
        x, intermediate_acts = self.encoder(x)

        x = x.transpose(1, 2)
        x = self.proj_rnn_in(x)
        x, _ = self.rnn(x)
        x = self.proj_rnn_out(x)
        x = x.transpose(1, 2)

        y = self.decoder(x, intermediate_acts)
        return y


@pytest.mark.xfail
@torch.no_grad()
def test_unet():
    channels = 16
    stride = 2
    rnn_hidden = 128
    num_layers = 4

    e2e_stride = stride**num_layers

    min_seq = e2e_stride

    # original pytorch model definition
    model = UNet(
        channels=channels,
        expansion_factor=stride,
        stride=stride,
        kernel_size=2 * stride,
        num_layers=num_layers,
        rnn_hidden=rnn_hidden,
    )

    x = torch.randn(8, channels, 4 * min_seq)
    y_orig = model(x)
    print(
        f"Called original model on input of shape {x.shape}, got output of shape {y_orig.shape}"
    )

    # Convert and quantize the model
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
    cmodel.quantize([torch.randn(8, channels, 4 * min_seq) for _ in range(4)])
    print("Converted and quantized the model")

    # Run on same input, measure mse
    y_quant = cmodel(x)
    err = (y_orig - y_quant).pow(2).mean()
    print(f"Quantized model has mse of {err:.3f} on the original input")

    # Trace to FQIR --> This will trigger a graph transformation for strided conv/tconv layers
    fqir_graph = cmodel.trace()

    # We will use the IOSpec from the converted model to get details about how the graph was transformed
    iospec = cmodel.get_iospec()
    print("Model's IOSPEC:\n", iospec)
    # In this case, we see that our original input and output sequences were of shape [channels, T]
    # After transformation, they are now both of shape [channels * S, T//S], where S is the end-to-end stride

    # Use the iospec object to call the FQIR graph, to confirm that the behavior matches the quantized pytorch
    # Need to remove batchdim to run FQIR (FQIR does not support batching, nor does SPU)
    x = torch.randn(1, channels, 4 * min_seq)
    y_cmodel = cmodel(x)[0].numpy()
    y_fqir = iospec.run_graph(fqir_graph, [x[0].numpy()], dequant=True)

    mse = np.mean((y_cmodel - y_fqir) ** 2)
    print(f"FQIR vs. quantized torch mse: {mse}")

    assert mse < 1e-3


if __name__ == "__main__":
    test_unet()
