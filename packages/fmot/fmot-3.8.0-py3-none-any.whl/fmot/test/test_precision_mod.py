import torch
import fmot


def get_model():
    torch.manual_seed(0)
    model = torch.nn.Sequential(
        torch.nn.ReLU(),
        torch.nn.Linear(32, 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 32),
    )
    inputs = [torch.randn(32, 32) for __ in range(10)]
    return model, inputs


def test_precision_modification():
    model, inputs = get_model()
    cmodel = fmot.ConvertedModel(model, precision="double", interpolate=False)
    cmodel.quantize(inputs)

    x = inputs[0]
    with torch.no_grad():
        y_fp = model(x)
        y_dbl = cmodel(x)
        cmodel.modify_precision("standard")
        y_std = cmodel(x)
    assert y_dbl.bitwidth == fmot.qat.fqint16
    assert y_std.bitwidth == fmot.qat.fqint8
    mse_dbl, mse_std = [(y_fp - y).pow(2).mean() for y in [y_dbl, y_std]]
    assert mse_dbl < mse_std
