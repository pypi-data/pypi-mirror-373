import torch
import fmot
from fmot.nn import (
    BlockGRU,
    BlockLSTM,
    BandGRU,
    BidirectionalBandGRU,
    BandLSTM,
    BidirectionalBandLSTM,
)
import matplotlib.pyplot as plt
import numpy as np
import pytest

TEST_T = 50


@pytest.mark.parametrize(
    ["block_input_size", "block_hidden_size", "num_blocks"],
    [[32, 64, 12]],
)
@pytest.mark.parametrize(
    ["model_cls", "dilation"],
    [
        [BlockGRU, 1],
        [BlockGRU, 4],
        [BlockLSTM, 2],
        [BlockLSTM, 3],
        [BandGRU, None],
        [BandLSTM, None],
        [BidirectionalBandGRU, None],
        [BidirectionalBandLSTM, None],
    ],
)
@torch.no_grad()
def test_blockrnn(
    model_cls, block_input_size, block_hidden_size, num_blocks, dilation, plot=False
):
    dil = {}
    if dilation is not None:
        dil = {"dilation": dilation}
    model = model_cls(block_input_size, num_blocks, block_hidden_size, bias=True, **dil)

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)

    # make sure that the converted model matches original model's behavior (pre-quantization)
    x = torch.randn(8, TEST_T, block_input_size * num_blocks)
    y0 = model(x)
    y1 = cmodel(x)
    nrmse = (y0 - y1).pow(2).mean().sqrt() / y0.pow(2).mean().sqrt()
    print(f"Converted model nrmse: {nrmse}")
    assert nrmse < 1e-6, f"{nrmse=} > 1e-6"

    cmodel.quantize(
        [torch.randn(8, 40, block_input_size * num_blocks) for _ in range(3)]
    )
    y2 = cmodel(x)

    nrmse = (y2 - y0).pow(2).mean().sqrt() / y0.pow(2).mean().sqrt()
    print(f"Quantized model nrmse: {nrmse}")
    assert nrmse < 1e-2

    if plot:
        plt.plot(y0.flatten(), y2.flatten(), ".")
        plt.show()

    graph = cmodel.trace()
    print(graph)

    x = x[0].numpy()
    yfqir = graph.run(x, dequant=True)

    nrmse = (torch.as_tensor(yfqir) - y2[0]).pow(2).mean().sqrt() / y2[0].pow(
        2
    ).mean().sqrt()
    print(f"FQIR vs. Cmodel nrmse: {nrmse}")

    if plot:
        plt.plot(y2[0].flatten(), yfqir.flatten(), ".")
        plt.show()


if __name__ == "__main__":
    import logging

    # logging.basicConfig(level=logging.DEBUG)

    # test_blockrnn(BlockGRU, 32, 64, 12, plot=False)
    # test_blockrnn(BlockLSTM, 32, 64, 12, plot=False)
    # test_blockrnn(BandLSTM, 32, 64, 12, plot=True)
    # test_blockrnn(BidirectionalBandLSTM, 32, 64, 12, plot=True)
    test_blockrnn(BlockGRU, 32, 32, 6, 2, True)
