import torch
from torch import nn
import fmot
import numpy as np


class ReuseModel(nn.Module):
    def __init__(self, H=32):
        super().__init__()
        self.param = nn.Parameter(torch.randn(H, H))
        self.bias = nn.Parameter(torch.randn(H))

    def forward(self, x):
        x = torch.matmul(x, self.param.T) + self.bias
        x = x.relu()
        x = torch.matmul(x, self.param.T) + self.bias
        return x


class ReuseModel2(nn.Module):
    def __init__(self, H=32):
        super().__init__()
        self.lin = nn.Linear(H, H)

    def forward(self, x):
        x = self.lin(x)
        x = x.relu()
        x = self.lin(x)
        return x


@torch.no_grad()
def test_param_reuse():
    model = ReuseModel2(32)
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.randn(8, 32) for __ in range(4)])
    graph = cmodel.trace()
    print(graph)

    x = torch.randn(8, 32)
    y0 = model(x).numpy()
    y1 = cmodel(x).numpy()

    # print(np.mean(y0**2 - y1**2)/np.mean(y0**2))

    # np.testing.assert_allclose(y0, y1, rtol=2**(-14))

    y2 = graph.run(x[0].numpy())
    # np.testing.assert_allclose(y2, y1[0], rtol=2**(-14))

    # print('Success')


if __name__ == "__main__":
    test_param_reuse()
