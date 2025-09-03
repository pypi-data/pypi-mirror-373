import torch
from torch import nn
import fmot
from fmot.beta import QuantizationErrorAnalyzer

if __name__ == "__main__":
    model = nn.Sequential(
        fmot.nn.TemporalConv1d(32, 64, kernel_size=1),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 64, kernel_size=3, groups=64),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 32, kernel_size=1),
        fmot.nn.TemporalConv1d(32, 64, kernel_size=1),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 64, kernel_size=3, groups=64),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 32, kernel_size=1),
        fmot.nn.TemporalConv1d(32, 64, kernel_size=1),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 64, kernel_size=3, groups=64),
        nn.ReLU(),
        fmot.nn.TemporalConv1d(64, 32, kernel_size=1),
        nn.Sigmoid(),
    )

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=2)
    cmodel.quantize([torch.randn(8, 32, 32) for _ in range(4)])

    analyzer = QuantizationErrorAnalyzer(cmodel, (torch.randn(8, 32, 32),))
    analyzer.plot_qsnr(show=True)
    analyzer.plot_dynamic_range_utilization(show=True, fname="dyn_util.png")
