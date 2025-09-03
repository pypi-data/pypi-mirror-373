import torch
from torch import nn, Tensor
from fmot.nn.blockrnn import GRUCellEQN, LSTMCellEQN, transfer_param
from fmot.nn import Loop, SuperStructure
from fmot.nn.atomics import Chunk, Cat
import math


UNI_BAND_TORCH2SEQ_MAPPING = {
    "shared_rnn.weight_ih_l": ("layers.", ".weight_ih"),
    "shared_rnn.weight_hh_l": ("layers.", ".weight_hh"),
    "shared_rnn.bias_ih_l": ("layers.", ".bias_ih"),
    "shared_rnn.bias_hh_l": ("layers.", ".bias_hh"),
}

BI_BAND_TORCH2SEQ_MAPPING = {
    "fwd_rnn.weight_ih_l": ("layers.", ".weight_ih_fwd"),
    "fwd_rnn.weight_hh_l": ("layers.", ".weight_hh_fwd"),
    "fwd_rnn.bias_ih_l": ("layers.", ".bias_ih_fwd"),
    "fwd_rnn.bias_hh_l": ("layers.", ".bias_hh_fwd"),
    "rev_rnn.weight_ih_l": ("layers.", ".weight_ih_rev"),
    "rev_rnn.weight_hh_l": ("layers.", ".weight_hh_rev"),
    "rev_rnn.bias_ih_l": ("layers.", ".bias_ih_rev"),
    "rev_rnn.bias_hh_l": ("layers.", ".bias_hh_rev"),
}


