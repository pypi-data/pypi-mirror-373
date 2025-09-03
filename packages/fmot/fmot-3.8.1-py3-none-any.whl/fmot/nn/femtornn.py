from typing import List, Tuple
import torch
from torch import nn, Tensor
from . import Sequencer, BlockDiagLinear
from .sparsifiers import (
    ThresholdSparsifier,
    LayerNormThresholdSparsifier,
    AdaptiveSparsifierCell,
    AdaptiveLayerNormSparsifierCell,
)
from .sparsifiers import AdaptiveSparsifierCell_A, AdaptiveSparsifierCell_B


SPARSIFIERS = {
    "threshold": ThresholdSparsifier,
    "layer_norm_threshold": LayerNormThresholdSparsifier,
    "adaptive": AdaptiveSparsifierCell,
    "layer_norm_adaptive": AdaptiveLayerNormSparsifierCell,
    "adaptive_a": AdaptiveSparsifierCell_A,
    "adaptive_b": AdaptiveSparsifierCell_B,
}


def get_sparsifier(key, hidden_size, **kwargs):
    sp_class = SPARSIFIERS[key]
    sp = sp_class(size=hidden_size, **kwargs)
    return sp


####################
# GRU VARIANTS
####################


class SnapshotGRU(Sequencer):
    r"""
    A GRU with a sparsified hidden state.

    For each element :math:`x_t` in the input sequence, the layer computes the
    following function:

    .. math::

        &r_t = \sigma(W_{ir} x_t + b_{ir} + W_{ar} a_{(t-1)} + b_{ar}) \\
        &z_t = \sigma(W_{iz} x_t + b_{iz} + W_{az} a_{(t-1)} + b_{az}) \\
        &n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{an} a_{(t-1)}+ b_{an})) \\
        &h_t = (1 - z_t) * n_t + z_t * h_{(t-1)} \\
        &a_t = \text{ReLU}(\gamma * h_t - \theta)

    Here, :math:`h_{(t-1)}` and :math:`a_{(t-1)}` are the dense and sparse hidden
    states at time :math:`t-1`, respectively.

    The SnapshotGRU modifies the standard GRU layer by sparsifying the hidden state
    :math:`h_t` with a :class:`fmot.nn.ThresholdSparsifier`, producing the sparse
    hidden state :math:`a_t`. The sparsified state :math:`a_{(t-1)}` replaces
    :math:`h_{(t-1)}` in matrix-vector products in order to take advantage
    of sparse matrix-vector hardware.

    Args:
        input_size (int): Number of features in input :math:`x`
        hidden_size (int): Number of features in hidden states :math:`a` and :math:`h`
        batch_first (bool): If :attr:`True`, then input and output tensors are expected
            as :math:`(batch, seq, feature)`. Default: :attr:`False`
    """

    def __init__(self, input_size, hidden_size, batch_first=False):
        state_shapes = [[hidden_size], [hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.linear_ih = nn.Linear(self.input_size, 3 * self.hidden_size)
        self.linear_hh = nn.Linear(self.hidden_size, 3 * self.hidden_size)
        self.sparsifier = get_sparsifier("threshold", hidden_size)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, a_t = state

        stacked_layer_i = self.linear_ih(x_t)
        stacked_layer_a = self.linear_hh(a_t)

        # Dim 0 = Batch Dim
        r_t, z_t, n_t = stacked_layer_i.chunk(3, 1)
        r_t_a, z_t_a, n_t_a = stacked_layer_a.chunk(3, 1)

        r_t = torch.sigmoid(r_t + r_t_a)
        z_t = torch.sigmoid(z_t + z_t_a)
        n_t = torch.tanh(n_t + r_t * n_t_a)

        h_t = (1 - z_t) * n_t + z_t * h_t

        a_t = self.sparsifier(h_t)

        return a_t, [h_t, a_t]


class AdaptiveSnapshotGRU(Sequencer):
    r"""
    A GRU with an adaptively sparsified hidden state.

    For each element :math:`x_t` in the input sequence, the layer computes the
    following function:

    .. math::

        &r_t = \sigma(W_{ir} x_t + b_{ir} + W_{ar} a_{(t-1)} + b_{ar}) \\
        &z_t = \sigma(W_{iz} x_t + b_{iz} + W_{az} a_{(t-1)} + b_{az}) \\
        &n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{an} a_{(t-1)}+ b_{an})) \\
        &h_t = (1 - z_t) * n_t + z_t * h_{(t-1)} \\
        &a_t = \text{ReLU}(h_t*\gamma - \theta - \phi_{(t-1)}) \\
        &\phi_t = \alpha*\phi_{(t-1)} + \omega*\{ h_t > 0 \}

    Here, :math:`h_{(t-1)}` and :math:`a_{(t-1)}` are the dense and sparse hidden
    states at time :math:`t-1`, respectively. :math:`\phi{(t-1)}` is the deviation
    of the sparsifier's adaptive threshold from the baseline :math:`\theta`.

    The AdaptiveSnapshotGRU modifies the standard GRU layer by sparsifying the hidden state
    :math:`h_t` with a :class:`fmot.nn.AdaptiveSparsifier`, producing the sparse
    hidden state :math:`a_t`. The :math:`a_{(t-1)}` replaces :math:`h_{(t-1)}` in
    matrix-vector products in order to take advantage of sparse matrix-vector hardware.

    Args:
        input_size (int): Number of features in input :math:`x`
        hidden_size (int): Number of features in hidden states :math:`a` and :math:`h`
        batch_first (bool): If :attr:`True`, then input and output tensors are expected
            as :math:`(batch, seq, feature)`. Default: :attr:`False`
        tau_min (float): Minimum relaxation time-constant for sparsifier's adaptive threshold,
            in number of time-steps. Default: :attr:`3`.
        tau_max (float): Maximum relaxation time-constant for sparsifier's adaptive threshold,
            in number of time-steps. Default: :attr:`3`.
    """

    def __init__(
        self, input_size, hidden_size, batch_first=False, tau_min=3.0, tau_max=6.0
    ):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.linear_ih = nn.Linear(self.input_size, 3 * self.hidden_size)
        self.linear_hh = nn.Linear(self.hidden_size, 3 * self.hidden_size)
        self.sparsifier = get_sparsifier(
            "adaptive", hidden_size, tau_min=tau_min, tau_max=tau_max
        )

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, a_t, mov_avg_t = state

        stacked_layer_i = self.linear_ih(x_t)
        stacked_layer_a = self.linear_hh(a_t)

        # Dim 0 = Batch Dim
        r_t, z_t, n_t = stacked_layer_i.chunk(3, 1)
        r_t_a, z_t_a, n_t_a = stacked_layer_a.chunk(3, 1)

        r_t = torch.sigmoid(r_t + r_t_a)
        z_t = torch.sigmoid(z_t + z_t_a)
        n_t = torch.tanh(n_t + r_t * n_t_a)

        h_t = (1 - z_t) * n_t + z_t * h_t
        a_t, mov_avg_t = self.sparsifier(h_t, mov_avg_t)

        return a_t, [h_t, a_t, mov_avg_t]


class FemtoGRU(Sequencer):
    r"""
    A GRU with a sparsified hidden state and dense local communication.

    For each element :math:`x_t` in the input sequence, the layer computes the
    following function:

    .. math::

        &r_t = \sigma(W_{ir} x_t + b_{ir} + W_{ar} a_{(t-1)} + b_{ar} + D_{hr} h_{t-1}) \\
        &z_t = \sigma(W_{iz} x_t + b_{iz} + W_{az} a_{(t-1)} + b_{az} + D_{hz} h_{t-1}) \\
        &n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{an} a_{(t-1)}+ b_{an} + D_{hn} h_{t-1})) \\
        &h_t = (1 - z_t) * n_t + z_t * h_{(t-1)} \\
        &a_t = \text{ReLU}(\gamma * h_t - \theta)

    Here, :math:`h_{(t-1)}` and :math:`a_{(t-1)}` are the dense and sparse hidden
    states at time :math:`t-1`, respectively.

    The matrices :math:`D_{hr}`, :math:`D_{hz}`, and :math:`D_{hn}` are
    block-diagonal, thus restricting the scope of the dense matrix-vector products.

    The FemtoGRU modifies the standard GRU layer by sparsifying the hidden state
    :math:`h_t` with a :class:`fmot.nn.ThresholdSparsifier`, producing the sparse
    hidden state :math:`a_t`. :math:`a_{(t-1)}` replaces :math:`h_{(t-1)}` in
    matrix-vector products in order to take advantage of sparse matrix-vector hardware.

    Args:
        input_size (int): Number of features in input :math:`x`
        hidden_size (int): Number of features in hidden states :math:`a` and :math:`h`
        num_blocks (int): Number of matrix blocks in block-diagonal matrices :math:`D_{hr}`,
            :math:`D_{hz}`, and :math:`D_{hn}`. Each block will be of shape
            :math:`(\text{hidden_size}/\text{num_blocks}, \text{hidden_size}/\text{num_blocks})`,
            resulting in a total of :math:`\text{hidden_size}^2/\text{num_blocks}` nonzero matrix
            elements (compared to :math:`\text{hidden_size}^2` for completely dense matrices).
        batch_first (bool): If :attr:`True`, then input and output tensors are expected
            as :math:`(batch, seq, feature)`. Default: :attr:`False`
    """

    def __init__(
        self, input_size, hidden_size, num_blocks, batch_first=False, bias=True
    ):
        state_shapes = [[hidden_size], [hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_blocks = num_blocks
        self.bias = bias
        self.linear_ih = nn.Linear(self.input_size, 3 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 3 * self.hidden_size, self.bias)
        self.block_r = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_z = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_n = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.sparsifier = get_sparsifier("threshold", hidden_size)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, a_t = state

        stacked_layer_i = self.linear_ih(x_t)
        stacked_layer_a = self.linear_hh(a_t)
        r_t_l, z_t_l, n_t_l = self.block_r(h_t), self.block_z(h_t), self.block_n(h_t)

        # Dim 0 = Batch Dim
        r_t, z_t, n_t = stacked_layer_i.chunk(3, 1)
        r_t_a, z_t_a, n_t_a = stacked_layer_a.chunk(3, 1)

        r_t = torch.sigmoid(r_t + r_t_a + n_t_l)
        z_t = torch.sigmoid(z_t + z_t_a + n_t_l)
        n_t = torch.tanh(n_t + r_t * (n_t_a + n_t_l))

        h_t = (1 - z_t) * n_t + z_t * h_t

        a_t = self.sparsifier(h_t)

        return a_t, [h_t, a_t]


class AdaptiveFemtoGRU(Sequencer):
    r"""
    A GRU with an adaptively sparsified hidden state and dense local communication.

    For each element :math:`x_t` in the input sequence, the layer computes the
    following function:

    .. math::

        &r_t = \sigma(W_{ir} x_t + b_{ir} + W_{ar} a_{(t-1)} + b_{ar} + D_{hr} h_{t-1}) \\
        &z_t = \sigma(W_{iz} x_t + b_{iz} + W_{az} a_{(t-1)} + b_{az} + D_{hz} h_{t-1}) \\
        &n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{an} a_{(t-1)}+ b_{an} + D_{hn} h_{t-1})) \\
        &h_t = (1 - z_t) * n_t + z_t * h_{(t-1)} \\
        &a_t = \text{ReLU}(h_t*\gamma - \theta - \phi_{(t-1)}) \\
        &\phi_t = \alpha*\phi_{(t-1)} + \omega*\{ h_t > 0 \}

    Here, :math:`h_{(t-1)}` and :math:`a_{(t-1)}` are the dense and sparse hidden
    states at time :math:`t-1`, respectively. :math:`\phi{(t-1)}` is the deviation
    of the sparsifier's adaptive threshold from the baseline :math:`\theta`.

    The matrices :math:`D_{hr}`, :math:`D_{hz}`, and :math:`D_{hn}` are
    block-diagonal, thus restricting the scope of the dense matrix-vector products.

    The FemtoGRU modifies the standard GRU layer by sparsifying the hidden state
    :math:`h_t` with a :class:`fmot.nn.ThresholdSparsifier`, producing the sparse
    hidden state :math:`a_t`. :math:`a_{(t-1)}` replaces :math:`h_{(t-1)}` in
    matrix-vector products in order to take advantage of sparse matrix-vector hardware.

    Args:
        input_size (int): Number of features in input :math:`x`
        hidden_size (int): Number of features in hidden states :math:`a` and :math:`h`
        num_blocks (int): Number of matrix blocks in block-diagonal matrices :math:`D_{hr}`,
            :math:`D_{hz}`, and :math:`D_{hn}`. Each block will be of shape
            :math:`(\text{hidden_size}/\text{num_blocks}, \text{hidden_size}/\text{num_blocks})`,
            resulting in a total of :math:`\text{hidden_size}^2/\text{num_blocks}` nonzero matrix
            elements (compared to :math:`\text{hidden_size}^2` for completely dense matrices).
        batch_first (bool): If :attr:`True`, then input and output tensors are expected
            as :math:`(batch, seq, feature)`. Default: :attr:`False`
        tau_min (float): Minimum relaxation time-constant for sparsifier's adaptive threshold,
            in number of time-steps. Default: :attr:`3`.
        tau_max (float): Maximum relaxation time-constant for sparsifier's adaptive threshold,
            in number of time-steps. Default: :attr:`6`.
    """

    def __init__(
        self,
        input_size,
        hidden_size,
        num_blocks,
        batch_first=False,
        bias=True,
        tau_min=3.0,
        tau_max=6.0,
    ):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_blocks = num_blocks
        self.bias = bias
        self.linear_ih = nn.Linear(self.input_size, 3 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 3 * self.hidden_size, self.bias)
        self.block_r = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_z = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_n = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.sparsifier = get_sparsifier(
            "adaptive", hidden_size, tau_min=tau_min, tau_max=tau_max
        )

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, a_t, mov_avg_t = state

        stacked_layer_i = self.linear_ih(x_t)
        stacked_layer_a = self.linear_hh(a_t)
        r_t_l, z_t_l, n_t_l = self.block_r(h_t), self.block_z(h_t), self.block_n(h_t)

        # Dim 0 = Batch Dim
        r_t, z_t, n_t = stacked_layer_i.chunk(3, 1)
        r_t_a, z_t_a, n_t_a = stacked_layer_a.chunk(3, 1)

        r_t = torch.sigmoid(r_t + r_t_a + n_t_l)
        z_t = torch.sigmoid(z_t + z_t_a + n_t_l)
        n_t = torch.tanh(n_t + r_t * (n_t_a + n_t_l))

        h_t = (1 - z_t) * n_t + z_t * h_t

        a_t, mov_avg_t = self.sparsifier(h_t, mov_avg_t)

        return a_t, [h_t, a_t, mov_avg_t]


class AdaptiveFemtoGRU_A(AdaptiveFemtoGRU):
    def __init__(
        self,
        input_size,
        hidden_size,
        num_blocks,
        batch_first=False,
        bias=True,
        tau_min=3.0,
        tau_max=6.0,
    ):
        super().__init__(
            input_size,
            hidden_size,
            num_blocks,
            batch_first=False,
            bias=True,
            tau_min=3.0,
            tau_max=6.0,
        )
        self.sparsifier = get_sparsifier(
            "adaptive_a", hidden_size, tau_min=tau_min, tau_max=tau_max
        )


class AdaptiveFemtoGRU_B(AdaptiveFemtoGRU):
    def __init__(
        self,
        input_size,
        hidden_size,
        num_blocks,
        batch_first=False,
        bias=True,
        tau_min=3.0,
        tau_max=6.0,
    ):
        super().__init__(
            input_size,
            hidden_size,
            num_blocks,
            batch_first=False,
            bias=True,
            tau_min=3.0,
            tau_max=6.0,
        )
        self.sparsifier = get_sparsifier(
            "adaptive_b", hidden_size, tau_min=tau_min, tau_max=tau_max
        )


####################
# LSTM VARIANTS
####################


class SnapshotLSTM(Sequencer):
    def __init__(self, input_size, hidden_size, batch_first=False, bias=True):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first

        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 4 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 4 * self.hidden_size, self.bias)
        self.sparsifier = get_sparsifier("threshold", self.hidden_size)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t, a_t = state
        stacked_layer = self.linear_ih(x_t) + self.linear_hh(a_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t)
        f_t = torch.sigmoid(f_t)
        g_t = torch.tanh(g_t)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)
        a_t = self.sparsifier(h_t)

        return a_t, [h_t, c_t, a_t]


class AdaptiveSnapshotLSTM(Sequencer):
    def __init__(
        self,
        input_size,
        hidden_size,
        batch_first=False,
        bias=True,
        tau_min=3.0,
        tau_max=6.0,
    ):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first

        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 4 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 4 * self.hidden_size, self.bias)
        self.sparsifier = get_sparsifier(
            "adaptive", self.hidden_size, tau_min=tau_min, tau_max=tau_max
        )

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t, a_t, mov_avg_t = state
        stacked_layer = self.linear_ih(x_t) + self.linear_hh(a_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t)
        f_t = torch.sigmoid(f_t)
        g_t = torch.tanh(g_t)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)
        a_t, mov_avg_t = self.sparsifier(h_t, mov_avg_t)

        return a_t, [h_t, c_t, a_t, mov_avg_t]


