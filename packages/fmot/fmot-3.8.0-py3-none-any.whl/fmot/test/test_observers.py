import fmot
import torch
from torch import nn
import pytest

OBSERVERS = [
    # observer                                      config
    (fmot.qat.nn.MinMaxObserver, None),
    (fmot.qat.nn.MovingAverageMinMaxObserver, dict(alpha=0.9)),
    (fmot.qat.nn.MovingAverageMinMaxObserver, dict(alpha=0.95)),
    (fmot.qat.nn.GaussianObserver, dict(ignore_zero=True)),
    (fmot.qat.nn.GaussianObserver, dict(ignore_zero=False)),
]

OBSERVER_DEFAULT_VALS_MAP = {
    # observer                  (attribute, default_val)
    fmot.qat.nn.MinMaxObserver: [
        ("min_val", torch.tensor([])),
        ("max_val", torch.tensor([])),
    ],
    fmot.qat.nn.MovingAverageMinMaxObserver: [
        ("min_val", torch.tensor([])),
        ("max_val", torch.tensor([])),
    ],
    fmot.qat.nn.FixedRangeObserver: [
        ("min_val", torch.tensor([])),
        ("max_val", torch.tensor([])),
    ],
    fmot.qat.nn.GaussianObserver: [
        ("N", torch.tensor(0)),
        ("running_x", torch.tensor(0)),
        ("running_x2", torch.tensor(0)),
        ("maxabs", torch.tensor(0)),
    ],
}


class MyModel(nn.Module):
    def __init__(self, Din, H, Dout):
        super().__init__()
        self.Din = Din
        self.H = H
        self.Dout = Dout
        self.l0 = nn.Linear(Din, H)
        self.l1 = nn.GRU(H, H, batch_first=True)
        self.l2 = nn.Linear(H, Dout)

    def forward(self, x):
        x = self.l0(x).relu()
        x, __ = self.l1(x)
        x = self.l2(x)
        return x

    def get_random_input(self, B, T):
        return torch.randn(B, T, self.Din)

    def get_quantized_model(
        self,
        observer,
        observer_config,
        precision="double",
        interpolate=False,
        B=16,
        T=10,
        N=5,
    ):
        inputs = [self.get_random_input(B, T) for __ in range(N)]
        cmodel = fmot.ConvertedModel(
            model=self,
            batch_dim=0,
            seq_dim=1,
            precision=precision,
            observer=observer,
            observer_config=observer_config,
        )
        cmodel.quantize(inputs)
        return cmodel

    @torch.no_grad()
    def measure_nqmse(
        self,
        observer,
        observer_config,
        precision="double",
        interpolate=False,
        B=16,
        T=8,
        N=5,
    ):
        """
        Returns normalized quantized mean squared error
        """
        qmodel = self.get_quantized_model(
            observer, observer_config, precision, interpolate, B, T, N
        )
        x = self.get_random_input(B, T)
        # hopefully get rid of this api soon
        x.dimensions = ["B", "T", "F"]
        yfp = self(x)
        yq = qmodel(x)
        mse = (yfp - yq).pow(2).mean() / (yfp.pow(2).mean())
        return mse


@pytest.mark.parametrize("observer,observer_config", OBSERVERS)
def test_conversion(observer, observer_config):
    model = MyModel(32, 64, 32)
    try:
        model.get_quantized_model(observer, observer_config)
    except:
        raise Exception(f"Could not convert model with observer {observer.__name__}")


@pytest.mark.parametrize("observer,observer_config", OBSERVERS)
def test_reset_observers(observer, observer_config):
    model = MyModel(32, 64, 32)
    cmodel = model.get_quantized_model(observer, observer_config)

    # Check One - On Quantizing, the Observer attributes SHOULD NOT BE default values
    for module in cmodel.modules():
        if isinstance(module, fmot.qat.nn.ObserverBase):
            for attribute, default_val in OBSERVER_DEFAULT_VALS_MAP[type(module)]:
                assert not torch.equal(getattr(module, attribute), default_val)

    cmodel.reset_observers()

    # Check Two - On calling cmodel.reset_observers(), the Observer attributes SHOULD BE set to default values
    for module in cmodel.modules():
        if isinstance(module, fmot.qat.nn.ObserverBase):
            for attribute, default_val in OBSERVER_DEFAULT_VALS_MAP[type(module)]:
                assert torch.equal(getattr(module, attribute), default_val)

    sample_input = model.get_random_input(2, 5)
    out = cmodel(sample_input)
