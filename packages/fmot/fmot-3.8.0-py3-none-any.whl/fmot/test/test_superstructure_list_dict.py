import torch
import torch.nn as nn
from torch import Tensor
import fmot
from typing import List, Dict


class Mul(nn.Module):
    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        return x * y


class CombinedListDictSuperStructure(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.mul = Mul()
        self.lstm = nn.LSTM(
            input_size=40, hidden_size=50, num_layers=2, batch_first=True
        )

    def forward(
        self,
        a: List[Dict[str, List[Dict[str, Tensor]]]],
        b: List[Dict[str, List[Dict[str, Tensor]]]],
    ) -> List[Dict[str, List[Dict[str, Tensor]]]]:
        results = []
        for dict_elem_a, dict_elem_b in zip(a, b):
            inner_results_level1 = {}
            for key1 in dict_elem_a.keys():
                inner_results_level2 = []
                for sub_dict_a, sub_dict_b in zip(dict_elem_a[key1], dict_elem_b[key1]):
                    inner_results_level3 = {}
                    for key2 in sub_dict_a.keys():
                        mul_result = self.mul(sub_dict_a[key2], sub_dict_b[key2])
                        lstm_out, _ = self.lstm(mul_result)
                        inner_results_level3[key2] = lstm_out
                    inner_results_level2.append(inner_results_level3)
                inner_results_level1[key1] = inner_results_level2
            results.append(inner_results_level1)
        return results


def test_combined_super_structure():
    model = CombinedListDictSuperStructure()
    B, S, D = 1, 20, 40

    a = [{"key1": [{"subkey1": torch.randn(B, S, D), "subkey2": torch.randn(B, S, D)}]}]
    b = [{"key1": [{"subkey1": torch.randn(B, S, D), "subkey2": torch.randn(B, S, D)}]}]

    # Quantization
    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    calib_data = [(a, b), (a, b)]
    cmodel.quantize(calib_data)

    # Verify quantized output
    out_q = cmodel(*calib_data[0])
    out_fp = model(*calib_data[0])

    # Check that the shapes match
    for dict_q, dict_fp in zip(out_q, out_fp):
        for key1 in dict_q.keys():
            for list_q, list_fp in zip(dict_q[key1], dict_fp[key1]):
                for key2 in list_q.keys():
                    assert (
                        list_q[key2].shape == list_fp[key2].shape
                    ), f"Shape mismatch: {list_q[key2].shape} != {list_fp[key2].shape}"


if __name__ == "__main__":
    test_combined_super_structure()
