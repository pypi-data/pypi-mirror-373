"""Test model Conversion, Quantization, and Tracing (CQT)"""
import pytest
import torch

from fmot import ConvertedModel

DIM = 8
FF_LIN = torch.nn.Linear(DIM, DIM)


@pytest.mark.parametrize(
    "                model,  test_input,           batch_dim, seq_dim",
    [
        pytest.param(
            FF_LIN,
            torch.randn(8),
            None,
            None,
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        (FF_LIN, torch.randn(1, 8), 0, None),
        pytest.param(
            FF_LIN,
            torch.randn(1, 8),
            None,
            0,
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        (FF_LIN, torch.randn(1, 1, 8), 0, 1),
        (FF_LIN, torch.randn(1, 1, 8), 1, 0),
        (FF_LIN, torch.randn(2, 8), 0, None),
        pytest.param(
            FF_LIN,
            torch.randn(2, 8),
            None,
            0,
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        (FF_LIN, torch.randn(2, 2, 8), 0, 1),
        (FF_LIN, torch.randn(2, 2, 8), 1, 0),
    ],
)
def test_cqt(model, test_input, batch_dim, seq_dim):
    sample_inputs = [test_input for _ in range(3)]
    cmodel = ConvertedModel(model, batch_dim=batch_dim, seq_dim=seq_dim)
    # cmodel.quantize(sample_inputs)
    # cmodel.trace()


if __name__ == "__main__":
    pytest.main(["-s", "-o", "log_cli=True", "--log-cli-level=INFO", __file__])
