import torch
from torch import nn, Tensor
from . import atomics
from .super_structures import SuperStructure
from typing import Optional, List, Tuple
import math
import numpy as np
import torch.nn.utils.prune as prune
import torch.nn.functional as F


class VISub(nn.Module):
    def __init__(self, imm):
        super().__init__()
        self.imm = -imm

    def forward(self, x):
        return x + self.imm


class F_Linear(nn.Module):
    def __init__(self):
        super().__init__()
        self.matmul = atomics.AddMM()

    def forward(self, x, weight, bias):
        weight = weight.t()
        return self.matmul(bias, x, weight)


class F_Linear_nb(nn.Module):
    def __init__(self):
        super().__init__()
        self.transpose = atomics.Transpose()
        self.matmul = atomics.Matmul()

    def forward(self, x, weight):
        weight = self.transpose(weight)
        return self.matmul(x, weight)


class Var(nn.Module):
    def __init__(self, dim=0, keepdim=False, unbiased=True):
        super().__init__()
        self.mean_x = atomics.Mean(dim, keepdim, biased=True)
        self.mean_x2 = atomics.Mean(dim, keepdim, biased=not unbiased)

    def forward(self, x):
        mu = self.mean_x(x)
        xp = x - mu
        return self.mean_x2(xp * xp)


class Std(nn.Module):
    def __init__(self, dim=0, keepdim=False, unbiased=True):
        super().__init__()
        self.dim = dim
        self.keepdim = keepdim
        self.unbiased = unbiased

    def forward(self, x):
        var = torch.var(x, dim=self.dim, keepdim=self.keepdim, unbiased=self.unbiased)
        return torch.sqrt(var)


class VarMean(nn.Module):
    def __init__(self, dim=0, keepdim=False, unbiased=True):
        super().__init__()
        self.mean_x = atomics.Mean(dim, keepdim, biased=True)
        self.mean_x2 = atomics.Mean(dim, keepdim, biased=not unbiased)

    def forward(self, x):
        mu = self.mean_x(x)
        xp = x - mu
        return self.mean_x2(xp * xp), mu


class StdMean(nn.Module):
    def __init__(self, dim=0, keepdim=False, unbiased=True):
        super().__init__()
        self.mean_x = atomics.Mean(dim, keepdim, biased=True)
        self.mean_x2 = atomics.Mean(dim, keepdim, biased=not unbiased)

    def forward(self, x):
        mu = self.mean_x(x)
        xp = x - mu
        return torch.sqrt(self.mean_x2(xp * xp)), mu


class RSqrtPlusEps(nn.Module):
    def __init__(self, eps):
        super().__init__()
        self.eps = eps

    def forward(self, x):
        return torch.rsqrt(x + self.eps)


class F_LayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps):
        super().__init__()
        dim = [-i for i in range(1, len(normalized_shape) + 1)]
        self.var_mean = VarMean(dim=dim, keepdim=True, unbiased=False)
        self.rsqrt = RSqrtPlusEps(eps)

    def forward(self, x, weight, bias):
        var, mu = self.var_mean(x)
        return (x - mu) * self.rsqrt(var) * weight + bias


class SquareApply(nn.Module):
    def forward(self, x, y):
        """
        Args:
            x (Tensor): tensor to square
            y (Tensor): multiply this by the square

        Returns:
            x2: square of x
            y*x2
        """
        x2 = x * x
        y = y * x2
        return x2, y


class SquarePass(nn.Module):
    """
    Args:
        x (Tensor): tensor to square
        y (Tensor): leave this alone

    Returns:
            x2: square of x
            y
    """

    def forward(self, x, y):
        x2 = x * x
        return x2, y


def decompose_to_pow2(x):
    assert x > 0
    assert math.floor(x) == x

    decomps = []
    while x > 0:
        d = 2 ** math.floor(math.log2(x))
        decomps.append(d)
        x = x - d
    return decomps[::-1]


class PowDecompPosInt(nn.Module):
    """
    Decompose x**power into iterative squares
    """

    def __init__(self, power):
        super().__init__()
        decomposition = decompose_to_pow2(power)
        Nsq = int(math.log2(np.max(decomposition)))
        if 1 in decomposition:
            self.start = atomics.Identity()
        else:
            self.start = atomics.OnesLike()
        self.squarers = nn.ModuleList()
        for i in range(Nsq):
            if 2 ** (i + 1) in decomposition:
                self.squarers.append(SquareApply())
            else:
                self.squarers.append(SquarePass())

    def forward(self, x):
        y = self.start(x)
        for l in self.squarers:
            x, y = l(x, y)
        return y


