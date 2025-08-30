"""BLOCK-RNN:
RNN layers based on fmot loops that process inputs in a block-wise fashion
"""
import torch
from torch import nn, Tensor
from torch.nn import functional as F
from typing import Optional
from fmot.nn import Sequencer, Loop, SuperStructure
from fmot.nn.sequenced_rnn import rsetattr, rgetattr, get_trailing_number
import math
import logging

logger = logging.getLogger(__name__)


BLOCK_TORCH2SEQ_MAPPING = {
    "shared_rnn.weight_ih_l": ("layers.", ".loop.weight_ih"),
    "shared_rnn.weight_hh_l": ("layers.", ".loop.weight_hh"),
    "shared_rnn.bias_ih_l": ("layers.", ".loop.bias_ih"),
    "shared_rnn.bias_hh_l": ("layers.", ".loop.bias_hh"),
}


def map_param_name(torch_name, mapping=BLOCK_TORCH2SEQ_MAPPING):
    # Find the layer number from string
    l = get_trailing_number(torch_name)
    torch_key = torch_name.replace(l, "")
    s_start, s_end = mapping[torch_key]
    seq_name = s_start + l + s_end

    return seq_name


def transfer_param(
    parent,
    sequencer,
    inherited_name,
    inherited_dict: dict[str, tuple[str, str]],
    mapping=BLOCK_TORCH2SEQ_MAPPING,
):
    for name, param in parent.named_parameters():
        new_name = map_param_name(name, mapping)
        rsetattr(sequencer, new_name, param)
        new_param_name = inherited_name + map_param_name(name, mapping)
        inherited_dict[inherited_name + name] = (new_param_name, None)


class GRUCellEQN(nn.Module):
    """Low-level GRU cell implemented strictly with tensor ops.

    This class mirrors the maths used by `torch.nn.functional.gru_cell`
    but keeps the weight and bias tensors as explicit arguments.  It is meant
    for internal use inside custom loop kernels where parameters must live on
    the enclosing module, not on the cell itself.

    Args:
        x_t (Tensor): Input at the current time step, shape ``(B, C_in)``.
        h_t (Tensor): Hidden state from the previous step, shape ``(B, C_hid)``.
        w_ih (Tensor): Input-to-hidden weights, shape
            ``(3 * C_hid, C_in)``.
        w_hh (Tensor): Hidden-to-hidden weights, shape
            ``(3 * C_hid, C_hid)``.
        b_ih (Tensor): Input-side bias, shape ``(3 * C_hid,)``.
        b_hh (Tensor): Hidden-side bias, shape ``(3 * C_hid,)``.

    Returns:
        Tensor: Next hidden state ``h_{t+1}``, shape ``(B, C_hid)``.
    """

    def forward(
        self,
        x_t: Tensor,
        h_t: Tensor,
        w_ih: Tensor,
        w_hh: Tensor,
        b_ih: Tensor,
        b_hh: Tensor,
    ) -> Tensor:
        u_x = torch.matmul(x_t, w_ih.t()) + b_ih
        u_h = torch.matmul(h_t, w_hh.t()) + b_hh

        r_x, z_x, n_x = u_x.chunk(3, -1)
        r_h, z_h, n_h = u_h.chunk(3, -1)

        r_t = torch.sigmoid(r_x + r_h)
        z_t = torch.sigmoid(z_x + z_h)
        n_t = torch.tanh(n_x + r_t * n_h)

        h_t = (1 - z_t) * n_t + z_t * h_t

        return h_t


