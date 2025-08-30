import torch
from torch import nn, Tensor
from .sequencer import Sequencer
import torch.nn.functional as F
import math
from typing import List, Tuple
from .atomics import Gt0


class ActSparsifier(nn.Module):
    r"""
    Base class for activation sparsifier layers. This enables fmot activation sparsity utils
    to register necessary activation-related metrics.

    Attributes:
         act_zeros (Tensor)
    """

    def __init__(self):
        super().__init__()
        self.act_zeros = None
        self.act_pen = None
        self.act_numel = None


class ReLU(ActSparsifier):
    r"""
    ReLU layer as an activation sparsifier.

    """

    def __init__(self, inplace: bool = False):
        super().__init__()
        self.inplace = inplace

    def forward(self, input: Tensor) -> Tensor:
        return F.relu(input, inplace=self.inplace)


class ThresholdSparsifier(ActSparsifier):
    r"""
    Sparsify activations below a learned element-wise threshold.

    .. math::

        y = \text{ReLU}(x*\gamma - \theta)

    Args:
        size (int): Input activation feature size

    Shapes:
        - :attr:`input`: :math:`(*, \text{size})` where :math:`*` denotes
          any number of tensor dimensions
        - :attr:`output`: :math:`(*, \text{size})`; same shape as input
    """

    def __init__(self, size):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(size))
        self.theta = nn.Parameter(torch.zeros(size))

    def forward(self, x):
        return torch.relu(self.gamma * x - self.theta)


class LayerNormThresholdSparsifier(ActSparsifier):
    r"""
    Normalize, then sparsify activations below a learned threshold.

    A layernorm is applied to the feature dimension before sparsifying activations
    through a ReLU.

    .. math::

        &\tilde{x} = \frac{x-\mathrm{E}[x]}{\sqrt{\mathrm{Var}[x]+\epsilon}} \\
        &y = \text{ReLU}\Big(\tilde{x}*\gamma-\theta\Big)

    Args:
        size (int): Input activation feature size
        eps (float, optional): A value added to layernorm denominator for numerical stability,
            default is :attr:`1e-05`.

    Shapes:
        - :attr:`input`: :math:`(*, \text{size})` where :math:`*` denotes
          any number of tensor dimensions
        - :attr:`output`: :math:`(*, \text{size})`; same shape as input

    """

    def __init__(self, size, eps=1e-05):
        super().__init__()
        self.normalized_shape = [size]
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(size))
        self.theta = nn.Parameter(torch.zeros(size))

    def forward(self, x):
        return torch.relu(
            F.layer_norm(
                x,
                normalized_shape=self.normalized_shape,
                weight=self.gamma,
                bias=-self.theta,
                eps=self.eps,
            )
        )


class AdaptiveSparsifierCell(ActSparsifier):
    def __init__(self, size, tau_min=3.0, tau_max=6.0):
        super().__init__()
        self.size = size
        self.gamma = nn.Parameter(torch.ones(size))
        self.theta_0 = nn.Parameter(torch.zeros(size))

        # Exponential smoothing coefficient chosen such that
        # time-constant is uniformly distributed between bounds
        a_min = math.exp(-1 / tau_min)
        a_max = math.exp(-1 / tau_max)
        alpha = torch.rand(size) * (a_max - a_min) + a_min
        self.alpha = nn.Parameter(alpha)
        self.omega = nn.Parameter(torch.ones(size))
        self.gt0 = Gt0(pseudo_derivative=True)

    def forward(self, x_t: Tensor, mov_avg: Tensor) -> Tuple[Tensor, Tensor]:
        y_t = torch.relu(self.gamma * x_t - self.theta_0 - mov_avg)
        new_mov_avg = self.alpha * mov_avg + self.omega * self.gt0(y_t)
        return y_t, new_mov_avg


class AdaptiveSparsifierCell_A(AdaptiveSparsifierCell):
    def __init__(self, size, tau_min=3.0, tau_max=6.0):
        super().__init__(size, tau_min, tau_max)
        self.size = size
        self.gamma = nn.Parameter(torch.ones(size))
        self.theta_0 = nn.Parameter(torch.zeros(size))

        # Exponential smoothing coefficient chosen such that
        # time-constant is uniformly distributed between bounds
        a_min = math.exp(-1 / tau_min)
        a_max = math.exp(-1 / tau_max)
        alpha = torch.rand(size) * (a_max - a_min) + a_min
        self.alpha = nn.Parameter(alpha)

    def forward(self, x_t: Tensor, mov_avg: Tensor) -> Tuple[Tensor, Tensor]:
        y_t = torch.relu(self.gamma * x_t - self.theta_0 - mov_avg)
        new_mov_avg = self.alpha * mov_avg + (1 - self.alpha) * y_t
        return y_t, new_mov_avg


