import torch
from ..nn.sparsifiers import ThresholdSparsifier


def actsp_hook_fn(module, _, output):
    r"""
    Forward hook that attach activation sparsity metrics to the sparsifier.
    Args:
        module: a PyTorch model
        _: unused hook argument
        output: the output of the forward pass

    Returns:
        output: the output of the forward pass (unchanged)
    """
    module.actzero = torch.count_nonzero(output, dim=(1, 2)).detach()
    module.act_numel = output.shape[-1] * output.shape[-2]
    module.actsp_penalty = torch.relu(output).sum(-1).sum(-1)
    return output


def register_actsp_hook(model):
    r"""
    Registers hooks for activation sparsity enforcement. The hook will be computed at each forward pass
    of the model. They will be used to gather some metrics necessary to activation penalty computation.

    Args:
        model (torch.nn.Module): a PyTorch model

    Returns:
        hooks: a list of PyTorch hook. Can be used to remove the hoooks from the model later on.
    """
    hooks = []
    for module in model.modules():
        if isinstance(module, ThresholdSparsifier) or isinstance(module, torch.nn.ReLU):
            hooks.append(module.register_forward_hook(actsp_hook_fn))

    return hooks


def remove_hooks(hooks):
    r"""
    Removes hooks for activation sparsity enforcement.

    Args:
        hooks: a list of PyTorch hooks

    Returns:
        None
    """
    for hook in hooks:
        hook.remove()


def compute_actsp(model, reduce="none"):
    r"""



    Args:
        model (torch.nn.Module): a PyTorch model
        reduce: specifies the reduction to apply to the output: 'none' or 'mean'.
            'none': no reduction will be applied

    Returns:
        act_sp (torch.Tensor): a tensor containing activation sparsity patterns.
        act_pen (torch.Tensor): a tensor containing activation penalties.
    """
    act_zeros = 0.0
    act_pen = 0.0
    act_numel = 0
    for module in model.modules():
        if isinstance(module, ThresholdSparsifier):
            if module.actzero is None:
                raise RuntimeError(
                    "Sparsifier attributes are set to None. You should register activation hooks "
                    "before retrieving activation sparsity metrics."
                )
            act_zeros += module.actzero
            act_numel += module.act_numel
            act_pen += module.actsp_penalty

    act_sp = act_zeros / act_numel
    act_pen = act_pen / act_numel
    if reduce == "mean":
        act_sp = act_sp.mean()
        act_pen = act_pen.mean()
    elif reduce == "none":
        pass
    else:
        raise Exception("Unknown reductio operator.")

    return act_sp, act_pen