class FemtoLSTM(Sequencer):
    def __init__(
        self, input_size, hidden_size, num_blocks, batch_first=False, bias=True
    ):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first
        self.num_blocks = num_blocks

        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 4 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 4 * self.hidden_size, self.bias)
        self.block_i = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_f = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_g = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_o = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.sparsifier = get_sparsifier("threshold", self.hidden_size)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t, a_t = state
        stacked_layer = self.linear_ih(x_t) + self.linear_hh(a_t)

        i_l_t, f_l_t = self.block_i(h_t), self.block_f(h_t)
        g_l_t, o_l_t = self.block_g(h_t), self.block_o(h_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t + i_l_t)
        f_t = torch.sigmoid(f_t + f_l_t)
        g_t = torch.tanh(g_t + g_l_t)
        o_t = torch.sigmoid(o_t + o_l_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)
        a_t = self.sparsifier(h_t)

        return a_t, [h_t, c_t, a_t]


class AdaptiveFemtoLSTM(Sequencer):
    def __init__(
        self,
        input_size,
        hidden_size,
        num_blocks,
        batch_first=False,
        bias=True,
        tau_min=3.0,
        tau_max=6.0,
    ):
        state_shapes = [[hidden_size], [hidden_size], [hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first
        self.num_blocks = num_blocks

        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 4 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 4 * self.hidden_size, self.bias)
        self.block_i = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_f = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_g = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.block_o = BlockDiagLinear(
            self.hidden_size, self.hidden_size, self.num_blocks, bias=False
        )
        self.sparsifier = get_sparsifier(
            "adaptive", self.hidden_size, tau_min=tau_min, tau_max=tau_max
        )

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t, a_t, mov_avg_t = state
        stacked_layer = self.linear_ih(x_t) + self.linear_hh(a_t)

        i_l_t, f_l_t = self.block_i(h_t), self.block_f(h_t)
        g_l_t, o_l_t = self.block_g(h_t), self.block_o(h_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t + i_l_t)
        f_t = torch.sigmoid(f_t + f_l_t)
        g_t = torch.tanh(g_t + g_l_t)
        o_t = torch.sigmoid(o_t + o_l_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)
        a_t, mov_avg_t = self.sparsifier(h_t, mov_avg_t)

        return a_t, [h_t, c_t, a_t, mov_avg_t]
