import torch
import fmot
import numpy as np


class Mul(torch.nn.Module):
    def forward(self, x, y):
        return x * y


def test_broadcast_input():
    SIZE_X = 8
    SIZE_Y = 1
    BATCH = 16

    model = Mul()
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize(
        [(torch.randn(BATCH, SIZE_X), torch.randn(BATCH, SIZE_Y)) for _ in range(4)]
    )

    graph = cmodel.trace()
    print(graph)

    x = np.random.randn(SIZE_X)
    y = np.random.randn(SIZE_Y)
    z = graph.run(x, y, dequant=True)

    assert np.allclose(z, x * y, rtol=1e-2)


if __name__ == "__main__":
    test_broadcast_input()