class _BandRNN(nn.Module):
    """Base class for a unidirectional band RNN cell

    Arguments:
        cell_type (type): e.g. torch.nn.GRU, torch.nn.LSTM
        block_input_size (int): size of each block in the input activation
        num_blocks (int): number of blocks
        hidden_size_per_block (int): hidden-size per block
        bias (bool):
        dropout (bool):
    """

    def __init__(
        self,
        cell_type: type[nn.Module],
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__()
        self.shared_rnn = cell_type(
            block_input_size,
            block_hidden_size,
            bias=bias,
            batch_first=True,
            dropout=dropout,
        )

        self.num_blocks = num_blocks
        self.block_input_size = block_input_size
        self._expected_chin = num_blocks * block_input_size
        self.block_hidden_size = block_hidden_size
        self.bias = bias
        self.dropout = dropout

    def forward(self, x: Tensor) -> Tensor:
        B, T, C = x.shape
        if C != self._expected_chin:
            raise ValueError(f"Expected {self._expected_chin}, got {C} instead")

        # reshape sequence to (B * T, num_blocks, block_input_size)
        # so that it iterates over num_blocks as the "sequential" dimension
        x = x.reshape(B * T, self.num_blocks, self.block_input_size)

        y, _ = self.shared_rnn(x)
        # output shape: (B * T, num_blocks, block_hidden_size)

        # reshape output to (B, T, num_blocks * block_hidden_size)
        y = y.reshape(B, T, self.block_hidden_size * self.num_blocks)

        return y


class _BidirectionalBandRNN(nn.Module):
    """Base class for a bidirectional band RNN cell

    Arguments:
        cell_type (type): e.g. torch.nn.GRU, torch.nn.LSTM
        block_input_size (int): size of each block in the input activation
        num_blocks (int): number of blocks
        hidden_size_per_block (int): hidden-size per block
        bias (bool):
        dropout (bool):
    """

    def __init__(
        self,
        cell_type: type[nn.Module],
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__()
        self.fwd_rnn = cell_type(
            block_input_size,
            block_hidden_size,
            num_layers=1,
            bias=bias,
            batch_first=True,
            dropout=dropout,
        )
        self.rev_rnn = cell_type(
            block_input_size,
            block_hidden_size,
            num_layers=1,
            bias=bias,
            batch_first=True,
            dropout=dropout,
        )

        self.num_blocks = num_blocks
        self.block_input_size = block_input_size
        self._expected_chin = num_blocks * block_input_size
        self.block_hidden_size = block_hidden_size
        self.bias = bias
        self.dropout = dropout

    def forward(self, x: Tensor) -> Tensor:
        B, T, C = x.shape
        if C != self._expected_chin:
            raise ValueError(f"Expected {self._expected_chin}, got {C} instead")

        # reshape sequence to (B * T, num_blocks, block_input_size)
        # so that it iterates over num_blocks as the "sequential" dimension
        x = x.reshape(B * T, self.num_blocks, self.block_input_size)

        y_fwd, _ = self.fwd_rnn(x)
        y_rev, _ = self.rev_rnn(torch.flip(x, (1,)))
        y_rev = torch.flip(y_rev, (1,))
        y = torch.cat([y_fwd, y_rev], -1)
        # output shape: (B * T, num_blocks, 2 * block_hidden_size)

        # reshape output to (B, T, 2 * num_blocks * block_hidden_size)
        y = y.reshape(B, T, self.block_hidden_size * self.num_blocks * 2)

        return y


class BandLSTM(_BandRNN):
    """Band LSTM iterates an LSTM over the band-dimension, rather than the time-dimension.

    ``BandLSTM`` behaves like :class:`torch.nn.LSTM` applied to the *band* dimension.
    It partitions the feature dimension into *N* equal "bands" and iterates an LSTM
    over these bands. The hidden-states from each iteration are concatenated into the final
    feature dimension.

    Args:
        block_input_size (int): size of each band in the input activation
        num_blocks (int): number of bands
        block_hidden_size (int): hidden-size per band
        bias (bool, optional): if True, uses a bias in the LSTM. Default True.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size)``

        where ``B`` is the batch size and ``T`` is the time dimension.

        The layer is equivalent to:

        .. code:: python

            def apply_band_lstm(x: Tensor, block_input_size: int, num_blocks: int, lstm: nn.LSTM):
                # x shape: [B, T, block_input_size * num_blocks]

                B, T, _ = x.shape
                x = x.reshape(B * T, num_blocks, block_input_size)
                y, _ = lstm(x) # [B*T, num_blocks, block_hidden_size]
                y = y.reshape(B, T, -1) # [B, T, num_blocks * block_hidden_size]
                return y

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.LSTM` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·T, num_blocks, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
    ):
        super().__init__(nn.LSTM, block_input_size, num_blocks, block_hidden_size, bias)


class BidirectionalBandLSTM(_BidirectionalBandRNN):
    """Bidirectional Band LSTM iterates a bidirectional LSTM over the band-dimension, rather than the time-dimension.

    ``BidirectionalBandLSTM`` behaves like a bidirectional :class:`torch.nn.LSTM` applied to the *band* dimension.
    It partitions the feature dimension into *N* equal "bands" and iterates an LSTM
    over these bands. The hidden-states from each iteration and direction are concatenated into the final
    feature dimension.

    Args:
        block_input_size (int): size of each band in the input activation
        num_blocks (int): number of bands
        block_hidden_size (int): hidden-size per band
        bias (bool, optional): if True, uses a bias in the LSTM. Default True.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size · 2)``

        where ``B`` is the batch size and ``T`` is the time dimension.

        The layer is equivalent to:

        .. code:: python

            def apply_band_lstm(x: Tensor, block_input_size: int, num_blocks: int, lstm: nn.LSTM):
                # x shape: [B, T, block_input_size * num_blocks]

                B, T, _ = x.shape
                x = x.reshape(B * T, num_blocks, block_input_size)
                y, _ = lstm(x) # [B*T, num_blocks, block_hidden_size]
                y = y.reshape(B, T, -1) # [B, T, num_blocks * block_hidden_size * 2]
                return y

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.LSTM` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·T, num_blocks, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            nn.LSTM, block_input_size, num_blocks, block_hidden_size, bias, dropout
        )


class BandGRU(_BandRNN):
    """Band GRU iterates a GRU over the band-dimension, rather than the time-dimension.

    ``BandGRU`` behaves like :class:`torch.nn.GRU` applied to the *band* dimension.
    It partitions the feature dimension into *N* equal "bands" and iterates an GRU
    over these bands. The hidden-states from each iteration are concatenated into the final
    feature dimension.

    Args:
        block_input_size (int): size of each band in the input activation
        num_blocks (int): number of bands
        block_hidden_size (int): hidden-size per band
        bias (bool, optional): if True, uses a bias in the GRU. Default True.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size)``

        where ``B`` is the batch size and ``T`` is the time dimension.

        The layer is equivalent to:

        .. code:: python

            def apply_band_lstm(x: Tensor, block_input_size: int, num_blocks: int, lstm: nn.GRU):
                # x shape: [B, T, block_input_size * num_blocks]

                B, T, _ = x.shape
                x = x.reshape(B * T, num_blocks, block_input_size)
                y, _ = lstm(x) # [B*T, num_blocks, block_hidden_size]
                y = y.reshape(B, T, -1) # [B, T, num_blocks * block_hidden_size]
                return y

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.GRU` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·T, num_blocks, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            nn.GRU, block_input_size, num_blocks, block_hidden_size, bias, dropout
        )


