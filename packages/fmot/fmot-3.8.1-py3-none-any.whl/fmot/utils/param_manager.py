import torch


def get_trailing_digits(bitwidth):
    s = str(bitwidth)
    p = len(s) - 1
    digits = ""
    while s[p].isdigit() and p >= 0:
        digits = s[p] + digits
        p -= 1
    return int(digits)


def memory_format(memory_size):
    if isinstance(memory_size, str):
        return memory_size
    power = 1.0
    n = 0
    units = {0: "", 1: "k", 2: "M", 3: "G", 4: "T"}
    while memory_size > power * 2**10:
        power *= 2**10
        n += 1
        if n >= 4:
            break
    return f"{(memory_size / power):0.1f}" + " " + units[n] + "B"


def get_nb_param(param):
    nb_param = 1.0
    for dim in param.shape:
        nb_param *= dim
    return nb_param


def get_param_density(param):
    nb_param = get_nb_param(param)
    return float(1.0 - torch.sum(param == 0) / nb_param)


def get_param_memory(param, param_quantizer):
    """Returns parameter memory in Bytes"""
    density = get_param_density(param)
    bitwidth = get_trailing_digits(param_quantizer.bitwidth)
    memory = density * get_nb_param(param) * bitwidth
    return memory / 8.0


def get_param_attributes(param, param_quantizer, formatting=True):
    """Density and memory will be updated automatically
    if model is called with enabled densities and if model is
    traced respectively
    """
    attr_dict = dict()
    attr_dict["shape"] = param.shape
    attr_dict["density"] = get_param_density(param)
    if param_quantizer is None:
        attr_dict["precision"] = "N/A"
        attr_dict["memory"] = "N/A"
    else:
        attr_dict["precision"] = param_quantizer.bitwidth
        attr_dict["memory"] = get_param_memory(param, param_quantizer)
    if formatting:
        attr_dict["shape"] = str(tuple(attr_dict["shape"]))
        attr_dict["precision"] = str(attr_dict["precision"])
        attr_dict["density"] = "{0:.1f} %".format(attr_dict["density"] * 100)
        attr_dict["memory"] = memory_format(attr_dict["memory"])

    return attr_dict


def generate_param_table(model):
    param_dict = dict()
    for name, param in model.named_parameters():
        param_quantizer = (
            model.param2quant[name] if model.param2quant is not None else None
        )
        param_dict[name] = get_param_attributes(param, param_quantizer)

    return param_dict
