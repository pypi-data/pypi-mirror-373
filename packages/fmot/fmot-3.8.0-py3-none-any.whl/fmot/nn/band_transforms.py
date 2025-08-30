import torch
from torch import nn, Tensor
from fmot.nn import Split, Cat, VVAdd, SuperStructure


class RaggedBlockDiagonal(SuperStructure):
    """
    Applies a ragged block-diagonal linear transformation.

    This module splits an input tensor into non-uniform subvectors (blocks),
    applies independent linear transformations to each block, and then concatenates
    the transformed results into a single output tensor. It effectively implements
    a block-wise linear operation with varying input and output sizes per block.

    This is useful for architectures where different parts of the input require
    different transformations, such as frequency-domain processing or multi-resolution
    representations.

    Args:
        block_in_channels (list[int]):
            A list specifying the input dimensions for each block.
        block_out_channels (list[int]):
            A list specifying the output dimensions for each block.
        bias (bool, optional):
            Whether to include a bias term in the linear layers. Defaults to ``False``.

    Example:
        .. code-block:: python

            import torch
            from fmot.nn import RaggedBlockDiagonal

            # Define block sizes
            block_in = [4, 8, 6]   # Three blocks of different sizes
            block_out = [3, 5, 2]  # Output dimensions for each block

            # Instantiate the layer
            layer = RaggedBlockDiagonal(block_in, block_out)

            # Generate dummy input with concatenated blocks
            batch_size, time_steps = 2, 10
            x = torch.randn(batch_size, time_steps, sum(block_in))  # (batch, time, total_input_dim)

            # Forward pass
            output = layer(x)
            print(output.shape)  # Expected: (batch, time, sum(block_out))

    Inputs:
        - A tensor of shape:

        .. code-block:: python

            (batch, time, sum(block_in_channels))

        where the last dimension represents concatenated blocks of varying sizes.

    Outputs:
        - A tensor of shape:

        .. code-block:: python

            (batch, time, sum(block_out_channels))

        containing the transformed, concatenated output blocks.

    Notes:
        - The lengths of ``block_in_channels`` and ``block_out_channels`` must be the same.
        - Each block undergoes an independent linear transformation.
        - This operation is conceptually equivalent to a block-diagonal matrix,
          but with ragged (non-uniform) block sizes.

    Raises:
        ValueError: If ``block_in_channels`` and ``block_out_channels`` have different lengths.
    """

    def __init__(
        self, block_in_channels: list[int], block_out_channels: list[int], bias=False
    ):
        super().__init__()
        self.block_in_channels = block_in_channels
        self.block_out_channels = block_out_channels

        self.lins = nn.ModuleList()
        for cin, cout in zip(block_in_channels, block_out_channels):
            self.lins.append(nn.Linear(cin, cout, bias=bias))

        self.split = Split(self.block_in_channels, dim=-1)
        self.cat = Cat(dim=-1)

    @torch.jit.ignore
    def forward(self, x):
        subs_in = self.split(x)
        subs_out = []
        for x, lin in zip(subs_in, self.lins):
            subs_out.append(lin(x))
        out = self.cat(subs_out)
        return out


class ToBands(SuperStructure):
    """
    A module that applies a ragged-block-diagonal transformation to each input source and sums the results.

    This module is useful for transforming frequency-domain representations (e.g., FFT coefficients)
    into a band-wise representation, with bandwidths following Bark, Mel, or any other frequency scale.

    Args:
        num_srcs (int):
            Number of input sources (e.g., 2 for the real and imaginary components of an STFT).
        n_fft (int):
            Number of input frequency channels per source (must be the same for all sources).
        num_bands (int):
            Number of frequency bands to create.
        d_band (int):
            Output dimensionality of each band (same for all bands).
        bandwidths (list[int]):
            A list specifying the bandwidths (in FFT bins) assigned to each band.
            Must sum to `n_fft` and have a length equal to `num_bands`.
        bias (bool, optional):
            Whether to use a bias term in the transformation. Defaults to ``True``.

    Example:
        Instantiating and using a ``ToBands`` module:

        .. code-block:: python

            import torch
            from fmot.nn import ToBands

            # Define parameters
            num_srcs = 2
            n_fft = 257
            num_bands = 8
            d_band = 64
            bandwidths = [2, 3, 4, 8, 16, 32, 64, 128]

            # Instantiate the layer
            to_bands = ToBands(num_srcs, n_fft, num_bands, d_band, bandwidths)

            # Generate dummy input: a list of 4 sources, each with shape (batch, time, n_fft)
            batch_size, time_steps = 2, 10
            inputs = [torch.randn(batch_size, time_steps, n_fft) for _ in range(num_srcs)]

            # Forward pass
            output = to_bands(inputs)
            print(output.shape)  # Expected: torch.Size([2, 10, num_bands * d_band])

    Inputs:
        A list of ``num_srcs`` tensors, each of shape:

        .. code-block:: python

            (batch, time, n_fft)

        These tensors represent the spectral representations of different sources.

    Outputs:
        A single tensor of shape:

        .. code-block:: python

            (batch, time, num_bands * d_band)

        This output contains the concatenated transformed bandwise representations.

    Raises:
        ValueError: If ``sum(bandwidths) != n_fft`` or ``len(bandwidths) != num_bands``.

    Notes:
        - The ``bandwidths`` list **must** sum to ``n_fft`` to ensure full spectral coverage.
        - The length of ``bandwidths`` **must** match ``num_bands`` to define each band's width.
        - Only the first source receives a bias term (if enabled).
    """

    def __init__(
        self,
        num_srcs: int,
        n_fft: int,
        num_bands: int,
        d_band: int,
        bandwidths: list[int],
        bias: bool = True,
    ):
        super().__init__()

        # a few quick checks:
        assert sum(bandwidths) == n_fft
        assert len(bandwidths) == num_bands

        self.blocked_lins = nn.ModuleList()
        for i in range(num_srcs):
            self.blocked_lins.append(
                RaggedBlockDiagonal(
                    bandwidths, [d_band] * num_bands, bias=(i == 0) and bias
                )
            )

        self.add = VVAdd()

    @torch.jit.ignore
    def forward(self, sources: list[Tensor]) -> Tensor:
        res = None
        for blin, src in zip(self.blocked_lins, sources):
            curr = blin(src)
            if res is None:
                res = curr
            else:
                res = self.add(res, curr)

        return res