class BidirectionalBandGRU(_BidirectionalBandRNN):
    """Bidirectional Band GRU iterates a bidirectional GRU over the band-dimension, rather than the time-dimension.

    ``BidirectionalBandGRU`` behaves like a bidirectional :class:`torch.nn.GRU` applied to the *band* dimension.
    It partitions the feature dimension into *N* equal "bands" and iterates an GRU
    over these bands. The hidden-states from each iteration and direction are concatenated into the final
    feature dimension.

    Args:
        block_input_size (int): size of each band in the input activation
        num_blocks (int): number of bands
        block_hidden_size (int): hidden-size per band
        bias (bool, optional): if True, uses a bias in the GRU. Default True.

    Shape:
        * **Input:**  ``(B, T, num_blocks · block_input_size)``
        * **Output:** ``(B, T, num_blocks · block_hidden_size · 2)``

        where ``B`` is the batch size and ``T`` is the time dimension.

        The layer is equivalent to:

        .. code:: python

            def apply_band_lstm(x: Tensor, block_input_size: int, num_blocks: int, lstm: nn.GRU):
                # x shape: [B, T, block_input_size * num_blocks]

                B, T, _ = x.shape
                x = x.reshape(B * T, num_blocks, block_input_size)
                y, _ = lstm(x) # [B*T, num_blocks, block_hidden_size]
                y = y.reshape(B, T, -1) # [B, T, num_blocks * block_hidden_size * 2]
                return y

    Note:
        * Parameters are stored in a single underlying :class:`torch.nn.GRUb` called ``self.shared_rnn``.
        * During the forward pass the input is reshaped to ``(B·T, num_blocks, block_input_size)`` so that PyTorch can leverage its cuDNN/CPU kernels without modification.
    """

    report_supported = True

    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            nn.GRU, block_input_size, num_blocks, block_hidden_size, bias, dropout
        )


class _UnidirectionalBandRNNLoop(Loop):
    def __init__(
        self,
        celleqn: type[nn.Module],
        n_gates: int,
        n_state: int,
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
    ):
        super().__init__(
            n_iter=num_blocks,
            n_recurse=n_state,
            slice_blocksizes=[
                block_input_size,
            ],
        )

        self.celleqn = celleqn()

        self.block_hidden_size = block_hidden_size

        self.weight_ih = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_input_size)
        )
        self.weight_hh = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_hidden_size)
        )
        if bias:
            self.bias_ih = nn.Parameter(torch.empty(n_gates * block_hidden_size))
            self.bias_hh = nn.Parameter(torch.empty(n_gates * block_hidden_size))

        self._init_params()

        if not bias:
            self.bias_ih = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
            )
            self.bias_hh = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
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


class _UnidirectionalBandGRULoop(_UnidirectionalBandRNNLoop):
    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            celleqn=GRUCellEQN,
            n_gates=3,
            n_state=1,
            block_input_size=block_input_size,
            block_hidden_size=block_hidden_size,
            num_blocks=num_blocks,
            bias=bias,
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        (h_t,) = x_recursed
        (x_t,) = x_sliced

        h_t = self.celleqn(
            x_t, h_t, self.weight_ih, self.weight_hh, self.bias_ih, self.bias_hh
        )

        return [h_t], [h_t], []


class _UnidirectionalBandLSTMLoop(_UnidirectionalBandRNNLoop):
    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            celleqn=LSTMCellEQN,
            n_gates=4,
            n_state=2,
            block_input_size=block_input_size,
            block_hidden_size=block_hidden_size,
            num_blocks=num_blocks,
            bias=bias,
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        (h_t, c_t) = x_recursed
        (x_t,) = x_sliced

        h_t, c_t = self.celleqn(
            x_t, h_t, c_t, self.weight_ih, self.weight_hh, self.bias_ih, self.bias_hh
        )

        return [h_t, c_t], [h_t], []