class LSTMCellEQN(nn.Module):
    """Low-level LSTM cell implemented strictly with tensor ops.

    Identical to `torch.nn.functional.lstm_cell` but expressed as
    primitive tensor operations. Intended to be used internally
    inside custom loop kernels where parameters must live on
    the enclosing module, not on the cell itself.

    Args:
        x_t (Tensor): Input at the current time step, ``(B, C_in)``.
        h_t (Tensor): Hidden state from the previous step, ``(B, C_hid)``.
        c_t (Tensor): Cell state from the previous step, ``(B, C_hid)``.
        w_ih (Tensor): Input-to-hidden weight matrix, ``(4*C_hid, C_in)``.
        w_hh (Tensor): Hidden-to-hidden weight matrix, ``(4*C_hid, C_hid)``.
        b_ih (Tensor): Input-side bias, ``(4*C_hid,)``.
        b_hh (Tensor): Hidden-side bias, ``(4*C_hid,)``.

    Returns:
        tuple[Tensor, Tensor]: ``(h_{t+1}, c_{t+1})``, each ``(B, C_hid)``.
    """

    def forward(
        self,
        x_t: Tensor,
        h_t: Tensor,
        c_t: Tensor,
        w_ih: Tensor,
        w_hh: Tensor,
        b_ih: Tensor,
        b_hh: Tensor,
    ) -> tuple[Tensor, Tensor]:
        u = torch.matmul(x_t, w_ih.t()) + torch.matmul(h_t, w_hh.t()) + b_ih + b_hh

        i_t, f_t, g_t, o_t = u.chunk(4, -1)
        i_t = torch.sigmoid(i_t)
        f_t = torch.sigmoid(f_t)
        g_t = torch.tanh(g_t)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)

        return h_t, c_t


