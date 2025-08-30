import torch
import fmot
import numpy as np
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)


class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.unfold = fmot.nn.TemporalUnfold1d(3)

    def forward(self, x):
        y = self.unfold(x) + 1
        return y


def test_unfold():
    model = Model()
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
    cmodel.quantize([torch.randn(8, 16, 4) for _ in range(4)])

    graph = cmodel.trace()
    print(graph)
    node = graph.subgraphs["ARITH"].nodes[0]
    print(node)
    print(node.inputs)
    print(node.constants)

    x = torch.linspace(0, 1, 16 * 4)
    x = x.reshape(1, 4, 16).transpose(1, 2)
    y0 = model(x).detach().numpy()
    print(f"{y0.shape=}")
    y1 = cmodel(x).detach().numpy()
    print(f"{y1.shape=}")
    y2 = graph.run(x[0].numpy(), dequant=True)
    print(f"{y2.shape=}")


if __name__ == "__main__":
    test_unfold()
