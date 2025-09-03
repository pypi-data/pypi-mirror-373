import torch
from torch import nn
import fmot
import pytest
from contextlib import nullcontext


class MyModel(nn.Module):
    def __init__(self, function="sigmoid"):
        super().__init__()
        if function == "sigmoid":
            self.fn = nn.Sigmoid()
        elif function == "tanh":
            self.fn = nn.Tanh()
        else:
            raise ValueError()

    def forward(self, x):
        return self.fn(x)


def pytest_raise_or_null(raises=True):
    if raises:
        return pytest.raises(Exception)
    else:
        return nullcontext()


SATURATION_BEHAVIOR = {"sigmoid": [(-8, 0), (8, 1)], "tanh": [(-4, -1), (4, 1)]}


@pytest.mark.parametrize("function", ["sigmoid", "tanh"])
@pytest.mark.parametrize("enable_saturation", [True, False])
def test_nonlin_sat(function, enable_saturation):
    model = MyModel(function)
    fmot.CONFIG.forced_endpoint_saturation = enable_saturation
    cmodel = fmot.ConvertedModel(model)

    # check that the function has been wrapped such that it evaluates to precisely
    # 0/1 where expected
    for input, exp_output in SATURATION_BEHAVIOR[function]:
        with pytest_raise_or_null(not enable_saturation):
            x = torch.linspace(input, input * 2, 500)
            y = cmodel(x)
            assert torch.all(y == exp_output)

    # quantize, run these asserts one last time
    cmodel.quantize([torch.linspace(-16, 16, 500) for _ in range(4)])

    for input, exp_output in SATURATION_BEHAVIOR[function]:
        with pytest_raise_or_null(not enable_saturation):
            x = torch.linspace(input, input * 2, 500)
            y = cmodel(x)
            diff = y - exp_output
            assert torch.allclose(
                y, torch.as_tensor(exp_output, dtype=torch.float), atol=1e-4
            ), f"{y=}\n{exp_output=}\n{diff=}"
            print(diff)


if __name__ == "__main__":
    test_nonlin_sat("sigmoid", True)
    test_nonlin_sat("sigmoid", False)
    test_nonlin_sat("tanh", True)
    test_nonlin_sat("tanh", False)
