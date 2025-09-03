import fmot
from fmot import CONFIG, ROUND_CONFIG
import torch
from torch import nn


def test_vvadd():
    ROUND_CONFIG.add = True

    CONFIG.quant_round = True
    add = fmot.nn.VVAdd()
    cmodel = fmot.ConvertedModel(add)
    assert cmodel.model.model.round

    CONFIG.quant_round = False
    cmodel = fmot.ConvertedModel(add)
    assert not cmodel.model.model.round


def test_prod():
    ROUND_CONFIG.prod = True

    lin = nn.Linear(32, 32)

    CONFIG.quant_round = True
    cmodel = fmot.ConvertedModel(lin)
    assert cmodel.model.model.multiplier.round

    CONFIG.quant_round = False
    cmodel = fmot.ConvertedModel(lin)
    assert not cmodel.model.model.multiplier.round


def test_mul():
    ROUND_CONFIG.mul = True

    mul = fmot.nn.VVMul()

    CONFIG.quant_round = True
    cmodel = fmot.ConvertedModel(mul)
    assert cmodel.model.model.round

    CONFIG.quant_round = False
    cmodel = fmot.ConvertedModel(mul)
    assert not cmodel.model.model.round


if __name__ == "__main__":
    test_vvadd()
    test_prod()
    test_mul()