class FromBands(SuperStructure):
    """
    Converts a band-wise representation back into a full-frequency representation.

    This module takes an input tensor where spectral features have been grouped into bands
    (e.g., Bark or Mel scales) and applies a learned transformation to reconstruct
    a full-frequency representation. Each source is processed separately using
    a block-wise transformation.

    This is the inverse operation of ``ToBands`` and can be used to reconstruct
    frequency-domain signals after processing in a bandwise format.

    Args:
        num_srcs (int):
            Number of output sources.
        n_fft (int):
            Number of frequency bins in the reconstructed representation.
        num_bands (int):
            Number of bands in the input representation.
        d_band (int):
            Dimensionality of each band (same for all bands).
        bandwidths (list[int]):
            A list specifying the bandwidths (in FFT bins) assigned to each band.
            Must sum to ``n_fft``.
        bias (bool, optional):
            Whether to use a bias term in the transformation. Defaults to ``True``.

    Example:
        Instantiating and using a ``FromBands`` module:

        .. code-block:: python

            import torch
            from fmot.nn import FromBands

            # Define parameters
            num_srcs = 2
            n_fft = 257
            num_bands = 8
            d_band = 64
            bandwidths = [2, 3, 4, 8, 16, 32, 64, 128]

            # Instantiate the layer
            from_bands = FromBands(num_srcs, n_fft, num_bands, d_band, bandwidths)

            # Generate dummy input of shape (batch, time, num_bands * d_band)
            batch_size, time_steps = 2, 10
            x = torch.randn(batch_size, time_steps, num_bands * d_band)

            # Forward pass
            outputs = from_bands(x)
            print(len(outputs))  # Expected: num_srcs
            print(outputs[0].shape)  # Expected: (batch, time, n_fft)

    Inputs:
        - A single tensor of shape:

        .. code-block:: python

            (batch, time, num_bands * d_band)

        representing the band-wise processed signal.

    Outputs:
        - A list of ``num_srcs`` tensors, each of shape:

        .. code-block:: python

            (batch, time, n_fft)

        where each tensor represents a reconstructed full-frequency source.

    Notes:
        - The ``bandwidths`` list **must** sum to ``n_fft`` to ensure complete reconstruction.
        - The number of elements in ``bandwidths`` **must** equal ``num_bands``.
        - This is the inverse operation of ``ToBands`` and should ideally be used in conjunction with it.

    Raises:
        ValueError: If ``sum(bandwidths) != n_fft`` or ``len(bandwidths) != num_bands``.
    """

    def __init__(
        self,
        num_srcs: int,
        n_fft: int,
        num_bands: int,
        d_band: int,
        bandwidths: list[int],
        bias: bool = True,
    ):
        super().__init__()

        # a few quick checks:
        assert sum(bandwidths) == n_fft
        assert len(bandwidths) == num_bands

        self.blocked_lins = nn.ModuleList()
        for i in range(num_srcs):
            self.blocked_lins.append(
                RaggedBlockDiagonal([d_band] * num_bands, bandwidths, bias=bias)
            )

    def forward(self, x: Tensor) -> list[Tensor]:
        out = []
        for blin in self.blocked_lins:
            out.append(blin(x))
        return out
