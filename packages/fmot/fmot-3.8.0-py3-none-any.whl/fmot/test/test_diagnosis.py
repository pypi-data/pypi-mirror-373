import torch
from torch import nn
from unittest.mock import patch

from fmot.utils.quant_tools.diagnosis import get_quant_diagnosis
from fmot import ConvertedModel


class LinNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(128, 64)

    def forward(self, x):
        y = self.lin(x)

        return y


class RnnNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.LSTM(128, 64, batch_first=True)

    def forward(self, x):
        y, _ = self.layer(x)

        return y


class SeqNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.seq = nn.Sequential(nn.Linear(8, 8), nn.Linear(8, 8))
        self.module_list = nn.ModuleList([nn.Linear(8, 8), nn.Linear(8, 8)])

    def forward(self, x):
        y = self.seq(x)
        for module in self.module_list:
            y = module(y)

        return y


def test_qact_diagnosis():
    """Tests that the quant debug tool API runs, with the expected numbers of plots"""
    model = RnnNet()

    cmodel = ConvertedModel(model, batch_dim=0, seq_dim=1)
    quant_inputs = [torch.randn(5, 10, 128) for _ in range(3)]

    cmodel.quantize(quant_inputs)

    sample_input = quant_inputs[0]
    with patch("matplotlib.pyplot.show") as mock_plot:
        get_quant_diagnosis(model, cmodel, sample_input, plot=True)
        assert mock_plot.call_count == 1


def test_layer_diagnosis():
    """Tests that the quant debug tool works when we register one particular layer, with the expected numbers of
    plots
    """
    model = LinNet()

    cmodel = ConvertedModel(model)
    quant_inputs = [torch.randn(5, 128) for _ in range(3)]

    cmodel.quantize(quant_inputs)

    sample_input = quant_inputs[0]
    with patch("matplotlib.pyplot.show") as mock_plot:
        get_quant_diagnosis(
            model, cmodel, sample_input, to_register={"lin"}, kind="output", plot=True
        )
        assert mock_plot.call_count == 1


def test_seqmodel_diagnosis():
    """Tests that the quant debug tool works on ModuleList and Sequential layers, with the expected numbers of
    plots
    """
    model = SeqNet()

    cmodel = ConvertedModel(model)
    quant_inputs = [torch.randn(5, 8) for _ in range(3)]

    cmodel.quantize(quant_inputs)

    sample_input = quant_inputs[0]
    with patch("matplotlib.pyplot.show") as mock_plot:
        get_quant_diagnosis(model, cmodel, sample_input, kind="input", plot=True)
        assert mock_plot.call_count == 4
