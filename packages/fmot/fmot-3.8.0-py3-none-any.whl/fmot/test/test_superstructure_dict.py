import torch
import torch.nn as nn
from torch import Tensor
import fmot
from typing import *


class Mul(nn.Module):
    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        return x * y


class NestedDictSuperStructure(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.mul = Mul()
        self.lstm = nn.LSTM(
            input_size=40, hidden_size=50, num_layers=2, batch_first=True
        )

    def forward(
        self,
        a: Dict[str, Dict[str, Dict[str, Tensor]]],
        b: Dict[str, Dict[str, Dict[str, Tensor]]],
    ) -> Dict[str, Dict[str, Dict[str, Tensor]]]:
        results = {}
        for key1 in a.keys():
            inner_results_level1 = {}
            for key2 in a[key1].keys():
                inner_results_level2 = {}
                for key3 in a[key1][key2].keys():
                    mul_result = self.mul(a[key1][key2][key3], b[key1][key2][key3])
                    lstm_out, _ = self.lstm(mul_result)
                    inner_results_level2[key3] = lstm_out
                inner_results_level1[key2] = inner_results_level2
            results[key1] = inner_results_level1
        return results


def test_nested_dict_super_structure():
    model = NestedDictSuperStructure()
    B, S, D = 1, 20, 40

    a = {
        "key1": {
            "subkey1": {
                "subsubkey1": torch.randn(B, S, D),
                "subsubkey2": torch.randn(B, S, D),
            },
            "subkey2": {
                "subsubkey1": torch.randn(B, S, D),
                "subsubkey2": torch.randn(B, S, D),
            },
        }
    }
    b = {
        "key1": {
            "subkey1": {
                "subsubkey1": torch.randn(B, S, D),
                "subsubkey2": torch.randn(B, S, D),
            },
            "subkey2": {
                "subsubkey1": torch.randn(B, S, D),
                "subsubkey2": torch.randn(B, S, D),
            },
        }
    }

    # Quantization
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    calib_data = [(a, b), (a, b)]
    cmodel.quantize(calib_data)

    # Verify quantized output
    out_q = cmodel(*calib_data[0])
    out_fp = model(*calib_data[0])

    # Check that the shapes match
    for key1 in out_q.keys():
        for key2 in out_q[key1].keys():
            for key3 in out_q[key1][key2].keys():
                assert (
                    out_q[key1][key2][key3].shape == out_fp[key1][key2][key3].shape
                ), f"Shape mismatch: {out_q[key1][key2][key3].shape} != {out_fp[key1][key2][key3].shape}"


if __name__ == "__main__":
    test_nested_dict_super_structure()
