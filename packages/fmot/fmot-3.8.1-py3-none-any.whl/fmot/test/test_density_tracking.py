import fmot
import torch
from torch import nn
import unittest
from fmot.qat.nn.density_matmul import _MMBase

torch.manual_seed(0)
MODEL = torch.nn.Sequential(
    torch.nn.ReLU(), torch.nn.Linear(32, 64), torch.nn.ReLU(), torch.nn.Linear(64, 32)
)
INPUTS = [torch.randn(32, 32) for __ in range(10)]
metrics = ["act_density", "fanout_density", "lookup_density"]


class ActDensityTest(unittest.TestCase):
    def test_density_metric_api(self):
        """Tests that act. density API is running correctly."""
        cmodel = fmot.ConvertedModel(MODEL)

        self.assertRaises(
            fmot.exceptions.ConversionDependencyError,
            cmodel.measure_density_metrics,
            *metrics
        )

        __ = cmodel(INPUTS[0])
        _ = cmodel.measure_density_metrics(*metrics)

    def test_density_logic(self):
        """Checks the logic of act., lookup and fanout densities
        on a simple example."""
        model = torch.nn.Sequential(torch.nn.ReLU(), torch.nn.Linear(2, 4))
        model[1].weight = nn.Parameter(
            torch.tensor([[0.0, 2.0], [0.0, 2.0], [1.0, 2.0], [1.0, 2.0]])
        )
        input = torch.tensor([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
        cmodel = fmot.ConvertedModel(model)
        metrics = ["act_density", "fanout_density", "lookup_density"]

        self.assertRaises(
            fmot.exceptions.ConversionDependencyError,
            cmodel.measure_density_metrics,
            *metrics
        )

        __ = cmodel(input)
        densities = cmodel.measure_density_metrics(*metrics)
        assert densities["act_density"] == 0.5
        assert densities["fanout_density"] == 1 / 3
        assert densities["lookup_density"] == 1 / 4

    def test_density_backprop(self):
        """Checks that we can use act. density in the loss function
        and backpropagate the gradient"""
        cmodel = fmot.ConvertedModel(MODEL)
        for metric in metrics:
            __ = cmodel(INPUTS[0])
            loss = cmodel.measure_density_metrics(metric)[metric]
            loss.backward()

    def test_density_print(self):
        """Checks that the QuantRELU representation
        with activation density works"""
        cmodel = fmot.ConvertedModel(MODEL)
        print(cmodel)
        __ = cmodel(INPUTS[0])
        _ = cmodel.measure_density_metrics("act_density")["act_density"]
        print(cmodel)

    def test_high_dim(self):
        """Check is the activation density API works on
        Linear layer with high dimension inputs"""
        model = nn.Sequential(nn.ReLU(), nn.Linear(2, 4))
        model[1].weight = nn.Parameter(
            torch.tensor([[0.0, 2.0], [0.0, 2.0], [1.0, 2.0], [1.0, 2.0]])
        )
        input = torch.tensor(
            [[[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]], [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]]
        )
        cmodel = fmot.ConvertedModel(model)
        _ = cmodel(input)
        densities = cmodel.measure_density_metrics("act_density")

        assert densities["act_density"] == 0.5
        for module in cmodel.modules():
            if isinstance(module, _MMBase) and module.has_sparse_input:
                assert module.nb_iter == 3 * 2


if __name__ == "__main__":
    ActDensityTest().test_density_logic()
    ActDensityTest().test_density_print()
    ActDensityTest().test_high_dim()