class PowDecompNegInt(nn.Module):
    def __init__(self, power):
        super().__init__()
        self.pospow = PowDecompPosInt(-power)

    def forward(self, x):
        return self.pospow(x.reciprocal())


class F_Softmax(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.sum = atomics.Sum(dim=dim, keepdim=True)

    def forward(self, x):
        x_exp = x.exp()
        return x_exp / self.sum(x_exp)


##### HARD NONLINEARITIES ######


class Abs(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return torch.relu(x) + torch.relu(-x)


class ClampAB(nn.Module):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b

    def forward(self, x):
        return self.a + torch.relu(x - self.a) - torch.relu(x - self.b)


class ClampA(nn.Module):
    def __init__(self, a):
        super().__init__()
        self.a = a

    def forward(self, x):
        return self.a + torch.relu(x - self.a)


class ClampB(nn.Module):
    def __init__(self, b):
        super().__init__()
        self.b = b

    def forward(self, x):
        return x + torch.relu(x - self.b)


class ConstantLike(nn.Module):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def forward(self, x):
        return self.value * torch.ones_like(x)


class HardSigmoid(nn.Module):
    def forward(self, x):
        return torch.clamp(x / 6 + 0.5, 0, 1)


class HardTanh(nn.Module):
    def __init__(self, min_val=-1, max_val=1):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val

    def forward(self, x):
        return torch.clamp(x, self.min_val, self.max_val)


class LeakyReLU(nn.Module):
    def __init__(self, negative_slope=0.01):
        super().__init__()
        self.negative_slope = negative_slope

    def forward(self, x):
        return torch.relu(x) - self.negative_slope * torch.relu(-x)


class Dropout(nn.Module):
    def __init__(self, p, training, inplace):
        super().__init__()
        self.p = p
        self.training = training
        self.inplace = inplace

    def forward(self, x):
        if self.training:
            mask = torch.bernoulli(torch.zeros(x.shape) + self.p)
            return mask * x
        else:
            return x


class DepthWiseConvSummer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, bias):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.bias = bias

        self.K = int(out_channels / in_channels)
        self.linlist_len = self.K * self.kernel_size
        if self.bias:
            # we keep bias for each lin at the begeinning of a new filter set only
            self.has_bias = [
                not (i % self.kernel_size) for i in range(self.linlist_len)
            ]
        else:
            self.has_bias = [False for _ in range(self.linlist_len)]

        self.lin_list = nn.ModuleList(
            nn.Linear(1, self.in_channels, bias=self.has_bias[i])
            for i in range(self.linlist_len)
        )

    @torch.jit.ignore
    def forward(self, x_list: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        output = []
        for i, lin in enumerate(self.lin_list):
            if i % self.kernel_size == 0:
                y = x_list[i % self.kernel_size] * lin.weight.squeeze()
                if self.bias:
                    y += lin.bias
            else:
                y += x_list[i % self.kernel_size] * lin.weight.squeeze()
            if (i + 1) % self.kernel_size == 0:
                output.append(y)

        return y, output


class _BlockDiagMasking(prune.BasePruningMethod):
    def __init__(self, num_blocks):
        """Init class

        @param amount (float): percent of the model to prune out
        @param pencil_size (int): size of the pencils
        @param row_major (bool): true if we want row-pencil sparsity
        """
        super().__init__()
        self.num_blocks = num_blocks

    def compute_mask(self, tensor, default_mask):
        # Check that input tensor shape is compatible
        tensor = tensor.clone()
        assert tensor.dim() == 2
        nrows, ncols = tensor.shape
        assert (
            nrows % self.num_blocks == 0
        ), "Number of blocks needs to divide the tensor size"
        assert (
            ncols % self.num_blocks == 0
        ), "Number of blocks needs to divide the tensor size"

        mask = torch.zeros_like(tensor, dtype=bool)
        brow = nrows // self.num_blocks
        bcol = ncols // self.num_blocks

        for k in range(self.num_blocks):
            mask[k * brow : (k + 1) * brow, k * bcol : (k + 1) * bcol] = 1

        return mask

    @classmethod
    def apply(cls, module, name, num_blocks):
        return super(_BlockDiagMasking, cls).apply(module, name, num_blocks=num_blocks)


class BlockDiagLinear(nn.Module):
    def __init__(self, in_features, out_features, num_blocks, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_blocks = num_blocks
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter("bias", None)
        self.reset_parameters()
        _BlockDiagMasking.apply(self, "weight", num_blocks=self.num_blocks)
        self.weight_orig.data *= self.weight_mask

    def reset_parameters(self):
        fan_in, fan_out = self.weight.shape
        bound = math.sqrt(6 * self.num_blocks / (fan_in + fan_out))
        nn.init.uniform_(self.weight, -bound, bound)
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, x):
        return F.linear(x, self.weight, bias=self.bias)


class LogMM(nn.Module):
    def forward(self, x, matrix):
        x = torch.matmul(x, matrix)
        x = torch.log(x)  # + self.epsilon)
        return x


class LogEpsMM(nn.Module):
    def __init__(self, epsilon):
        super().__init__()
        self.epsilon = epsilon

    def forward(self, x, matrix):
        x = torch.matmul(x, matrix)
        return torch.log(x + self.epsilon)


class TuningEpsilon(nn.Module):
    """Automatically tunes a small +epsilon factor so that it doesn't round to zero
    after quantization. The value epsilon will be tuned as `eps * running_max`, where
    `max_abs` is a running maximum input seen by the layer.

    Arguments:
        eps (float): ratio between max_abs and epsilon. Must be >= 2**-14
        alpha (float): exponential smoothing coefficient, for updating `running_max`
    """

    def __init__(self, eps=2**-14, alpha=0.99):
        super().__init__()

        # 2**-14 is the smallest allowed epsilon (below this will lead to truncation)
        if eps < 2**-14:
            raise ValueError(
                f"Epsilon {eps} < 2**-14, will be truncated to zero when quantized"
            )

        self.register_buffer("running_max", torch.tensor(0))
        self.alpha = alpha
        self.eps = eps

    @torch.jit.ignore()
    def epsilon(self):
        return self.running_max * self.eps

    @torch.jit.ignore()
    @torch.no_grad()
    def update(self, x):
        """Updates the running max during training"""
        if self.training:
            xmax = torch.max(x).detach()
            if self.running_max == 0:
                self.running_max = xmax
            else:
                self.running_max = (
                    self.alpha * self.running_max + (1 - self.alpha) * xmax
                )

    def forward(self, x):
        self.update(x)
        return x + self.epsilon()


class Softmax(nn.Module):
    def __init__(self, size: int, dim=-1):
        super().__init__()
        self.dim = dim
        self.sum = atomics.Sum(dim)
        self.broad = atomics.Expand(size, dim)

    def forward(self, x):
        e_x = torch.exp(x)
        den = self.sum(e_x)
        norm = 1 / den
        norm = self.broad(norm)
        return e_x * norm


class Hardswish(nn.Module):
    def forward(self, x):
        xc = torch.clamp(x, -3, 3)
        mc = xc * (xc + 3) / 6
        y = mc + (x - 3).relu()
        return y


class PReLU(SuperStructure):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()
        self.transpose_in = None
        self.transpose_out = None
        self.neg = atomics.Neg()
        self.add_1 = atomics.VIAdd(1)
        self.mul1 = atomics.VVMul()
        self.mul2 = atomics.VVMul()
        self.add = atomics.VVAdd()

    def forward(self, input: Tensor, weight: Tensor) -> Tensor:
        if input.ndim > 2 and self.transpose_in is None:
            self.transpose_in = atomics.FTranspose(1, input.ndim - 1)
            self.transpose_out = atomics.FTranspose(1, input.ndim - 1)

        if self.transpose_in is not None:
            input = self.transpose_in(input)

        # ya = weight * input
        ya = self.mul1(weight, input)
        # w_minus = 1 - weight
        w_minus = self.add_1(self.neg(weight))
        # yb = w_minus * relu(input)
        yb = self.mul2(w_minus, self.relu(input))
        # output = ya + yb
        output = self.add(ya, yb)

        if self.transpose_out is not None:
            output = self.transpose_out(output)

        return output


class GLU(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        a, b = torch.chunk(x, 2, self.dim)
        return a * torch.sigmoid(b)

    @classmethod
    def _from_torchmodule(cls, parent: torch.nn.GLU, *args, **kwargs):
        return cls(dim=parent.dim)