class _BlockRNN(nn.Module):
    """Shared implementation for *block-wise* RNN layers.

    Each forward pass treats the feature dimension as **N independent
    sub-sequences (“blocks”)** that are processed by a single shared RNN.  This
    drastically reduces the parameter count while retaining per-block
    recurrence.

    Dilation > 1 lets the model capture longer temporal contexts without growing
    the hidden-state size: *D parallel, interleaved copies* of the RNN are
    created implicitly by round-robin dispatching consecutive frames to one of D
    hidden-state banks.

    Args:
        cell_type (type[nn.Module]): `nn.GRU or nn.LSTM.
        block_input_size (int): Feature size per block.
        num_blocks (int): Number of independent blocks in the input.
        block_hidden_size (int): Hidden size for each block.
        num_layers (int, optional): Stacked RNN depth. Defaults to ``1``.
        bias (bool, optional): Include bias parameters. Defaults to ``True``.
        dropout (float, optional): Inter-layer dropout. Defaults to ``0.0``.
        dilation (int, optional): Temporal dilation ``D``.  ``D= 1``: standard RNN. Defaults to ``1``.

    Attributes:
        shared_rnn (nn.Module): The underlying PyTorch RNN shared across blocks.

    Shape:
        - **Input**: `(B, T, num_blocks * block_input_size)
        - **Output**: `(B, T, num_blocks * block_hidden_size)

    Raises:
        ValueError: If the channel dimension does not equal
            `num_blocks * block_input_size.
    """

    def __init__(
        self,
        cell_type: type[nn.Module],
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__()
        self.shared_rnn = cell_type(
            block_input_size,
            block_hidden_size,
            num_layers=num_layers,
            bias=bias,
            batch_first=True,
            bidirectional=False,
            dropout=dropout,
        )

        self.num_blocks = num_blocks
        self.block_input_size = block_input_size
        self._expected_channels = num_blocks * block_input_size
        self.block_hidden_size = block_hidden_size
        self.num_layers = num_layers
        self.bias = bias
        self.dropout = dropout
        self.dilation = dilation

    # ---------------------------------------------------------------------
    # helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def _check_channels(C: int, expected: int) -> None:
        if C != expected:
            raise ValueError(f"Expected feature dimension {expected}, got {C} instead")

    @staticmethod
    def _dilate(x: Tensor, dilation: int) -> tuple[Tensor, int]:
        """Pack *dilation* into the batch dimension.

        Returns the dilated sequence and the padded time length *Tp*.
        """
        if dilation == 1:
            return x, x.size(1)  # no-op

        B, T, C = x.shape
        Tp = math.ceil(T / dilation) * dilation
        if Tp != T:  # pad so T is divisible by D
            x = F.pad(x, (0, 0, 0, Tp - T))

        # (B, Tp, C) → (B, Tp/D, D, C) → (B·D, Tp/D, C)
        x = (
            x.view(B, Tp // dilation, dilation, C)
            .transpose(1, 2)  # put dilation in dim=1 for contiguous reshape
            .reshape(B * dilation, Tp // dilation, C)
        )
        return x, Tp

    @staticmethod
    def _undilate(y: Tensor, B: int, Tp: int, dilation: int) -> Tensor:
        """Inverse of :meth:`_dilate`.  Reconstruct original (B, Tp, C) order."""
        if dilation == 1:
            return y

        C = y.size(-1)
        Td = Tp // dilation
        y = y.view(B, dilation, Td, C).transpose(1, 2).reshape(B, Tp, C)
        return y

    @staticmethod
    def _split_blocks(x: Tensor, num_blocks: int, block_size: int) -> Tensor:
        """(B, T, C) → (B·num_blocks, T, block_size) where C = num_blocks·block_size"""
        B, T, _ = x.shape
        return (
            x.view(B, T, num_blocks, block_size)
            .transpose(1, 2)  # (B, num_blocks, T, block_size)
            .reshape(B * num_blocks, T, block_size)
        )

    @staticmethod
    def _merge_blocks(y: Tensor, B: int, T: int, num_blocks: int) -> Tensor:
        """Inverse of :meth:`_split_blocks`.  (B·nb, T, F) → (B, T, nb·F)"""
        F = y.size(-1)
        return (
            y.view(B, num_blocks, T, F)
            .transpose(1, 2)  # (B, T, num_blocks, F)
            .reshape(B, T, num_blocks * F)
        )

    def forward(self, x: Tensor) -> Tensor:  # (B, T, C)
        B, T, C = x.shape
        self._check_channels(C, self._expected_channels)

        # 1) Temporal dilation ————————————————————————————————
        x, Tp = self._dilate(x, self.dilation)  # (B·D, T', C)

        # 2) Block-wise split   ————————————————————————————————
        x = self._split_blocks(
            x, self.num_blocks, self.block_input_size
        )  # (B·D·nb, T', Fi)

        # 3) Shared RNN         ————————————————————————————————
        y, _ = self.shared_rnn(x)  # same shape as *x*

        # 4) Merge & undilate   ————————————————————————————————
        y = self._merge_blocks(
            y, B * self.dilation, Tp // self.dilation, self.num_blocks
        )
        y = self._undilate(y, B, Tp, self.dilation)

        return y[:, :T]  # trim any pad


class BlockGRU(_BlockRNN):
    """Grouped-channel GRU that shares parameters across blocks.

    ``BlockGRU`` behaves like :class:`torch.nn.GRU`, but it partitions the
    feature dimension into *N* equal “blocks” and applies *one* GRU to each
    block in parallel.  All blocks reuse the same weights, so the parameter
    count is independent of `num_blocks`.  This yields:

    * strong inductive bias for signals with repeated structure
    * smaller models (≈ 1/N^2 the parameters of a full GRU)
    * higher arithmetic intensity (more parameter reuse)

    Dilation > 1 lets the model capture longer temporal contexts without growing
    the hidden-state size: *D parallel, interleaved copies* of the RNN are
    created implicitly by round-robin dispatching consecutive frames to one of D
    hidden-state banks.

    Args:
        block_input_size (int):  Width of **one** block fed to the shared GRU.
        num_blocks (int): Number of independent blocks, i.e. how many times
            `block_input_size` appears in the channel dimension.
        block_hidden_size (int): Hidden size **per block**.  The overall output channel count is
            `num_blocks * block_hidden_size`.
        num_layers (int, optional): Stacked RNN depth. Defaults to ``1``.
        bias (bool, optional): Include bias parameters. Defaults to ``True``.
        dropout (float, optional): Inter-layer dropout. Defaults to ``0.0``.
        dilation (int, optional): Temporal dilation ``D``.  ``D= 1``: standard RNN. Defaults to ``1``.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size)``

        where ``B`` is the batch size and ``T`` is the time dimension.

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.GRU` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·num_blocks, T, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__(
            nn.GRU,
            block_input_size,
            num_blocks,
            block_hidden_size,
            num_layers,
            bias,
            dropout,
            dilation=dilation,
        )


class BlockLSTM(_BlockRNN):
    """Grouped-channel LSTM that shares parameters across blocks.

    ``BlockLSTM`` behaves like :class:`torch.nn.LSTM`, but it partitions the
    feature dimension into *N* equal “blocks” and applies *one* LSTM to each
    block in parallel.  All blocks reuse the same weights, so the parameter
    count is independent of `num_blocks`.  This yields:

    * strong inductive bias for signals with repeated structure
    * smaller models (≈ 1/N^2 the parameters of a full LSTM)
    * higher arithmetic intensity (more parameter reuse)

    Dilation > 1 lets the model capture longer temporal contexts without growing
    the hidden-state size: *D parallel, interleaved copies* of the RNN are
    created implicitly by round-robin dispatching consecutive frames to one of D
    hidden-state banks.

    Args:
        block_input_size (int):  Width of **one** block fed to the shared LSTM.
        num_blocks (int): Number of independent blocks, i.e. how many times
            `block_input_size` appears in the channel dimension.
        block_hidden_size (int): Hidden size **per block**.  The overall output channel count is
            `num_blocks * block_hidden_size`.
        num_layers (int, optional): Stacked RNN depth. Defaults to ``1``.
        bias (bool, optional): Include bias parameters. Defaults to ``True``.
        dropout (float, optional): Inter-layer dropout. Defaults to ``0.0``.
        dilation (int, optional): Temporal dilation ``D``.  ``D = 1``: standard RNN. Defaults to ``1``.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size)``

        where ``B`` is the batch size and ``T`` is the time dimension.

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.LSTM` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·num_blocks, T, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__(
            nn.LSTM,
            block_input_size,
            num_blocks,
            block_hidden_size,
            num_layers,
            bias,
            dropout,
            dilation=dilation,
        )


class _BlockRNNCellLoop(Loop):
    """Generic fmot **Loop** that applies a cell equation block-by-block.

    The loop iterates over ``num_blocks`` slices of the input tensor, applying
    the provided *cell equation* (GRU or LSTM).

    Args:
        cell_eqn (type[nn.Module]): ``GRUCellEQN`` or ``LSTMCellEQN``.
        h_multiplier (int): Gate multiplier (3 for GRU, 4 for LSTM).
        n_hidden (int): How many hidden tensors are carried (1 for GRU,
            2 for LSTM).
        block_input_size (int): Features per block fed to the cell.
        block_hidden_size (int): Hidden size of the cell.
        num_blocks (int): Number of blocks to process.
        bias (bool, optional): Include bias vectors. Defaults to ``True``.
    """

    def __init__(
        self,
        cell_eqn: type[nn.Module],
        h_multiplier: int,
        n_hidden: int,
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
    ):
        super().__init__(
            n_iter=num_blocks,
            n_recurse=0,
            slice_blocksizes=[block_input_size] + [block_hidden_size] * n_hidden,
        )
        self.celleqn = cell_eqn()

        self.block_hidden_size = block_hidden_size

        self.weight_ih = nn.Parameter(
            torch.empty(block_hidden_size * h_multiplier, block_input_size)
        )
        self.weight_hh = nn.Parameter(
            torch.empty(block_hidden_size * h_multiplier, block_hidden_size)
        )
        if bias:
            self.bias_ih = nn.Parameter(torch.empty(h_multiplier * block_hidden_size))
            self.bias_hh = nn.Parameter(torch.empty(h_multiplier * block_hidden_size))

        self._init_params()

        if not bias:
            self.bias_ih = nn.Parameter(
                torch.zeros(h_multiplier * block_hidden_size), requires_grad=False
            )
            self.bias_hh = nn.Parameter(
                torch.zeros(h_multiplier * block_hidden_size), requires_grad=False
            )

    def _init_params(self):
        stdv = 1.0 / math.sqrt(self.block_hidden_size)
        for weight in self.parameters():
            nn.init.uniform_(weight, -stdv, stdv)

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        raise NotImplementedError()


class _BlockGRULoop(_BlockRNNCellLoop):
    """Loop wrapper specialised for GRU blocks."""

    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            GRUCellEQN, 3, 1, block_input_size, block_hidden_size, num_blocks, bias
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        x_t, h_t = x_sliced

        h_t = self.celleqn(
            x_t, h_t, self.weight_ih, self.weight_hh, self.bias_ih, self.bias_hh
        )
        return [], [h_t], []


class _BlockLSTMLoop(_BlockRNNCellLoop):
    """Loop wrapper specialised for LSTM blocks."""

    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            LSTMCellEQN, 4, 2, block_input_size, block_hidden_size, num_blocks, bias
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        x_t, h_t, c_t = x_sliced

        h_t, c_t = self.celleqn(
            x_t, h_t, c_t, self.weight_ih, self.weight_hh, self.bias_ih, self.bias_hh
        )
        return [], [h_t, c_t], []


class _BlockGRUSeq(Sequencer, SuperStructure):
    """Sequencer that wraps :class:`_BlockGRULoop` into a functioning RNN layer."""

    def __init__(
        self,
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
        dilation=1,
    ):
        super().__init__([[block_hidden_size * num_blocks]] * dilation)
        self.loop = _BlockGRULoop(
            block_input_size, block_hidden_size, num_blocks, bias=bias
        )
        self.dilation = dilation

    @torch.jit.export
    def step(self, x_t: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        h_t = state[0]
        (h_t,) = self.loop(x_to_slice=[x_t, h_t], x_recursed_init=[], x_scope=[])
        state = state[1:] + [h_t]
        return h_t, state


class _BlockLSTMSeq(Sequencer, SuperStructure):
    """Sequencer that wraps :class:`_BlockLSTMLoop` into a functioning RNN layer."""

    def __init__(
        self,
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
        dilation=1,
    ):
        super().__init__([[block_hidden_size * num_blocks]] * (dilation * 2))
        self.loop = _BlockLSTMLoop(
            block_input_size, block_hidden_size, num_blocks, bias=bias
        )

    @torch.jit.export
    def step(self, x_t: Tensor, state: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        h_t, c_t = state[:2]
        h_t, c_t = self.loop(x_to_slice=[x_t, h_t, c_t], x_recursed_init=[], x_scope=[])
        state = state[2:] + [h_t, c_t]
        return h_t, state


class _ConvertedBlockRNN(nn.Module):
    """Internal converted version of a block RNN for quantization / export.

    Args:
        seq_type (type[nn.Module]): ``_BlockGRUSeq`` or ``_BlockLSTMSeq``.
        block_input_size (int): See :class:`_BlockRNN`.
        num_blocks (int): See :class:`_BlockRNN`.
        block_hidden_size (int): See :class:`_BlockRNN`.
        num_layers (int, optional): Number of stacked sequencers. Defaults to ``1``.
        bias (bool, optional): Copy bias parameters. Defaults to ``True``.
        dropout (float, optional): Inter-layer dropout (retained for parity). Defaults to ``0.0``.
    """

    def __init__(
        self,
        seq_type: type[nn.Module],
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__()

        self.layers = nn.ModuleList()
        isize = block_input_size
        for i in range(num_layers):
            self.layers.append(
                seq_type(
                    isize, block_hidden_size, num_blocks, bias=bias, dilation=dilation
                )
            )
            isize = block_hidden_size

    def forward(self, x):
        for layer in self.layers:
            x, _ = layer(x)
        return x

    @classmethod
    def _from_torchmodule(
        cls,
        parent,
        toplevel=None,
        inherited_name="",
        inherited_dict: dict = dict(),
    ):
        new = cls(
            block_input_size=parent.block_input_size,
            block_hidden_size=parent.block_hidden_size,
            num_blocks=parent.num_blocks,
            num_layers=parent.num_layers,
            bias=parent.bias,
            dropout=parent.dropout,
            dilation=parent.dilation,
        )

        transfer_param(
            parent, new, inherited_name, inherited_dict, BLOCK_TORCH2SEQ_MAPPING
        )

        return new


class ConvertedBlockGRU(_ConvertedBlockRNN):
    """Converted, quantization-ready version of :class:`BlockGRU`."""

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__(
            _BlockGRUSeq,
            block_input_size,
            num_blocks,
            block_hidden_size,
            num_layers,
            bias,
            dropout,
            dilation=dilation,
        )


class ConvertedBlockLSTM(_ConvertedBlockRNN):
    """Converted, quantization-ready version of :class:`BlockLSTM`."""

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        dropout: float = 0,
        dilation: int = 1,
    ):
        super().__init__(
            _BlockLSTMSeq,
            block_input_size,
            num_blocks,
            block_hidden_size,
            num_layers,
            bias,
            dropout,
            dilation=dilation,
        )