class AdaptiveSparsifierCell_B(AdaptiveSparsifierCell_A):
    def forward(self, x_t: Tensor, mov_avg: Tensor) -> Tuple[Tensor, Tensor]:
        y_t = torch.relu(self.gamma * x_t - self.theta_0 - mov_avg)
        new_mov_avg = self.alpha * mov_avg + (1 - self.alpha) * torch.sigmoid(y_t)
        return y_t, new_mov_avg


class AdaptiveSparsifier(Sequencer):
    r"""Sparsify activations below a time-varying threshold.

    The threshold changes in time via an exponential moving average of the
    sparsified outputs.

    .. math::

        &y[t] = \text{ReLU}(x[t]*\gamma - \theta - \phi[t-1]) \\
        &\phi[t] = \alpha*\phi[t-1] + \omega*\{ y[t] > 0 \}

    The adaptive threshold :math:`\theta + \phi[t]` is driven by impulses of size
    :math:`\omega` for each nonzero activation that the layer outputs. The threshold
    relaxes back towards :math:`\theta` with a time constant
    :math:`\tau = \frac{-1}{\ln{\alpha}}`. :math:`\alpha` is initialized so that
    time constants for each feature dimension are
    uniformly distributed between :attr:`tau_min` and :attr:`tau_max`.

    Parameters:
        size (int): Input feature size
        tau_min (float): Minimum value for exponential moving average time constant.
        tau_max (float): Maximum value for exponential moving average time constant.
        batch_first (bool): If :attr:`True`, then the input and output tensors are provided as
            (batch, seq, feature). Default: :attr:`False`
    """

    def __init__(self, size, tau_min=3.0, tau_max=6.0, batch_first=False):
        super().__init__(state_shapes=[[size]], batch_first=batch_first)
        self.cell = AdaptiveSparsifierCell(size, tau_min, tau_max)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        (mov_avg,) = state
        y_t, new_mov_avg = self.cell(x_t, mov_avg)
        return y_t, [new_mov_avg]


class AdaptiveLayerNormSparsifierCell(ActSparsifier):
    def __init__(self, size, tau_min=3.0, tau_max=6.0, eps=1e-05):
        super().__init__()
        self.size = size
        self.gamma = nn.Parameter(torch.ones(size))
        self.theta_0 = nn.Parameter(torch.zeros(size))
        self.eps = eps

        # Exponential smoothing coefficient chosen such that
        # time-constant is uniformly distributed between bounds
        a_min = math.exp(-1 / tau_min)
        a_max = math.exp(-1 / tau_max)
        alpha = torch.rand(size) * (a_max - a_min) + a_min
        self.alpha = nn.Parameter(alpha)
        self.gt0 = Gt0()

    def forward(self, x_t: Tensor, mov_avg: Tensor) -> Tuple[Tensor, Tensor]:
        x_normed = F.layer_norm(
            x,
            normalized_shape=self.normalized_shape,
            weight=self.gamma,
            bias=-self.theta,
            eps=self.eps,
        )
        y_t = torch.relu(x_normed - mov_avg)
        new_mov_avg = self.alpha * mov_avg + (1 - self.alpha) * self.gt0(y_t)
        return y_t, new_mov_avg


class AdaptiveLayerNormSparsifier(Sequencer):
    r"""
    Sparsify with an adaptive threshold and layernorm.

    Inputs are normalized via a layernorm. Then, they are compared to an
    adaptive threshold before a relu activation. The adaptive
    threshold changes in time via an exponential moving average of the
    sparsified outputs.

    .. math::

        &\theta[0] = \theta_o \\
        &\tilde{x[t]} = \frac{x[t]-\mathrm{E}[x[t]]}{\sqrt{\mathrm{Var}[x[t]]+\epsilon}} \\
        &y[t] = \text{ReLU}(\tilde{x[t]}*\gamma - \theta[t-1]) \\
        &\theta[t] = \theta_o + \alpha*(\theta[t-1] - \theta_0) + (1-\alpha)*y[t]

    Parameters:
        size (int): Input feature size
        tau_min (float): Minimum value for exponential moving average time constant.
        tau_max (float): Maximum value for exponential moving average time constant.
        eps (float): A value added to layernorm denominator for numerical stability,
            Default: :attr:`1e-05`.
        batch_first (bool): If :attr:`True`, then the input and output tensors are provided as
            (batch, seq, feature). Default: :attr:`False`
    """

    def __init__(self, size, tau_min=3.0, tau_max=6.0, eps=1e-05, batch_first=False):
        super().__init__(state_shapes=[[size]], batch_first=batch_first)
        self.cell = AdaptiveLayerNormSparsifierCell(size, tau_min, tau_max, eps)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        (mov_avg,) = state
        y_t, new_mov_avg = self.cell(x_t, mov_avg)
        return y_t, [new_mov_avg]
