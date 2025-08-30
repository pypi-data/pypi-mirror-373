import torch
from torch import nn
import fmot
from fmot.qat.nn import (
    ObserverBase,
    Quantizer,
    QuantileMinMaxObserver,
    ParameterQuantizer,
    MinMaxObserver,
)
import pytest


def test_quantile_observer():
    model = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 64))

    def check_observer(model, obs_class=QuantileMinMaxObserver, **kwargs):
        cmodel = fmot.ConvertedModel(model, batch_dim=0, **kwargs)
        for name, module in cmodel.named_modules():
            if isinstance(module, Quantizer):
                if "bias" not in name and "weight" not in name:
                    assert isinstance(module.observer, obs_class)

    # assert that it uses QuantileMinMaxObserver if we set the observer to "quantile99"
    check_observer(model, QuantileMinMaxObserver, observer="quantile99")

    # assert that it uses MinMaxObserver by default
    check_observer(model, MinMaxObserver)

    # check that the quantile value is properly set by the observer string
    def check_quantile_value(name, value):
        cmodel = fmot.ConvertedModel(model, batch_dim=0, observer=name)
        for name, module in cmodel.named_modules():
            if isinstance(module, Quantizer):
                if "bias" not in name and "weight" not in name:
                    assert isinstance(module.observer, QuantileMinMaxObserver)
                    assert module.observer.quantile == value

    check_quantile_value("quantile99", 0.99)
    check_quantile_value("quantile85", 0.85)


@pytest.mark.parametrize(
    ["quantile", "outlier_value", "expected_maxval"],
    [[0.99, 0.997, 1], [0.99, -1000, 1], [1, 1, 1]],
)
def test_outlier_rejection(quantile, outlier_value, expected_maxval):
    class IdModel(nn.Module):
        def forward(self, x):
            return x + 0

    model = IdModel()
    cmodel = fmot.ConvertedModel(
        model, batch_dim=0, observer=f"quantile{int(quantile*100)}"
    )

    calib = torch.rand(8, 1000) * 2 - 1
    calib[0, 500] = outlier_value

    cmodel.quantize([calib] * 4)

    y = cmodel(calib)
    mv = y.abs().max()

    assert mv <= expected_maxval, f"maxval {mv} was not less than {expected_maxval}"


def test_observer_tagging():
    class MyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.minmax_layer = nn.Sequential(nn.Linear(32, 32), nn.ReLU())
            self.quantile_layer = nn.Sequential(nn.Linear(32, 32), nn.ReLU())
            self.quantile_layer.observer_class = "quantile99"
            self.minmax_layer.observer_class = "minmax"

        def forward(self, x):
            x = self.minmax_layer(x)
            x = self.quantile_layer(x)

            return x

    cmodel = fmot.ConvertedModel(
        MyModel(), batch_dim=0, seq_dim=1, observer="quantile99"
    )

    for name, module in cmodel.named_modules():
        if isinstance(module, ObserverBase):
            if "weight" not in name and "bias" not in name:
                if "minmax_layer" in name:
                    assert isinstance(module, MinMaxObserver)
                elif "quantile_layer" in name:
                    assert isinstance(
                        module, QuantileMinMaxObserver
                    ), f"module {name} was expected to be QuantileMinMaxObserver, was {type(module)}"


if __name__ == "__main__":
    test_observer_tagging()


# if __name__ == '__main__':
#     # test_quantile_observer()
#     test_outlier_rejection(0.99, 1000, 1)
#     test_outlier_rejection(0.99, -1000, 1)

#     test_outlier_rejection(1.0, 1000, 1)
