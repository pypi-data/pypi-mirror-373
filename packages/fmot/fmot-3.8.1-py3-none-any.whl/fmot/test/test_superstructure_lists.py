import torch
import torch.nn as nn
from torch import Tensor
import fmot
from typing import List


class Mul(nn.Module):
    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        return x * y


class NestedListSuperStructure(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.mul = Mul()
        self.lstm = nn.LSTM(
            input_size=40, hidden_size=50, num_layers=2, batch_first=True
        )

    def forward(
        self, a: List[List[List[Tensor]]], b: List[List[List[Tensor]]]
    ) -> List[List[List[Tensor]]]:
        results = []
        for i in range(len(a)):
            inner_results = []
            for j in range(len(a[i])):
                mul_result = self.mul(
                    a[i][j][0], b[i][j][-1]
                )  # multiply first element, and last-element randomly
                lstm_out, _ = self.lstm(mul_result)
                inner_results.append([lstm_out])
            results.append(inner_results)
        return results


def test_nested_list_super_structure():
    model = NestedListSuperStructure()
    B, S, D = 1, 20, 40

    a = [
        [[torch.randn(B, S, D), torch.randn(B, S, D)] for _ in range(2)]
        for _ in range(2)
    ]
    b = [
        [[torch.randn(B, S, D), torch.randn(B, S, D)] for _ in range(2)]
        for _ in range(2)
    ]

    # Quantization
    calib_data = [(a, b), (a, b)]
    out_fp = model(*calib_data[0])

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    cmodel.quantize(calib_data)

    # Verify quantized output
    out_q = cmodel(*calib_data[0])

    # Check that the shapes match
    for out_q_level1, out_fp_level1 in zip(out_q, out_fp):
        for out_q_level2, out_fp_level2 in zip(out_q_level1, out_fp_level1):
            for o_q, o_fp in zip(out_q_level2, out_fp_level2):
                assert (
                    o_q.shape == o_fp.shape
                ), f"Shape mismatch: {o_q.shape} != {o_fp.shape}"


class NestedListSuperStructureSingleInput(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.mul = Mul()
        self.lstm = nn.LSTM(
            input_size=40, hidden_size=50, num_layers=2, batch_first=True
        )

    def forward(self, a: List[List[List[Tensor]]]) -> List[List[List[Tensor]]]:
        results = []
        for i in range(len(a)):
            inner_results = []
            for j in range(len(a[i])):
                mul_result = self.mul(
                    a[i][j][0], a[i][j][-1]
                )  # multiply first element, and last-element randomly
                lstm_out, _ = self.lstm(mul_result)
                inner_results.append([lstm_out])
            results.append(inner_results)
        return results


def test_nested_list_super_structure_single_input():
    model = NestedListSuperStructureSingleInput()
    B, S, D = 1, 20, 40

    a = [
        [[torch.randn(B, S, D), torch.randn(B, S, D)] for _ in range(2)]
        for _ in range(2)
    ]

    """
    We need to pass each sample of the calibration data as a Tuple: (arg_1, arg_2, ..., arg_n).

    This approach is to work around the specific code in `fmot/qat/control.py`, where we hard-code a check to see if `x` 
    is a tuple for handling multiple inputs. 

    We can't simply check if `x` is a tuple or list because if it is a list, it could either be a single-argument multi-dimensional 
    list or multiple arguments, each being a list. 

    Thus, passing data as a tuple (arg1, arg2, ..., arg_n) serves as an identifier for distinguishing multiple inputs from a single input.

    We attempted to generalize this by defining `def get_num_input_args()` in `fmot/qat/control.py`, but this led to unit test failures 
    elsewhere for other reasons.

    if not isinstance(x, tuple):
        out = model(x)
    else:
        out = model(*x)
    """
    calib_data = [(a,), (a,)]
    out_fp = model(*calib_data[0])

    cmodel = fmot.ConvertedModel(model, batch_dim=0, seq_dim=1)
    cmodel.quantize(calib_data)

    # Verify quantized output
    out_q = cmodel(*calib_data[0])

    # Check that the shapes match
    for out_q_level1, out_fp_level1 in zip(out_q, out_fp):
        for out_q_level2, out_fp_level2 in zip(out_q_level1, out_fp_level1):
            for o_q, o_fp in zip(out_q_level2, out_fp_level2):
                assert (
                    o_q.shape == o_fp.shape
                ), f"Shape mismatch: {o_q.shape} != {o_fp.shape}"


if __name__ == "__main__":
    test_nested_list_super_structure()
    test_nested_list_super_structure_single_input()
