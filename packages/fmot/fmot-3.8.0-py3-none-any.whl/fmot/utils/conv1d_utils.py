import torch
import numpy as np
import re
from typing import Callable

from .rich_attr import rgetattr


def flatten_conv_matrix(
    weight: torch.nn.parameter.Parameter, out_channels, in_channels, kernel_size
) -> torch.nn.parameter.Parameter:
    return torch.transpose(weight, 1, 2).reshape(
        out_channels, in_channels * kernel_size
    )


def inv_flatten_conv_matrix(weight, out_channels, in_channels, kernel_size):
    return torch.transpose(weight.reshape(out_channels, kernel_size, in_channels), 1, 2)


def flatten_conv_matrix_wrapper(
    out_channels, in_channels, kernel_size
) -> Callable[[torch.nn.parameter.Parameter], torch.nn.parameter.Parameter]:
    def f(x: torch.nn.parameter.Parameter):
        return flatten_conv_matrix(x, out_channels, in_channels, kernel_size)

    return f


def inv_flatten_conv_matrix_wrapper(out_channels, in_channels, kernel_size):
    def f(x):
        return inv_flatten_conv_matrix(x, out_channels, in_channels, kernel_size)

    return f


def inv_cat_flatten_conv_matrix_wrapper(out_channels, in_channels, kernel_size):
    def f(qmodel, children_dict):
        groups = []
        for tensor_name in children_dict.keys():
            tensor = rgetattr(qmodel, tensor_name)
            groups.append(
                inv_flatten_conv_matrix(tensor, out_channels, in_channels, kernel_size)
            )
        return torch.cat(groups, 0)

    return f


def cat_wrapper():
    def f(qmodel, children_dict):
        tensor_list = [
            rgetattr(qmodel, tensor_name) for tensor_name in children_dict.keys()
        ]
        return torch.cat(tensor_list, 0)

    return f


def dw_subslct_wrapper(id_group, K, id_kernel):
    def f(weight):
        index = torch.tensor([id_kernel]).to(weight.device)
        return torch.index_select(weight[id_group::K], dim=-1, index=index).squeeze(-1)

    return f


def dw_inv_wrapper(id_group, K, id_kernel):
    def f(param, sub_param):
        return param.index_copy_(0, torch.tensor([0]), torch.zeros([1, 1, 3]))

    return f


def dw_F_inv(shape, K, kernel_size):
    def f(qmodel, children_dict):
        orig_param = torch.zeros(shape)
        pass_weight = dict()
        for id_pass in range(K):
            pass_weight[id_pass] = [None for _ in range(kernel_size)]
        for param_name, f_tuple in children_dict.items():
            if param_name[-6:] == "weight":
                str_split = re.search("lin_list.(.*).weight", param_name)
                id_param = int(str_split.group(1))
                new_sub_param = (
                    rgetattr(
                        qmodel,
                        param_name.replace(
                            "lin_list." + str(id_param) + ".weight",
                            "weight_list." + str(id_param),
                        ),
                    )
                    .unsqueeze(-1)
                    .unsqueeze(-1)
                )
            elif param_name[-4:] == "bias":
                str_split = re.search("lin_list.(.*).bias", param_name)
                id_param = int(str_split.group(1))
                new_sub_param = rgetattr(
                    qmodel, param_name.replace("lin_list.0.bias", "bias_list.0")
                )
            id_pass = id_param // kernel_size
            pass_weight[id_pass][id_param % kernel_size] = new_sub_param

        for id_pass in range(K):
            pass_weight[id_pass] = torch.cat(pass_weight[id_pass], -1)
            indices = torch.tensor(np.arange(id_pass, shape[0], K))
            orig_param.index_copy_(0, indices, pass_weight[id_pass])
        return orig_param

    return f


def is_depthwise(tcn):
    """Returns True if the TCN is a DepthWise Conv"""
    try:
        return tcn.groups == tcn.in_channels
    except AttributeError:
        raise Exception(
            "Convolution-related attributes (groups, in_channels) are missing."
        )
