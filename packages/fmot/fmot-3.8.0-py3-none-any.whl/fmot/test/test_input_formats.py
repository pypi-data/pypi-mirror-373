import torch
from torch import nn, Tensor
import fmot
import pytest
import numpy as np
from typing import *

"""CALLING MODEL WITH KWARGS"""


class MyKwargModel(nn.Module):
    """Model is antisymmetric w.r.t a and b.
    If they get switched, output will not be the same."""

    def forward(self, a, b):
        y = a - b
        return y


def test_call_model_with_kwargs():
    model = MyKwargModel()
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([(torch.randn(8, 8), torch.randn(8, 8)) for _ in range(3)])

    a = torch.randn(8, 8)
    b = torch.randn(8, 8)

    y1 = cmodel(a, b)
    y2 = cmodel(a, b=b)
    y3 = cmodel(b=b, a=a)
    y4 = cmodel(a=a, b=b)

    def assert_same(x: torch.Tensor, y: torch.Tensor):
        x = x.numpy()
        y = y.numpy()

        assert np.array_equal(x, y)

    for z in [y2, y3, y4]:
        assert_same(y1, z)


"""INPUTS IN DATA STRUCTURES"""


class BaseTestModel(nn.Module):
    expected_signature: List[str] = []

    def get_inputs(self):
        raise NotImplementedError()


class TensorDictModel(BaseTestModel):
    expected_signature = ["x", "config.a"]

    def forward(self, x: Tensor, config: Dict[str, Tensor]):
        a = config["a"]
        return x + a

    def get_inputs(self):
        x = torch.randn(8, 8)
        a = torch.randn(8, 8)
        return (x, {"a": a})


class DictTensorModel(BaseTestModel):
    expected_signature = ["config.a", "x"]

    def forward(self, config: Dict[str, Tensor], x: Tensor):
        a = config["a"]
        return x + a

    def get_inputs(self):
        x = torch.randn(8, 8)
        a = torch.randn(8, 8)
        return ({"a": a}, x)


class DictOfDictModel(BaseTestModel):
    expected_signature = ["config.subconfig.a", "config.subconfig.b"]

    def forward(self, config: Dict[str, Dict[str, Tensor]]):
        a = config["subconfig"]["a"]
        b = config["subconfig"]["b"]
        return a + b

    def get_inputs(self):
        a = torch.randn(8, 8)
        b = torch.randn(8, 8)
        return ({"subconfig": {"a": a, "b": b}},)


class ListModel(BaseTestModel):
    expected_signature = ["inputs.0", "inputs.1"]

    def forward(self, inputs: List[Tensor]):
        a = inputs[0]
        b = inputs[1]
        return a + b

    def get_inputs(self):
        a = torch.randn(8, 8)
        b = torch.randn(8, 8)
        return ([a, b],)


class ListOfDictModel(BaseTestModel):
    expected_signature = ["configs.0.a", "configs.1.b"]

    def forward(self, configs: List[Dict[str, Tensor]]):
        a = configs[0]["a"]
        b = configs[1]["b"]
        return a + b

    def get_inputs(self):
        a = torch.randn(8, 8)
        b = torch.randn(8, 8)
        return ([{"a": a}, {"b": b}],)


class CrazyModel(BaseTestModel):
    expected_signature = [
        "x",
        "list_params.0",
        "list_params.1",
        "dynamic_params.0.a",
        "dynamic_params.1.b",
    ]

    def forward(
        self,
        x: Tensor,
        list_params: List[Tensor],
        dynamic_params: List[Dict[str, Tensor]],
    ):
        a = dynamic_params[0]["a"]
        b = dynamic_params[1]["b"]
        c = list_params[0]
        d = list_params[1]
        return x + a + b + c + d

    def get_inputs(self):
        a = torch.randn(8, 8)
        b = torch.randn(8, 8)
        c = torch.randn(8, 8)
        d = torch.randn(8, 8)
        x = torch.randn(8, 8)
        return (
            x,
            [c, d],
            [{"a": a}, {"b": b}],
        )


TEST_TYPES = [
    DictTensorModel,
    TensorDictModel,
    DictOfDictModel,
    ListModel,
    ListOfDictModel,
    CrazyModel,
]


@pytest.mark.parametrize("model_class", TEST_TYPES)
@torch.no_grad()
def test_typed_model(model_class: Callable[..., BaseTestModel], print_graph=False):
    model = model_class()
    cmodel = fmot.ConvertedModel(model)
    x = model.get_inputs()
    y0 = model(*x)
    y1 = cmodel(*x)

    mse = (y0 - y1).pow(2).mean() / y0.pow(2).mean()
    assert mse < 1e-3

    print(f"Calling success: {type(model)}")

    inputs = [model.get_inputs() for _ in range(4)]
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize(inputs)
    graph = cmodel.trace(*model.get_inputs())

    print(f"Tracing success: {type(model)}")

    signature = [t.name for t in graph.subgraphs["ARITH"].inputs]
    assert all(a == b for a, b in zip(signature, model.expected_signature))

    print(f"Signature matching success: {type(model)} {model.expected_signature}")

    if print_graph:
        print(graph.subgraphs["ARITH"])


"""OPTIONAL INPUTS"""


class OptionalInputModelA(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(32, 32)

    def forward(self, x: Tensor, y: Optional[Tensor] = None):
        z = self.lin(x)
        if y is not None:
            z = self.lin(y)
        return z


class OptionalInputModelB(fmot.nn.SuperStructure):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(32, 32)

    def forward(self, x: Optional[Tensor] = None, y: Optional[Tensor] = None):
        if x is not None:
            if y is None:
                z = self.lin(x)
            else:
                z = self.lin(y)
        elif y is not None:
            z = self.lin(y)
        else:
            raise ValueError("Expected nonzero x or y")
        return z


@pytest.mark.parametrize("y_mode", ["none", "skip", "include"])
def test_optional_inputs_a(y_mode: str):
    model = OptionalInputModelA()
    cmodel = fmot.ConvertedModel(model)

    if y_mode == "none":
        inputs = [(torch.randn(32, 32), None) for _ in range(4)]
    elif y_mode == "skip":
        inputs = [torch.randn(32, 32) for _ in range(4)]
    elif y_mode == "include":
        inputs = [(torch.randn(32, 32), torch.randn(32, 32)) for _ in range(4)]

    cmodel.quantize(inputs)
    graph = cmodel.trace()


@pytest.mark.parametrize("mode", ["xn", "xs", "xy", "ny"])
def test_optional_inputs_b(mode: str):
    model = OptionalInputModelB()
    cmodel = fmot.ConvertedModel(model)

    def get_input():
        input = []
        if mode[0] == "x":
            input.append(torch.randn(32, 32))
        elif mode[0] == "n":
            input.append(None)
        else:
            assert False

        if mode[1] == "y":
            input.append(torch.randn(32, 32))
        elif mode[1] == "n":
            input.append(None)
        elif mode[1] == "s":
            pass
        else:
            assert False

        if len(input) == 1:
            return input[0]
        else:
            return tuple(input)

    inputs = [get_input() for _ in range(4)]
    cmodel.quantize(inputs)
    graph = cmodel.trace()
