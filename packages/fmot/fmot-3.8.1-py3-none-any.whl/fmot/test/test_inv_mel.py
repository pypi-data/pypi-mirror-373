import torch
import math
import fmot
import pytest
from fmot.nn.signal_processing import InverseMelFilterBank


@pytest.mark.parametrize("mode", ["transpose", "transpose_stft_norm", "pinv"])
def test_inverse_mel_filter_bank(mode):
    # Define input parameters
    sr = 16000
    n_fft = 512
    n_mels = 20
    fmin = 0.0
    fmax = None

    # Create test input tensor
    batch_size = 2
    seq_len = 10
    n_feats = n_mels

    # Generate random test input
    input_tensor = torch.randn(batch_size, seq_len, n_feats)

    # Instantiate the full-precision InverseMelFilterBank module
    full_precision_module = InverseMelFilterBank(sr, n_fft, n_mels, fmin, mode, fmax)

    # Forward pass using full-precision model
    full_precision_output = full_precision_module(input_tensor)

    # Generate random calibration inputs
    num_samples = 5
    calibration_inputs = [
        torch.randn(batch_size, seq_len, n_feats) for _ in range(num_samples)
    ]

    # Quantize the full-precision model using fmot
    cmodel = fmot.ConvertedModel(full_precision_module, batch_dim=0, seq_dim=1)
    cmodel.quantize(calibration_inputs)
    fqir_graph = cmodel.trace()

    # Run inference on the quantized model using the test input
    quantized_output = fqir_graph.run(input_tensor.numpy(), dequant=True)

    # Calculate root mean squared error (RMSE) between full-precision and quantized outputs
    rmse = torch.sqrt(
        torch.mean(torch.pow(full_precision_output - quantized_output, 2))
    )

    # Define the tolerance for RMSE
    tolerance = 1e-2

    # Check if the RMSE is within the tolerance
    assert rmse <= tolerance, f"RMSE {rmse} is not within tolerance {tolerance}"
