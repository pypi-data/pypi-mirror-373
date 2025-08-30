import torch
from torch import nn
import torch.nn.utils.prune as prune

from fmot.sparse.pruning import PencilPruning, pencil_pruning, _pencil_conv1d_pruning
from fmot.sparse.pruning_utils import prune_model_parameters
from fmot.nn import TemporalConv1d


class TestPruning:
    def test_mask_shape(self):
        r"""Checking if the pruning is running correctly
        and that mask has correct shape on a simple case
        """
        my_prune = PencilPruning(amount=0.8, pencil_size=4)
        ncols, nrows = 8, 12
        tensor = torch.nn.Linear(ncols, nrows).weight
        default_mask = tensor * 0 + 1
        mask = my_prune.compute_mask(tensor, default_mask)
        assert mask.shape == tensor.shape

    def test_compute(self):
        r"""Checking if output corresponds to what's expected"""
        # Check 1
        tensor = torch.arange(12, dtype=torch.float64).view(-1, 3)
        expected_output = torch.tensor(
            [[0, 1, 1], [0, 1, 1], [0, 1, 1], [0, 1, 1]], dtype=torch.float64
        )

        my_prune = PencilPruning(amount=0.3, pencil_size=4)
        default_mask = tensor * 0 + 1
        new_mask = my_prune.compute_mask(tensor, default_mask)

        assert torch.all(torch.eq(expected_output, new_mask))

        # Check 2
        tensor = torch.tensor(
            [
                [-5, 4, 4, 6, -7],
                [5, -4, -4, 6, -7],
                [5, -4, -4, 6, -7],
                [5, -4, -4, 6, -7],
            ],
            dtype=torch.float64,
        )
        expected_output = torch.tensor(
            [[0, 0, 0, 1, 1], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1]],
            dtype=torch.float64,
        )

        my_prune = PencilPruning(amount=0.6, pencil_size=4)
        default_mask = tensor * 0 + 1
        new_mask = my_prune.compute_mask(tensor, default_mask)
        assert torch.all(torch.eq(expected_output, new_mask))

    def test_padding(self):
        r"""Checking if padding works"""
        tensor = torch.tensor(
            [
                [1.0, 5.0],
                [1.0, 5.0],
                [1.0, 5.0],
                [1.0, 5.0],
                [10.0, 1.0],
                [10.0, 1.0],
                [10.0, 1.0],
            ],
            dtype=torch.float64,
        )
        expected_output = torch.tensor(
            [
                [0.0, 1.0],
                [0.0, 1.0],
                [0.0, 1.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 0.0],
                [1.0, 0.0],
            ],
            dtype=torch.float64,
        )

        my_prune = PencilPruning(amount=0.5, pencil_size=4)
        default_mask = tensor * 0 + 1
        new_mask = my_prune.compute_mask(tensor, default_mask)

        assert torch.all(torch.eq(expected_output, new_mask))

    def test_module(self):
        r"""Checking if the pruning utility is working directly on modules"""

        class MyNet(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.lin1 = torch.nn.Linear(64, 32)
                self.lin2 = torch.nn.Linear(32, 16)

            def forward(self, inputs):
                return self.W(inputs)

        module = MyNet()
        pencil_pruning(module.lin1, name="weight", amount=0.5, pencil_size=4)

    def test_layer(self):
        r"""Checking if the row major is working as expected on Linear layers"""

        class MyNet(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.lin1 = torch.nn.Linear(8, 2)

            def forward(self, inputs):
                return self.W(inputs)

        module = MyNet()
        pencil_pruning(module.lin1, name="weight", amount=0.75, pencil_size=2)
        # We check 75% of the columns are zero'd out
        assert (torch.sum(module.lin1.weight, 0) == 0).numpy().sum() == int(0.75 * 8)

    def test_stacking(self):
        r"""Checking if we can still stack pruning on top of each other"""

        class MyNet(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.lin1 = torch.nn.Linear(8, 2)

            def forward(self, inputs):
                return self.W(inputs)

        module = MyNet()
        pencil_pruning(module.lin1, name="weight", amount=0.5, pencil_size=2)
        prune.ln_structured(module.lin1, name="weight", amount=0.5, n=2, dim=0)
        assert True

    def test_conv1d_pruning(self):
        r"""Checking if pencil pruning for conv1d behaves as expected"""
        in_channels = 8
        out_channels = 8
        kernel_size = 2

        # For usual Conv1d
        model = TemporalConv1d(in_channels, out_channels, kernel_size)
        new_weight = torch.zeros(model.weight.shape) + 1
        new_weight[0, 0, 0] = 0.0
        model.weight = nn.Parameter(new_weight)
        _pencil_conv1d_pruning(model, "weight", 1 / 8, 8)
        for i in range(out_channels):
            assert model.weight[i, 0, 0] == 0

        # For DW-Conv1d, check that we don't prune
        model = TemporalConv1d(out_channels, out_channels, 3, groups=out_channels)
        new_weight = torch.zeros(model.weight.shape) + 1
        new_weight[0, 0, 0] = 0.0
        model.weight = nn.Parameter(new_weight)
        _pencil_conv1d_pruning(model, "weight", 0.33, 8)
        for i in range(1, out_channels):
            assert model.weight[i, 0, 0] != 0

    def test_prune_model(self):
        # Testing on top level module
        model = nn.Linear(10, 10)
        prune_model_parameters(model, 0.5, min_numel=0)

        # Testing on model with module depth
        model = nn.Sequential(nn.Linear(10, 10), nn.Linear(10, 10))
        prune_model_parameters(model, 0.5, min_numel=0)


if __name__ == "__main__":
    pass

    # model = nn.GRU(128, 128, batch_first=True)
    # fmot.utils.pencil_pruning(model, 'weight_ih_l0', 0.7, 8)
    # qmodel = fmot.convert_torch_to_qat(model, verbose=True)

    from sparse.pruning import conv2d_pruning

    model = nn.Conv2d(8, 64, 3, 1)
    print(model.weight.shape)
    conv2d_pruning(model, "weight", 0.8, 8)