class _BidirectionalBandRNNLoop(Loop):
    def __init__(
        self,
        celleqn: type[nn.Module],
        n_gates: int,
        n_state: int,
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
    ):
        super().__init__(
            n_iter=num_blocks,
            n_recurse=2 * n_state,
            slice_blocksizes=[block_input_size, block_input_size],
        )
        self.celleqn_fwd = celleqn()
        self.celleqn_rev = celleqn()

        self.block_hidden_size = block_hidden_size

        self.weight_ih_fwd = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_input_size)
        )
        self.weight_ih_rev = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_input_size)
        )
        self.weight_hh_fwd = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_hidden_size)
        )
        self.weight_hh_rev = nn.Parameter(
            torch.empty(block_hidden_size * n_gates, block_hidden_size)
        )
        if bias:
            self.bias_ih_fwd = nn.Parameter(torch.empty(n_gates * block_hidden_size))
            self.bias_ih_rev = nn.Parameter(torch.empty(n_gates * block_hidden_size))
            self.bias_hh_fwd = nn.Parameter(torch.empty(n_gates * block_hidden_size))
            self.bias_hh_rev = nn.Parameter(torch.empty(n_gates * block_hidden_size))

        self._init_params()

        if not bias:
            self.bias_ih_fwd = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
            )
            self.bias_ih_rev = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
            )
            self.bias_hh_fwd = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
            )
            self.bias_hh_rev = nn.Parameter(
                torch.zeros(n_gates * block_hidden_size), requires_grad=False
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


class _BidirectionalBandGRULoop(_BidirectionalBandRNNLoop):
    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            celleqn=GRUCellEQN,
            n_gates=3,
            n_state=1,
            block_input_size=block_input_size,
            block_hidden_size=block_hidden_size,
            num_blocks=num_blocks,
            bias=bias,
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        h_t_fwd, h_t_rev = x_recursed
        x_t_fwd, x_t_rev = x_sliced

        h_t_fwd = self.celleqn_fwd(
            x_t_fwd,
            h_t_fwd,
            self.weight_ih_fwd,
            self.weight_hh_fwd,
            self.bias_ih_fwd,
            self.bias_hh_fwd,
        )
        h_t_rev = self.celleqn_rev(
            x_t_rev,
            h_t_rev,
            self.weight_ih_rev,
            self.weight_hh_rev,
            self.bias_ih_rev,
            self.bias_hh_rev,
        )

        return [h_t_fwd, h_t_rev], [h_t_fwd, h_t_rev], []


class _BidirectionalBandLSTMLoop(_BidirectionalBandRNNLoop):
    def __init__(
        self, block_input_size: int, block_hidden_size: int, num_blocks: int, bias=True
    ):
        super().__init__(
            celleqn=LSTMCellEQN,
            n_gates=4,
            n_state=2,
            block_input_size=block_input_size,
            block_hidden_size=block_hidden_size,
            num_blocks=num_blocks,
            bias=bias,
        )

    @torch.jit.export
    def step(
        self, x_sliced: list[Tensor], x_recursed: list[Tensor], x_scope: list[Tensor]
    ) -> tuple[list[Tensor], list[Tensor], list[Tensor]]:
        h_t_fwd, c_t_fwd, h_t_rev, c_t_rev = x_recursed
        x_t_fwd, x_t_rev = x_sliced

        h_t_fwd, c_t_fwd = self.celleqn_fwd(
            x_t_fwd,
            h_t_fwd,
            c_t_fwd,
            self.weight_ih_fwd,
            self.weight_hh_fwd,
            self.bias_ih_fwd,
            self.bias_hh_fwd,
        )
        h_t_rev, c_t_rev = self.celleqn_rev(
            x_t_rev,
            h_t_rev,
            c_t_rev,
            self.weight_ih_rev,
            self.weight_hh_rev,
            self.bias_ih_rev,
            self.bias_hh_rev,
        )

        return [h_t_fwd, c_t_fwd, h_t_rev, c_t_rev], [h_t_fwd, h_t_rev], []


class _ConvertedUnidirectionalBandRNN(nn.Module):
    def __init__(
        self,
        loop_rnn: type[_UnidirectionalBandRNNLoop],
        block_input_size: int,
        block_hidden_size: int,
        num_blocks: int,
        bias=True,
        dropout: float = 0,
    ):
        super().__init__()

        self.block_input_size = block_input_size
        self.num_blocks = num_blocks
        self.block_hidden_size = block_hidden_size
        self.bias = bias
        self.dropout = dropout

        self.layers = nn.ModuleList()

        for _ in range(1):
            self.layers.append(
                loop_rnn(block_input_size, block_hidden_size, num_blocks, bias)
            )

        self.zero_init = nn.Parameter(
            torch.zeros(block_hidden_size), requires_grad=False
        )

    @classmethod
    def _from_torchmodule(
        cls,
        parent: BandGRU,
        toplevel=None,
        inherited_name="",
        inherited_dict: dict = dict(),
    ):
        new = cls(
            block_input_size=parent.block_input_size,
            block_hidden_size=parent.block_hidden_size,
            num_blocks=parent.num_blocks,
            bias=parent.bias,
            dropout=parent.dropout,
        )

        transfer_param(
            parent, new, inherited_name, inherited_dict, UNI_BAND_TORCH2SEQ_MAPPING
        )

        return new

    def forward(self, x):
        raise NotImplementedError()


class ConvertedUnidirectionalBandGRU(_ConvertedUnidirectionalBandRNN):
    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            _UnidirectionalBandGRULoop,
            block_input_size,
            block_hidden_size,
            num_blocks,
            bias,
            dropout,
        )

    def forward(self, x):
        for layer in self.layers:
            (x,) = layer(x_to_slice=[x], x_recursed_init=[self.zero_init], x_scope=[])

        return x


