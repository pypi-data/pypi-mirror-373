import torch
from torch import nn
import fmot
import numpy as np
from fmot.fqir import GraphProto


class MyModel(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, batch_first=True)

    def forward(self, x):
        y, _ = self.gru(x)
        return y


def test_step_gru():
    model = MyModel(32, 32)
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    cmodel.quantize([torch.randn(8, 10, 32) for _ in range(10)])
    graph = cmodel.trace()

    arith = graph.subgraphs["ARITH"]
    init = graph.subgraphs["INIT"]
    quant = graph.subgraphs["QUANT"]

    x = np.random.randn(10, 32)
    y0 = graph.run(x)

    # call graph in step-wise fashion
    x = quant.run(x)
    _, state = init.run(return_objs=True)

    y1 = []
    for x_t in x:
        y_t, state = arith.run(x_t, state=state, return_objs=True)
        y1.append(y_t)

    y1 = np.stack(y1, 0)

    assert np.array_equal(y0, y1)


def fqir_stepwise_example(graph: GraphProto, x: np.ndarray):
    """Toy example: step arith to compute y_t, and then feed in x_t + y_t-1 as next time-step's input.

    Arguments:
        graph (FQIR GraphProto)
        x (np array): shape (time, input_size)
    """
    # unpack the arith and init subgraphs
    arith = graph.subgraphs["ARITH"]
    init = graph.subgraphs["INIT"]

    # do this one time to initialize internal variables
    _, state = init.run(return_objs=True)

    outputs = []
    y_prev = 0
    for x_t in x:
        # a toy example of feedback...
        x_t = x_t + y_prev

        y_t, state = arith.run(x_t, state=state, return_objs=True)

        outputs.append(y_t)
        y_prev = y_t

    return np.stack(outputs)


if __name__ == "__main__":
    test_step_gru()
