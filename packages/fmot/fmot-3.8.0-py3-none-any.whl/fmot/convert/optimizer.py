import torch
from copy import deepcopy
from ..utils import rgetattr


def get_id2name_dict(model):
    id2name_dict = dict()
    for param_id, (name, param) in enumerate(model.named_parameters()):
        id2name_dict[param_id] = name

    return id2name_dict


# This is to create the equivalent generator
def new_param_generator(model, qmodel):
    """Create a Module.parameters generator for the quantized model qmodel
    with the same parameter ordering as the initial model
    """
    for name, param in model.named_parameters():
        if name in qmodel.substitutions_dict.keys():
            new_param_name, _ = qmodel.substitutions_dict[name]
        else:
            new_param_name = name
        yield rgetattr(qmodel, "model." + new_param_name)
