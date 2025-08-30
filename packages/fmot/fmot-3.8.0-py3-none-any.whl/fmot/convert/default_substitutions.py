import fmot
from inspect import signature
import torch
from ..utils.typing import SubstDict
from ..nn.sru import SRU
from ..nn.special_rnn import DilatedLSTM, ConvertedDilatedLSTM
from ..nn.blockrnn import BlockGRU, ConvertedBlockGRU, BlockLSTM, ConvertedBlockLSTM
from ..nn.bandrnn import (
    BandGRU,
    BidirectionalBandGRU,
    BandLSTM,
    BidirectionalBandLSTM,
    ConvertedUnidirectionalBandLSTM,
    ConvertedUnidirectionalBandGRU,
    ConvertedBidirectionalBandGRU,
    ConvertedBidirectionalBandLSTM,
)

# You need to define a _from_torchmodule method if you add an entry to the DEFAULT_SUBSTITUTIONS dict
DEFAULT_SUBSTITUTIONS = {
    BlockGRU: ConvertedBlockGRU,
    BlockLSTM: ConvertedBlockLSTM,
    BandGRU: ConvertedUnidirectionalBandGRU,
    BidirectionalBandGRU: ConvertedBidirectionalBandGRU,
    BandLSTM: ConvertedUnidirectionalBandLSTM,
    BidirectionalBandLSTM: ConvertedBidirectionalBandLSTM,
    torch.nn.modules.rnn.RNN: fmot.nn.RNN,
    torch.nn.modules.rnn.GRU: fmot.nn.GRU,
    torch.nn.modules.rnn.LSTM: fmot.nn.LSTM,
    SRU: fmot.nn.SRUSequencer,
    fmot.nn.TemporalConvTranspose1d: fmot.nn.transposed_conv1d.FoldTemporalConvTranspose1d,
    DilatedLSTM: ConvertedDilatedLSTM,
    torch.nn.GLU: fmot.nn.GLU,
}


def from_torchmodule_template(
    cls, parent, toplevel=None, inherited_name="", inherited_dict=SubstDict
):
    """This is a template of how the `from_torchmodule` class method of a model used as a value in
    the DEFAULT_SUBSTITUTIONS dict should be defined. This will be used in the conversion step in order to map a
    torch model layers and parameters to its converted version. It will also take care of any transferomation in
    the weights that will be necessary to produce the same mathematical logic in the torch formulation vs the
    formulation in the substituted layer.

    Args:
        cls (type, metaclass): the class referenced in the class method
        parent (torch.nn.Module): the parent torch model whose parameters should be transfered to the new
            substituted fmot layer
        toplevel (bool): if whether or not the model is at the top level of the model tree.
        inherited_name (str): the name inherited from higher level models. For example, if the layer
            is model.conv_block.conv, the inherited name for the conv layer would be model.conv_block
        inherited_dict (fmot.SubstDict): the dictionary mapping the full path name of the parameter in the torch model
            to a tuple with the full path name of the parameter in the new substituted layer and the associated
            transformative function. For example, if model.conv_block.conv is the original layer and is
            mapped to cmodel.conv_block.linear in the converted model, then
            inherited_dict["model.conv_block.conv.weight"] = ("cmodel.conv_block.linear.weight", f) where
            linear.weight = f(conv.weight)

    Returns:
        s_model (torch.nn.Module): the model to substitute with inherited parameters

    """
    raise Exception("Not implemented. This is a template.")


def follows_template(func):
    try:
        sig_func = signature(func)
    except NameError:
        raise Exception(
            "{} is a substitution module but has no `_from_torchmodule`. Refer to"
            " default_substitutions.py for more information."
        )
    sig_template = signature(from_torchmodule_template)

    return sig_func == sig_template


def get_default_substitutions():
    """Apply config settings (e.g. turn on/off LSTM substitution mapping)"""
    substitutions = DEFAULT_SUBSTITUTIONS.copy()
    return substitutions


if __name__ == "__main__":
    for subst_class in DEFAULT_SUBSTITUTIONS.values():
        follows_template(subst_class._from_torchmodule)
