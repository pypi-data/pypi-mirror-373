import unittest
import torch
import os
from torch import nn

import fmot
from fmot import ConvertedModel


class TestSerialization(unittest.TestCase):
    def test_save_load_feedforward(self):
        r"""Tests if saving and loading models works correctly"""
        model = nn.Linear(3, 4)
        cmodel = ConvertedModel(model, batch_dim=0)
        fmot.save(cmodel, "test_save_model.pth")

        loaded_model = fmot.load("test_save_model.pth")
        for p_name, param in cmodel.named_parameters():
            assert abs(param - fmot.utils.rgetattr(loaded_model, p_name)).sum() == 0.0

        os.remove("test_save_model.pth")

    def test_tuneps(self):
        r"""Tests that TuningEpsilon running max appears in the state dict"""
        tuneps = fmot.nn.TuningEpsilon(eps=0.25)
        input = torch.tensor([8, 8, 8])
        with torch.no_grad():
            _ = tuneps(input)
        assert "running_max" in tuneps.state_dict().keys()
        assert tuneps.epsilon() == 2.0
