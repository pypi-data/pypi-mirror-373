import pdb
import torch
from torch import nn
from . import atomics, quantizers
from functools import partial


class BatchNorm(nn.Module):
    def __init__(
        self,
        num_features,
        bitwidth,
        eps=1e-5,
        momentum=0.1,
        affine=True,
        track_running_stats=True,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
    ):
        super().__init__()
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        if not track_running_stats:
            raise ValueError("BatchNorm1d must set track_running_stats=True")

        names = ["running_mean", "running_var"]
        values = [0, 1]
        req_grad = [False, False]
        if affine:
            names += ["gamma", "beta"]
            values += [1, 0]
            req_grad += [True, True]
        for name, value, rg in zip(names, values, req_grad):
            self.register_parameter(
                name, nn.Parameter(torch.ones(num_features) * value, requires_grad=rg)
            )
            setattr(
                self,
                f"{name}_quant",
                quantizers.ParameterQuantizer(bitwidth, observer=observer),
            )

        self.mean_sub = atomics.VVSub(bitwidth, observer=observer)
        self.inv_std_mul = atomics.VVMul(bitwidth, observer=observer)
        if affine:
            self.gamma_mul = atomics.VVMul(bitwidth, observer=observer)
            self.beta_add = atomics.VVAdd(bitwidth, observer=observer)

        self.frozen = False

    @torch.no_grad()
    def update_stats(self, x, dim=1):
        dims = list(range(x.dim()))
        dims.remove(dim)

        # update running mean
        x_mean = x.mean(dims)
        self.running_mean = nn.Parameter(self.running_mean.to(x.device))
        new_mean = (self.momentum) * self.running_mean + (1 - self.momentum) * x_mean
        self.running_mean.data[:] = new_mean

        # update running inverse std
        x_var = x.var(dim=dims, unbiased=False)
        self.running_var = nn.Parameter(self.running_var.to(x.device))
        new_var = (self.momentum) * self.running_var + (1 - self.momentum) * x_var
        self.running_var.data[:] = new_var

    def forward(self, x):
        if self.training and not self.frozen:
            self.update_stats(x)

        running_mean = self.running_mean
        running_inv_std = (self.running_var + self.eps).rsqrt()
        n_unsqueeze = x.dim() - 2
        running_mean = running_mean.reshape(-1, *[1] * n_unsqueeze)
        running_inv_std = running_inv_std.reshape(-1, *[1] * n_unsqueeze)
        running_mean = self.running_mean_quant(running_mean)
        running_inv_std = self.running_var_quant(running_inv_std)

        x = self.inv_std_mul(self.mean_sub(x, running_mean), running_inv_std)

        if self.affine:
            gamma = self.gamma
            beta = self.beta
            gamma = gamma.reshape(-1, *[1] * n_unsqueeze)
            beta = beta.reshape(-1, *[1] * n_unsqueeze)
            gamma = self.gamma_quant(gamma).to(x.device)
            beta = self.beta_quant(beta).to(x.device)
            x = self.beta_add(self.gamma_mul(x, gamma), beta)
        return x

    @classmethod
    def _from_float(
        cls,
        parent,
        bw_conf,
        interpolate,
        observer=quantizers.DEFAULT_OBSERVERS["default"],
        **observer_kwargs,
    ):
        observer = partial(observer, **observer_kwargs)
        try:
            eps = parent.eps
        except:
            eps = 1e-5
        try:
            momentum = parent.momentum
        except:
            momentum = 0.1

        layer = cls(
            num_features=parent.num_features,
            bitwidth=bw_conf.activations,
            eps=eps,
            momentum=momentum,
            affine=parent.affine,
            track_running_stats=parent.track_running_stats,
            observer=observer,
        )
        layer.running_mean.data[:] = parent.running_mean.data
        layer.running_var.data[:] = parent.running_var.data
        if parent.affine:
            layer.gamma.data[:] = parent.weight.data
            layer.beta.data[:] = parent.bias.data
        return layer
