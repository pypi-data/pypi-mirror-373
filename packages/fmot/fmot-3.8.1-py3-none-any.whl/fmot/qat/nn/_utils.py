import torch


def intitem(x):
    if isinstance(x, torch.Tensor):
        return int(x.detach().cpu().item())
    elif isinstance(x, int):
        return x
    elif isinstance(x, float):
        return int(x)
    else:
        raise Exception(f"Did not expect type {type(x)}")
