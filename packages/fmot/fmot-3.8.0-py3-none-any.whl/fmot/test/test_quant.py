import torch
from torch import nn

from fmot import ConvertedModel


class TestQuant:
    def test_quant_minimal_set(self):
        r"""Check that we can quantize a model on the minimum amount of data (2 samples)"""
        model = nn.Linear(10, 10)
        qmodel = ConvertedModel(model, batch_dim=0)
        quant_calib_data = [torch.randn(2, 10)]
        qmodel.quantize(quant_calib_data)
        assert True


if __name__ == "__main__":
    test_runner = TestQuant()
    test_runner.test_quant_minimal_set()
