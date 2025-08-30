import torch
from torch import nn, Tensor
import fmot
import numpy as np
from fmot.fqir.writer import FQIRWriter, new_fqir_graph

H = 32


class SimpleLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(H, H, batch_first=True)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = torch.clamp(x, -1, 1)
        return x


def test_2layer_lstm_stitching():
    modelA = SimpleLSTM()
    modelB = SimpleLSTM()

    cmodelA = fmot.ConvertedModel(modelA, batch_dim=0, seq_dim=1)
    cmodelB = fmot.ConvertedModel(modelB, batch_dim=0, seq_dim=1)

    # ensure matching quantas
    cmodelA.set_output_details(0, -15)
    cmodelB.set_input_details(0, -15)

    cmodelA.quantize([torch.randn(8, 10, H) for _ in range(4)])
    cmodelB.quantize([modelA(torch.randn(8, 10, H)) for _ in range(4)])

    graphA = cmodelA.trace()
    graphB = cmodelB.trace()

    # empty list of inputs
    g_merged = new_fqir_graph()

    writer = FQIRWriter.from_fqir(g_merged, "int16")
    inputs = writer.add_inputs_from_graph(graphA)
    outs_A = writer.inline_fqir_graph(graphA, inputs)
    outs_B = writer.inline_fqir_graph(graphB, outs_A)
    writer.add_outputs(outs_B)

    print(g_merged)

    x = np.random.randn(10, H)
    x_q = graphA.subgraphs["QUANT"].run(x, dequant=False)

    # compare graphA -> graphB with g_merged
    x_btwn = graphA.run(x_q, dequant=False)
    y_AB = graphB.run(x_btwn, dequant=False)
    y_merged = g_merged.run(x_q, dequant=False)

    assert np.array_equal(y_AB, y_merged)

    print("SUCCESS!")


if __name__ == "__main__":
    test_2layer_lstm_stitching()
