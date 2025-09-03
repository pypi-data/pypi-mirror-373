from fmot.convert.conversion_api import ConvertedModel
from fmot.qat.nn import BatchNorm


def freeze_batchnorm(model: ConvertedModel, frozen=True):
    """Freeze BatchNorm statistics within a ConvertedModel. Recurses through the
    model and freezes all BatchNorm layers.

    Arguments:
        model (ConvertedModel): ConvertedModel --
            could be quantized or still in full-precision mode
        frozen (bool, optional): default True, in which case batch-norm
            statistics are frozen. If False, will un-freeze batch-norm statistics.
    """

    assert isinstance(model, ConvertedModel)
    assert isinstance(frozen, bool)

    for module in model.modules():
        if isinstance(module, BatchNorm):
            module.frozen = frozen
