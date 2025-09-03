from torch import nn
from fmot.nn.sequencer import StateInitializer
from fmot.qat.nn import StateInitializer as QStateInitializer
import logging

logger = logging.getLogger(__name__)


def set_sequencer_p_inherit(model: nn.Module, p_inherit: float):
    """Enables in-place state inheritance in all sequencer layers
    within the model via state-initializer p-inherit parameter

    Arguments:
        model (nn.Module): the model to enable state-inheritance
        p_inherit (float): probability of carrying state over from one
            batch to the next. Must be between 0 and 1.
    """

    assert 0 <= p_inherit <= 1

    for name, layer in model.named_modules():
        if isinstance(layer, (StateInitializer, QStateInitializer)):
            layer.p_inherit = p_inherit
            logger.info(f"Setting p_inherit={p_inherit} in layer {name}")
