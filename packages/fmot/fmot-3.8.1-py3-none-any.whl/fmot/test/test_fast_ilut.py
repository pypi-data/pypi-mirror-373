import torch
from torch import nn, Tensor
import fmot
import numpy as np


def eval_lut_size():
    fmot.CONFIG.fast_ilut = False
    model = nn.Sequential(nn.Sigmoid())
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.linspace(-8, 8, 100).reshape(1, -1) for _ in range(4)])
    graph = cmodel.trace()
    print("OLD:")
    print(graph.subgraphs["ARITH"])
    nodes_old_ilut = len(graph.subgraphs["ARITH"].nodes)

    fmot.CONFIG.fast_ilut = True
    model = nn.Sequential(nn.Sigmoid())
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.linspace(-8, 8, 100).reshape(1, -1) for _ in range(4)])
    graph = cmodel.trace()
    print("\nNEW:")
    print(graph.subgraphs["ARITH"])
    nodes_fast_ilut = len(graph.subgraphs["ARITH"].nodes)

    print(f"\n{nodes_old_ilut=} {nodes_fast_ilut=}")


@torch.no_grad()
def test_fast_ilut_sigmoid():
    model = nn.Sequential(nn.ReLU(), nn.Tanh(), nn.ReLU())

    fmot.CONFIG.fast_ilut = True
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.linspace(-10, 10, 1000).reshape(1, -1) for _ in range(4)])

    x = torch.linspace(-10, 10, 1000).reshape(1, -1)
    y0 = model(x)
    y1 = cmodel(x)

    mse = (y1 - y0).pow(2).mean()
    print(mse)

    graph = cmodel.trace()
    print(graph)

    x = torch.randn(1, 32)
    y0 = cmodel(x)[0].numpy()
    y1 = graph.run(x[0].numpy(), dequant=True)

    mse = np.sqrt(np.mean((y0 - y1) ** 2) / np.mean(y0**2))
    print(mse)


if __name__ == "__main__":
    # test_fast_ilut_sigmoid()
    eval_lut_size()