class ConvertedUnidirectionalBandLSTM(_ConvertedUnidirectionalBandRNN):
    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            _UnidirectionalBandLSTMLoop,
            block_input_size,
            block_hidden_size,
            num_blocks,
            bias,
            dropout,
        )

    def forward(self, x):
        for layer in self.layers:
            (x,) = layer(
                x_to_slice=[x],
                x_recursed_init=[self.zero_init, self.zero_init],
                x_scope=[],
            )

        return x


class BandReverse(SuperStructure):
    def __init__(self, num_blocks):
        super().__init__()
        self.num_blocks = num_blocks
        self.chunk = Chunk(num_blocks, -1)
        self.cat = Cat(dim=-1)

    def forward(self, x):
        chunks = self.chunk(x)
        chunks = chunks[::-1]
        y = self.cat(chunks)
        return y


class BiDirInterleave(SuperStructure):
    def __init__(self, num_blocks):
        super().__init__()
        self.num_blocks = num_blocks
        self.chunk = Chunk(num_blocks, -1)
        self.cat = Cat(dim=-1)

    def forward(self, x_fwd, x_rev):
        chunks_fwd = self.chunk(x_fwd)
        chunks_rev = self.chunk(x_rev)
        chunks_rev = chunks_rev[::-1]
        to_cat = []
        for a, b in zip(chunks_fwd, chunks_rev):
            to_cat += [a, b]
        y = self.cat(to_cat)
        return y


class _ConvertedBidirectionalBandRNN(nn.Module):
    def __init__(
        self,
        loop_cls: type[_BidirectionalBandRNNLoop],
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__()
        self.block_input_size = block_input_size
        self.num_blocks = num_blocks
        self.block_hidden_size = block_hidden_size
        self.bias = bias
        self.dropout = dropout

        self.layers = nn.ModuleList()

        for _ in range(1):
            self.layers.append(
                loop_cls(block_input_size, block_hidden_size, num_blocks, bias)
            )

        self.zero_init = nn.Parameter(
            torch.zeros(block_hidden_size), requires_grad=False
        )

        self.band_reverse = BandReverse(num_blocks)
        self.bidir_interleave = BiDirInterleave(num_blocks)

    @classmethod
    def _from_torchmodule(
        cls,
        parent: BandGRU,
        toplevel=None,
        inherited_name="",
        inherited_dict: dict = dict(),
    ):
        new = cls(
            block_input_size=parent.block_input_size,
            block_hidden_size=parent.block_hidden_size,
            num_blocks=parent.num_blocks,
            bias=parent.bias,
            dropout=parent.dropout,
        )

        transfer_param(
            parent, new, inherited_name, inherited_dict, BI_BAND_TORCH2SEQ_MAPPING
        )

        return new

    def forward(self, x):
        raise NotImplementedError()


class ConvertedBidirectionalBandGRU(_ConvertedBidirectionalBandRNN):
    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            _BidirectionalBandGRULoop,
            block_input_size,
            num_blocks,
            block_hidden_size,
            bias,
            dropout,
        )

    def forward(self, x):
        x_fwd = x
        x_rev = self.band_reverse(x)

        for layer in self.layers:
            x_fwd, x_rev = layer(
                x_to_slice=[x_fwd, x_rev],
                x_recursed_init=[self.zero_init, self.zero_init],
                x_scope=[],
            )
            x = self.bidir_interleave(x_fwd, x_rev)

        return x


class ConvertedBidirectionalBandLSTM(_ConvertedBidirectionalBandRNN):
    def __init__(
        self,
        block_input_size: int,
        num_blocks: int,
        block_hidden_size: int,
        bias: bool = True,
        dropout: float = 0,
    ):
        super().__init__(
            _BidirectionalBandLSTMLoop,
            block_input_size,
            num_blocks,
            block_hidden_size,
            bias,
            dropout,
        )

    def forward(self, x):
        x_fwd = x
        x_rev = self.band_reverse(x)

        for layer in self.layers:
            x_fwd, x_rev = layer(
                x_to_slice=[x_fwd, x_rev],
                x_recursed_init=[
                    self.zero_init,
                    self.zero_init,
                    self.zero_init,
                    self.zero_init,
                ],
                x_scope=[],
            )
            x = self.bidir_interleave(x_fwd, x_rev)

        return x
