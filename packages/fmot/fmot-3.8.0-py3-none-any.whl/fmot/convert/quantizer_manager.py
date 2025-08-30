import torch
from ..qat.nn import ParameterQuantizer
from .prune_reparametrization import remove_all_pruners, reapply_all_pruners


def generate_param2quantizer(cmodel, inputs):
    """

    It first removes pruning, otherwise we can't keep a pointer of
    pruned weight as they are on-the-fly
    """
    pruning_info = remove_all_pruners(cmodel)
    param2name = dict()
    for name, param in cmodel.named_parameters():
        # if name.endswith('_orig'):
        #     name = name.split('_orig')[0]
        #     param = rgetattr(cmodel, name)
        param2name[param] = name

    class StoreQuantParam:
        def __init__(self):
            self.param2quant = dict()

        def __call__(self, module, input_param, output_param):
            try:
                name = param2name[input_param[0]]
                self.param2quant[name] = module
            except:
                pass
                # print("Unknwon tensor {}, param2quant mapping".format(input_param) +\
                #       " might be incomplete")

    store = StoreQuantParam()

    hook_handles = []
    for name, module in cmodel.named_modules():
        if isinstance(module, ParameterQuantizer):
            handle = module.register_forward_hook(store)
            hook_handles.append(handle)
    if isinstance(inputs, torch.Tensor):
        _ = cmodel(inputs)
    else:
        _ = cmodel(*inputs)

    for h in hook_handles:
        h.remove()

    reapply_all_pruners(cmodel, cmodel, pruning_info, cmodel._param_mapping_dict)

    return store.param2quant


def generate_param2quantizer(cmodel, inputs):
    """

    It first removes pruning, otherwise we can't keep a pointer of
    pruned weight as they are on-the-fly
    """
    pruning_info = remove_all_pruners(cmodel)
    param2name = dict()
    for name, param in cmodel.named_parameters():
        # if name.endswith('_orig'):
        #     name = name.split('_orig')[0]
        #     param = rgetattr(cmodel, name)
        param2name[param] = name

    class StoreQuantParam:
        def __init__(self):
            self.param2quant = dict()

        def __call__(self, module, input_param, output_param):
            try:
                name = param2name[input_param[0]]
                self.param2quant[name] = module
            except:
                pass
                # print("Unknwon tensor {}, param2quant mapping".format(input_param) +\
                #       " might be incomplete")

    store = StoreQuantParam()

    hook_handles = []
    for name, module in cmodel.named_modules():
        if isinstance(module, ParameterQuantizer):
            handle = module.register_forward_hook(store)
            hook_handles.append(handle)
    if isinstance(inputs, torch.Tensor):
        _ = cmodel(inputs)
    else:
        _ = cmodel(*inputs)

    for h in hook_handles:
        h.remove()

    reapply_all_pruners(cmodel, cmodel, pruning_info, cmodel._param_mapping_dict)

    return store.param2quant
