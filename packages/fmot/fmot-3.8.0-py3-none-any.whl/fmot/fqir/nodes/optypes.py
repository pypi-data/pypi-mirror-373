"""Defines the FQIR Atomic Operator Registry V1"""
import numpy as np
from .optype_base import OpType, OpRegistry
from .node_base import NodeReprSettings
import math
from .opcounters import (
    VVCounter,
    VCounter,
    ConvCounter,
    MatmulCounter,
    VLUTCounter,
    NullCounter,
    CopyCounter,
    ShiftCounter,
    ReductionCounter,
)
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

ST_LD_pessimism = 0.5
B_ACC_ENTRY = 32


def lshift(x, shamt):
    """Performs a left-shift on x

    Args:
        x (:obj:`numpy.ndarray`): Integer numpy array
        shamt (int): Shift amount (can be negative for right shift)
    """
    if shamt >= 0:
        return x << shamt
    else:
        try:
            return x >> -shamt
        except:
            raise Exception(f"in >>: {type(x)=} {type(shamt)=} {x.dtype=}")


def rounded_lshift(x, shamt, rounded):
    """Performs a left-shift on x

    Args:
        x (:obj:`numpy.ndarray`): Integer numpy array
        shamt (int): Shift amount (can be negative for right shift)
        rounded (bool): If True, rounds output to the nearest before shifting
    """
    if shamt >= 0:
        acc_init = 0
    else:
        if rounded:
            acc_init = 2 ** (-shamt - 1)  # Initial value of the accumulator
        else:
            acc_init = 0
    return lshift(acc_init + x, shamt)


def truncate(x, bw):
    """Truncate an integer tensor to a certain bitwidth"""
    vmin = -(2 ** (bw - 1))
    vmax = 2 ** (bw - 1) - 1
    return np.clip(x, vmin, vmax)


def split_to_subprecisions(x: np.ndarray, bws: list[int]):
    """
    Splits a higher-precision integer array into multiple lower-precision integer arrays,
    where each lower-precision array represents a segment of the bits of the higher-precision array.
    The segments are defined by the bit widths specified in `bws` and are extracted from least
    significant bits to most significant bits.

    The lower-precision arrays together can reconstruct the original higher-precision array.

    Arguments:
        x (np.ndarray): A NumPy array of signed integers representing the higher-precision numbers to be split.
        bws (list[int]): A list of bit widths for each segment, from least significant bits to most significant bits.

    Returns:
        List[np.ndarray]: A list of NumPy arrays, each containing signed integers of the
        corresponding bit width in `bws`.
    """
    outs = []
    shamt = 0

    # pre-saturate x to the sum of the bitwidths
    tot_bw = sum(bws) - len(bws) + 1
    x = truncate(x, tot_bw)

    x_uint = x.astype(np.uint64)

    # Each child-bw array contains its own sign bit, which we effectively ignore
    # by extracting bw - 1 bits before appending the values to outs. For the MSB segment,
    # we also extract the full bw bits, but this time, the MSB's sign bit serves as the
    # sign for the entire original value.

    for bw in bws[:-1]:
        # Extract the lower `bw` bits
        mask = np.uint64((1 << (bw - 1)) - 1)
        curr = (x_uint >> np.uint64(shamt)) & mask
        outs.append(curr.astype(np.int64))
        shamt += bw - 1

    # upper bits (more care to correctly establish the sign bit)
    bw = bws[-1]
    mask = np.uint64((1 << bw) - 1)
    curr = (x_uint >> np.uint64(shamt)) & mask
    sign_bit = 1 << (bw - 1)
    curr_signed = np.where(curr >= sign_bit, curr - (1 << bw), curr)
    outs.append(curr_signed.astype(np.int64))

    return outs


def _add(x, y, rounded, shamt_x, shamt_y, shamt_bwred, bw, sub=False):
    """Add two vectors together

    Args:
        x: First addend
        y: Second addend
        shamt_x: Left-shift-amount for x before adding
        shamt_y: Left-shift-amount for y before adding
        shamt_bwred: Left-shift-amount for resultant
        bw: Bitwidth of output
        bw_x: bitwidth of x
        bw_y: bitwidth of y
    """
    if isinstance(x, np.ndarray):
        x = x.astype(np.int64)
    if isinstance(y, np.ndarray):
        y = y.astype(np.int64)
    x = lshift(x, shamt_x)
    y = lshift(y, shamt_y)
    if sub:
        z_buff = x - y
    else:
        z_buff = x + y
    z_bwred = truncate(rounded_lshift(z_buff, shamt_bwred, rounded), bw)
    z_bwred = z_bwred.astype(np.int32)
    return z_bwred


class GMACv2(OpType):
    """General MAC (see design document: https://docs.google.com/document/d/1yKsixx42Fss7mNLFJyCihiLJJLHltsZF_Ba18BGWZ4Q/)
    with arbitrary output precision decomposition

    Defines a sequence of accumulated vector-vector and vector-immediate products.
    Without shamt-grouping (more on this later), and with `compute_lsbs=False`,
    the definition of this operation is:

    ARITHMETIC PART (build up the final accumulator state):
        acc = (
                (x_vv_0 * y_vv_0) >> shamts_vv[0] +
                (x_vv_1 * y_vv_1) >> shamts_vv[1] +
                ...
                (x_vi_0 * immediates_vi_0) >> shamts_vi[0] +
                (x_vi_1 * immediates_vi_1) >> shamts_vi[1] +
                ...
            )

    Then, decompose this accumulator value into multiple output tensors z[i], each with precision `bits_out[i]`

    See the design document for a definition of shamt-ordering.
    """

    def __init__(self):
        super().__init__(
            name="gmac_v2",
            inputs=["kwargs"],
            constants=["shamts_vv", "shamts_vi", "immediates_vi", "bits_out"],
            repr_settings=NodeReprSettings(
                # operator_symbol='+',
                use_var_names=True
            ),
            opcounter=VVCounter(op="add"),
            can_bcast_in=True,
        )

    def runtime(self, shamts_vv, shamts_vi, immediates_vi, bits_out, **kwargs):
        """Performs a General MAC (GMAC)

        Runtime Signature:
            vvadd(shamts_vv: List[int], shamts_vi: List[int], immediates_vi: List[int], compute_lsbs: bool, **kwargs)

            where kwargs carries an arbitrary number of x_vv_{i}, y_vv_{i} pairs for vector-vector multiplies
            and an arbitrary number of x_vi_{i} for vector-immediate multiplies.

        Constraints:
            - N_vv: number of x_vv_{i}, y_vv_{i} tensor arguments must match, and should be equal to len(shamts_vv)
            - N_vi: number of x_vi_{i} tensor arguments must be equal to len(shamts_vi) and len(immediates_vi)

        See https://docs.google.com/document/d/1yKsixx42Fss7mNLFJyCihiLJJLHltsZF_Ba18BGWZ4Q/ for a description of shamt-ordering
        and an explanation of how lsb-calculation is performed. In the `compute_lsbs=False` and without shamt-ordering, the operation is:

        output = (
            (x_vv_0 * y_vv_0) >> shamts_vv[0] +
            (x_vv_1 * y_vv_1) >> shamts_vv[1] +
            ...
            (x_vi_0 * immediates_vi_0) >> shamts_vi[0] +
            (x_vi_1 * immediates_vi_1) >> shamts_vi[1] +
            ...
        )

        """
        # unpack input tensors
        xs_vv = []
        ys_vv = []
        xs_vi = []
        i = 0
        while f"x_vv_{i}" in kwargs:
            xs_vv.append(kwargs[f"x_vv_{i}"])
            ys_vv.append(kwargs[f"y_vv_{i}"])
            i += 1

        i = 0
        while f"x_vi_{i}" in kwargs:
            xs_vi.append(kwargs[f"x_vi_{i}"])
            i += 1

        n_args_vv = len(shamts_vv)
        assert len(xs_vv) == n_args_vv
        n_args_vi = len(shamts_vi)
        assert len(immediates_vi) == n_args_vi
        assert len(xs_vi) == n_args_vi, f"{len(xs_vi)=}, {n_args_vi=}, {self=}"

        xs = xs_vv + xs_vi
        ys = ys_vv + immediates_vi
        shamts = shamts_vv + shamts_vi

        shamts = np.array(shamts)

        def _run_macs(shamts, prefix="acc"):
            idx_order = np.argsort(shamts)

            acc = 0
            prev_shamt = None
            shamt = None
            for n, i in enumerate(idx_order):
                shamt = shamts[i]
                if prev_shamt is not None:
                    dshamt = prev_shamt - shamt
                    if dshamt != 0:
                        acc = lshift(acc, dshamt)
                prev_shamt = shamt
                acc += xs[i] * ys[i]
            if shamt is not None:
                acc = lshift(acc, shamt)
            return acc

        acc = _run_macs(shamts, "acc")

        # Splits a higher-precision integer array into multiple lower-precision integer arrays,
        # where each lower-precision array represents a segment of the bits of the higher-precision array.
        outputs = tuple(split_to_subprecisions(acc, bits_out))
        return outputs


class VVADD(OpType):
    def __init__(self):
        super().__init__(
            name="vvadd",
            inputs=["x", "y"],
            constants=[
                "rounded",
                "shamt_x",
                "shamt_y",
                "shamt_bwred",
                "bw",
                "bw_x",
                "bw_y",
            ],
            repr_settings=NodeReprSettings(
                # operator_symbol='+',
                use_var_names=False
            ),
            opcounter=VVCounter(op="add"),
            can_bcast_in=True,
        )

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y, rounded=False):
        """Add two vectors together

        Runtime Signature:
            vvadd(x, y)

        Arguments:
            x: First addend
            y: Second addend
        Constants:
            shamt_x: Left-shift-amount for x before adding
            shamt_y: Left-shift-amount for y before adding
            shamt_bwred: Left-shift-amount for resultant
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Addends are decimal aligned (by integer shift and truncation)
            2. Decimal-aligned addends are added together
            3. Result of adding is bitwidth reduced (by integer shift and truncation)

        """
        return _add(x, y, rounded, shamt_x, shamt_y, shamt_bwred, bw, sub=False)


class VIADD(OpType):
    def __init__(self):
        super().__init__(
            name="viadd",
            inputs=["x"],
            constants=[
                "y",
                "shamt_x",
                "shamt_y",
                "shamt_bwred",
                "bw",
                "bw_x",
                "bw_y",
                "rounded",
            ],
            opcounter=VCounter(op="add"),
            repr_settings=NodeReprSettings(
                # operator_symbol='+',
                use_var_names=False,
                constants_to_rep=["y"],
            ),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y, rounded=False):
        """Add a vector to an immediate

        Runtime Signature:
            viadd(x)
        Arguments:
            x: Vector addend
        Constants:
            y: Immediate addend (stored as an integer)
            shamt_x: Left-shift-amount for x before adding
            shamt_y: Left-shift-amount for y (immediate) before adding
            shamt_bwred: Left-shift-amount for resultant
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Addends are decimal aligned (by integer shift and truncation)
            2. Decimal-aligned addends are added together
            3. Result of adding is bitwidth reduced (by integer shift and truncation)
        """
        return _add(x, y, rounded, shamt_x, shamt_y, shamt_bwred, bw, sub=False)


class VVSUB(OpType):
    def __init__(self):
        super().__init__(
            name="vvsub",
            inputs=["x", "y"],
            constants=[
                "shamt_x",
                "shamt_y",
                "shamt_bwred",
                "bw",
                "bw_x",
                "bw_y",
                "rounded",
            ],
            opcounter=VVCounter(op="add"),
            repr_settings=NodeReprSettings(
                # operator_symbol='-',
                use_var_names=False
            ),
            can_bcast_in=True,
        )

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y, rounded=False):
        """Subtracts one vector from another

        Runtime Signature:
            vvsub(x, y)

        Arguments:
            x: First argument
            y: Second argument (to be subtracted)
        Constants:
            shamt_x: Left-shift-amount for x before subtracting
            shamt_y: Left-shift-amount for y before subtracting
            shamt_bwred: Left-shift-amount for resulting difference
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Operands are decimal aligned (by integer shift and truncation).
            2. Decimal-aligned operands are subtracted.
            3. Resulting difference is bitwidth reduced (by integer shift and truncation).

        """
        return _add(x, y, rounded, shamt_x, shamt_y, shamt_bwred, bw, sub=True)


class VNEG(OpType):
    def __init__(self):
        super().__init__(
            name="vneg",
            inputs=["x"],
            constants=["bw"],
            opcounter=VCounter(op="add"),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, bw):
        """Multiply a vector by -1

        Runtime Signature:
            vneg(x)
        Arguments:
            x: Vector to be negated
        Constants:
            bw: Bitwidth of x and output

        Description:
            1. Input is negated
            2. Output is truncated
                Truncation can produce off-by-1s from mathematically expected at the negative extrema
                because of asymmetry the signed representation. For example, in 8bits, -128 negates to
                127 after trunction.
        """
        return truncate(-x, bw)


def _mul(x, y, rounded, shamt_bwred, bw):
    """Multiplies two vectors element-wise

    Args:
        x: First argument
        y: Second argument
        round_output: If True, rounds output to the nearest before shifting
        shamt_bwred: Left-shift-amount for resulting product
        bw: Bitwidth of output
    """
    if isinstance(x, np.ndarray):
        x = x.astype(np.int64)
    if isinstance(y, np.ndarray):
        y = y.astype(np.int64)
    z_buff = x * y
    z_bwred = truncate(rounded_lshift(z_buff, shamt_bwred, rounded=rounded), bw)
    z_bwred = z_bwred.astype(np.int32)
    return z_bwred


class VVMUL(OpType):
    def __init__(self):
        super().__init__(
            name="vvmul",
            inputs=["x", "y"],
            constants=["rounded", "shamt_bwred", "bw"],
            opcounter=VVCounter(op="mul"),
            repr_settings=NodeReprSettings(
                # operator_symbol='*',
                use_var_names=False
            ),
            can_bcast_in=True,
        )

    @staticmethod
    def runtime(x, y, shamt_bwred, bw, rounded=False):
        """Multiplies two vectors element-wise

        Runtime Signature:
            vvmul(x, y)
        Arguments:
            x: First argument
            y: Second argument
        Constants:
            rounded: If True, rounds output to the nearest before shifting
            shamt_bwred: Left-shift-amount for resulting product
            bw: Bitwidth of output

        Description:
            1. Operands are multipled
            2. Resulting product is left-shifted and truncated to bw
        """
        return _mul(x, y, rounded, shamt_bwred, bw)


class VIMUL(OpType):
    def __init__(self):
        super().__init__(
            name="vimul",
            inputs=["x"],
            constants=["y", "shamt_bwred", "bw", "rounded"],
            opcounter=VCounter(op="mul"),
            repr_settings=NodeReprSettings(
                # operator_symbol='*',
                constants_to_rep=["y"],
                use_var_names=False,
            ),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, y, shamt_bwred, bw, rounded=False):
        """Multiplies a vectors element-wise with an immediate

        Runtime Signature:
            vimul(x)
        Arguments:
            x: Operand
        Constants:
            y: Immediate (represented as an integer)
            shamt_bwred: Left-shift-amount for resulting product
            bw: Bitwidth of output

        Description:
            1. Operand is element-wise multipled with the immediate
            2. Resulting product is left-shifted and truncated to bw
        """
        x = x.astype(np.int32)
        return _mul(x, y, rounded=rounded, shamt_bwred=shamt_bwred, bw=bw)


class MATMUL(OpType):
    def __init__(self):
        super().__init__(
            name="matmul",
            inputs=["x", "y"],
            constants=["rounded", "shamt_bwred", "bw_out"],
            opcounter=MatmulCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, y, shamt_bwred, bw_out, rounded=False):
        """Matrix product

        Runtime Signature:
            matmul(x, y)
        Arguments:
            x: First argument
            y: Second argument
        Constants:
            rounded: If True, rounds output to the nearest before shifting
            shamt_bwred: Left-shift-amount for resulting product
            bw_out: Bitwidth of output

        Description:
            1. Matmul between input operands
            2. Resulting product is left-shifted and truncated
        """
        x = x.astype(np.int64)
        y = y.astype(np.int64)
        z_buff = x @ y
        z_bwred = truncate(rounded_lshift(z_buff, shamt_bwred, rounded=rounded), bw_out)
        z_bwred = z_bwred.astype(np.int32)
        return z_bwred


class ADDMM(OpType):
    def __init__(self):
        super().__init__(
            name="addmm",
            inputs=["bias", "x", "y"],
            constants=["rounded", "shamt_bias", "shamt_bwred", "bw_out"],
            opcounter=MatmulCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(
        bias: np.ndarray,
        x: np.ndarray,
        y: np.ndarray,
        shamt_bias,
        shamt_bwred,
        bw_out,
        rounded=False,
    ):
        """Matrix product with bias

        Runtime Signature:
            addmm(bias, mat1, mat2)
        Arguments:
            bias: constant vector to add to the product
            x: first matmul operand
            y: second matmul operand
        Constants:
            rounded: If True, rounds bias and output
            shamt_bias: left-shift-amount for bias, for shift without accumulation (step 1.)
            shamt_bwred: left-shift-amount for resulting product
            bw_out: output bitwidth

        Description:
            1. Bias is shifted (without truncation) to match the scale of the
                accumulating buffer (scale_buffer = scale_mat1 * scale_mat2)
            2. The matrix-vector product between mat1 and mat2 is accumulated into the
                buffer, on top of the bias
            3. Resulting product is left-shifted and truncated
        """

        x = x.astype(np.int64)
        y = y.astype(np.int64)
        buff = x @ y

        if bias.ndim == 1 and buff.ndim != 1:
            bias = bias.astype(np.int64)
            bias = bias.reshape(-1, *[1] * (buff.ndim - 1))
        buff = buff + truncate(
            rounded_lshift(bias, shamt_bias, rounded=rounded), B_ACC_ENTRY
        )
        z = truncate(rounded_lshift(buff, shamt_bwred, rounded=rounded), bw_out)
        z = z.astype(np.int32)
        return z


class RELU(OpType):
    def __init__(self):
        super().__init__(
            name="relu",
            inputs=["x"],
            constants=[],
            opcounter=VCounter(op=None, sparse_out=True),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x):
        """Element-wise rectified nonlinearity on the input vector

        Runtime Signature:
            relu(x)
        Arguments:
            x: Input

        Description:
            Relu clamps negative values to zero, and leaves positive entries unchanged.
                relu(x) = x * {x > 0}
            Because relu does not have an effect on the quantization scale, it does not involve any
            shamt constants.
        """
        return np.clip(x, 0, None)


class LUT(OpType):
    def __init__(self):
        super().__init__(
            name="lut",
            inputs=["x"],
            constants=["shamt_address", "bw_address", "table", "function"],
            opcounter=VLUTCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=["function"]),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, shamt_address, bw_address, table, function):
        """Performs an elementwise lookup table based nonlinearity on the input vector.

        Runtime Signature:
            lut(x)
        Arguments:
            x: Input
        Constants:
            shamt_address: Left-shift amount for truncating input to address bitwidth
            bw_address: Bitwidth of the LUT address space. Used during address truncation.
            table: An fmot.qat.nn.Table object. table.x is an integer array of input addresses.
                table.y is an integer array of output values.
            function: String, name of the function. Not used during computation, just a useful
                annotation.

        Description:
            1. Input vector is bitwidth-reduced to match the bitwidth of the LUT's address space
               This is done with a truncating left-shift, parametrized by `shamt_address` and
               `bits_address`. The LSBs up to `bw_address` are used during truncation.
            2. Outputs are generated element-by-element by querying the table with the truncated
               input values.
        """
        address = truncate(lshift(x, shamt_address), bw_address) - np.min(table.x)
        z = table.y[address]
        return z


class TRANSPOSE(OpType):
    def __init__(self):
        super().__init__(
            name="transpose",
            inputs=["x"],
            constants=["dim0", "dim1"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, dim0, dim1):
        """Performs a (hopefully) virtual transpose on a matrix.

        Runtime Signature:
            transpose(x)
        Arguments:
                x: input

        Description:
            The last two dimensions in a tensor are permuted.
            A matrix M that is row-major will be indexed as:
                (row_index, column_index) such that M[i, j] will be the entry in row-i and column-j.
            The matrix W = TRANSPOSE(M) will be column-major, with indexing as:
                (column_index, row_index) such that M[i,j] = W[j, i]
            If a tensor only has 1 dimension, this operation is identity
        """
        if x.ndim >= 2:
            y = np.transpose(x, (max(dim0, dim1), min(dim0, dim1)))
            return y
        else:
            return x


class RESHAPE(OpType):
    def __init__(self):
        super().__init__(
            name="reshape",
            inputs=["x"],
            constants=["shape"],
            opcounter=NullCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=["shape"]),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, shape):
        """Reshape the input tensor

        Runtime Signature:
            reshape(x)
        Arguments:
            x: The tensor to be reshaped
        Constants:
            shape: the shape for the new tensor

        Description:
            Returns a tensor with same data but with the specified shape.
        """
        return np.reshape(x, shape)


class QUANTIZE(OpType):
    def __init__(self):
        super().__init__(
            name="quantize",
            inputs=["x"],
            constants=["quanta", "bw"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x: np.ndarray, quanta, bw):
        """Convert a floating-point tensor into a quantized integer tensor, according to:

        Runtime Signature:
            quantize(x)
        Arguments:
            x: Input
        Constants:
            quanta: Integer quanta, related to scale as scale = 2**quanta
            bw: Integer bitwidth

        Description:
            If the input is already an integer np array, apply a check to ensure that
            the input is in range.

            If the input is a float:
                1. Divide input by scale = 2**quanta
                2. Floor
                3. Clip between -2**(bitwidth-1), 2**(bitwidth-1) - 1
        """
        boundaries = -(2 ** (bw - 1)), 2 ** (bw - 1) - 1
        if np.issubdtype(x.dtype, np.integer):
            assert np.all(np.logical_and(x >= boundaries[0], x <= boundaries[1]))
            return x.astype(int)
        else:
            scale = 2**quanta
            z = np.clip(np.floor(x / scale), *boundaries)
            z = z.astype(int)
            return z


class DEQUANTIZE(OpType):
    def __init__(self):
        super().__init__(
            name="dequantize",
            inputs=["x"],
            constants=["quanta"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, quanta):
        """Convert an integer tensor into a rounded floating-point tensor

        Runtime Signature:
            dequantize(x)
        Arguments:
            x: Onput
        Constants:
            quanta: Integer quanta, related to scale as scale = 2**quanta

        Description:
            1. Cast integer input to floating point
            2. Multiply by scale = 2**quanta
        """
        scale = 2**quanta
        x = x.astype(float)
        return x * scale


class CHUNK(OpType):
    def __init__(self):
        super().__init__(
            name="chunk",
            inputs=["x"],
            constants=["chunks", "dim"],
            opcounter=CopyCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, chunks, dim):
        """Split a tensor into a tuple of `chunks` tensors along a dimension `dim`.

        Runtime Signature:
            chunk(x)
        Arguments:
            x: Input
        Constants:
            chunks: Number of chunks
            dim: Dimension to split

        Description:
            Tensor dimension `dim` is evenly divided into `chunks` equal-length segments.
        """
        return tuple(np.array_split(x, chunks, dim))


class SPLIT(OpType):
    def __init__(self):
        super().__init__(
            name="split",
            inputs=["x"],
            constants=["lengths", "dim"],
            opcounter=CopyCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, lengths, dim):
        """Split a tensor into a tuple of tensors along a dimension `dim`.

        Runtime Signature:
            split(x)
        Arguments:
            x: Input
        Constants:
            lengths (list[int]): lengths of each split
            dim: Dimension to split

        Description:
            Tensor dimension `dim` is divided into segments, with lengths given by `lengths`.
        """

        outputs = []
        curr = 0
        for l in lengths:
            outputs.append(x[curr : curr + l])
            curr += l
        return tuple(outputs)


class CAT(OpType):
    def __init__(self):
        super().__init__(
            name="cat",
            inputs=["kwargs"],
            constants=["dim"],
            opcounter=CopyCounter(),
            repr_settings=NodeReprSettings(use_var_names=False),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(dim, **kwargs):
        """Concatenate tensors along `dim`, in order.

        Runtime Signature:
            cat(x0, x1, x2, ...)
        Arguments:
            x0, x1, ... : Variable number of input vectors to concatenate in index-order.
                Names must start with 'x0' and increment
        Constants:
            dim: Dimension to concatenate
        """
        to_cat = []
        i = 0
        while f"x{i}" in kwargs:
            to_cat.append(kwargs[f"x{i}"])
            i += 1
        return np.concatenate(to_cat, axis=dim)


class STACK(OpType):
    def __init__(self):
        super().__init__(
            name="stack",
            inputs=["kwargs"],
            constants=["dim"],
            opcounter=CopyCounter(),
            repr_settings=NodeReprSettings(use_var_names=False),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(dim, **kwargs):
        """Stack tensors along dim

        Runtime Signature:
            stack(x0, x1, x2, ...)
        Arguments:
            x0, x1, ... : Variable number of input vectors to stack in index-order
                Names must start with 'x0' and increment
        Constants:
            dim: Dimension to stack
        """
        to_stack = []
        i = 0
        while f"x{i}" in kwargs:
            to_stack.append(kwargs[f"x{i}"])
            i += 1
        return np.stack(to_stack, axis=dim)


class SQUEEZE(OpType):
    def __init__(self):
        super().__init__(
            name="squeeze",
            inputs=["x"],
            constants=["dim"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, dim):
        raise NotImplementedError


class ZEROS(OpType):
    def __init__(self):
        super().__init__(
            name="zeros",
            inputs=[],
            constants=["shape"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(shape):
        """Init a zeros vector of shape `shape`

        Runtime Signature:
            zeros()
        Constants:
            shape (tuple): Shape of zeros vector
        """
        return np.zeros(shape).astype(int)


class CONSTANT(OpType):
    def __init__(self):
        super().__init__(
            name="constant",
            inputs=[],
            constants=["shape", "value"],
            opcounter=NullCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=["value"]),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(shape, value):
        """Init a constant vector of shape `shape`

        Runtime Signature:
            zeros()
        Constants:
            shape (tuple): Shape of vector
            value (int): constant value for tensor
        """
        return np.ones(shape).astype(int) * value


class ASSIGN(OpType):
    def __init__(self):
        super().__init__(
            name="assign",
            inputs=["y", "x"],
            constants=[],
            opcounter=CopyCounter(),
            can_bcast_in=False,
        )

    def runtime(self, y, x):
        """Assign y to hold the value stored by x (i.e. y = x)

        Runtime Signature:
            assign(y, x)
        Arguments:
            y: Variable to copy to
            x: Variable to copy from
        """
        return {self._inputs["y"].name: x}


class TEMPORAL_UNFOLD_UNKERNELIZED(OpType):
    def __init__(self):
        super().__init__(
            name="temporal_unfold_unkernelized",
            inputs=["x"],
            constants=["kernel_size", "dilation", "buffer_length", "stride"],
            opcounter=NullCounter(),
            can_bcast_in=False,
            repr_settings=NodeReprSettings(
                constants_to_rep=["kernel_size", "stride", "dilation"]
            ),
        )

    def runtime(self, x, kernel_size, dilation, buffer_length, stride):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Returns a concatenation of the in-frame vectors
        at each time-step.

        Runtime Signature:
            temporal_unfold(x, buffer)

        Arguments:
            x: new input frame
            buffer: not added here -- will be added after kernelization
        Constants:
            kernel_size: kernel size of sliding window
            dilation: dilation of sliding window
            buffer_length: number of vectors stored in buffer
            stride: stride for the unfold operation
        """
        pass


class TEMPORAL_TRANSPOSE_FOLD_UNKERNELIZED(OpType):
    def __init__(self):
        super().__init__(
            name="temporal_transpose_fold_unkernelized",
            inputs=["x"],
            constants=["kernel_size", "dilation", "stride"],
            opcounter=NullCounter(),
            can_bcast_in=False,
            repr_settings=NodeReprSettings(
                constants_to_rep=["kernel_size", "stride", "dilation"]
            ),
        )

    def runtime(self, x, kernel_size, dilation, stride):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Returns tranpose fold 1d of the input sequence.

        Runtime Signature:
            temporal_transpose_fold_unkernelized(x, ...)

        Arguments:
            x: new input frame
        Constants:
            kernel_size: kernel size of sliding window
            dilation: dilation of sliding window
            stride: stride for the fold operation
        """
        pass


class TEMPORAL_UNFOLD(OpType):
    def __init__(self):
        super().__init__(
            name="temporal_unfold",
            inputs=["x", "buffer"],
            constants=["kernel_size", "dilation", "buffer_length"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    def runtime(self, x, buffer, kernel_size, dilation, buffer_length):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Returns a concatenation of the in-frame vectors
        at each time-step.

        Runtime Signature:
            temporal_unfold(x, buffer)

        Arguments:
            x: new input frame
            buffer: stateful buffer storing past frames
        Constants:
            kernel_size: kernel size of sliding window
            dilation: dilation of sliding window
            buffer_length: number of vectors stored in buffer
        """
        buffer = np.concatenate([buffer, x])
        buffer = buffer.reshape(-1, len(x))
        outs = buffer[::dilation]
        outs = outs.flatten()
        buffer = buffer[1:].flatten()

        return {self._outputs[0].name: outs, self._inputs["buffer"].name: buffer}


class TEMPORAL_CONV2D(OpType):
    def __init__(self):
        super().__init__(
            name="temporal_conv2d",
            inputs=["input", "buffer", "weight", "bias"],
            constants=[
                "kernel_size_t",
                "kernel_size_band",
                "d_band_in",
                "n_band_in",
                "dilation_t",
                "dilation_band",
                "stride_band",
                "padding_band",
                "groups",
                "shamt_bwred",
                "shamt_bias",
                "bw",
            ],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    def runtime(
        self,
        input,
        weight,
        kernel_size_t,
        kernel_size_band,
        d_band_in,
        n_band_in,
        dilation_t,
        dilation_band,
        stride_band,
        padding_band,
        groups,
        shamt_bwred,
        shamt_bias,
        bw,
        bias=None,
        buffer=None,
    ):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Applies a temporal conv2d to the buffered state.

        kernel_types:
         - "matrix" if groups = 1
         - "depthwise" if groups == d_band_in
         - unsupported otherwise
        """
        d_band_out = weight.shape[0]
        if groups == 1:
            kernel_type = "matrix"
        elif groups == d_band_in and groups == d_band_out:
            kernel_type = "depthwise"
        else:
            raise NotImplementedError(
                f"{groups = }, {d_band_in = }, {d_band_out = } combination not supported in TEMPORAL_CONV2D"
            )

        assert stride_band >= 1

        assert len(input) == d_band_in * n_band_in

        # update buffer, extract relevant state for this time-step
        if buffer is not None:
            buffer = np.concatenate([buffer, input])
            buffer = buffer.reshape(-1, len(input))
            state = buffer[::dilation_t]
            assert state.shape[0] == kernel_size_t
            buffer = buffer[1:].flatten()
        else:
            assert kernel_size_t == 1
            state = input.reshape(1, -1)

        # state: shape (kernel_size_t, n_band_in * d_band_in)
        # reshape and pad...
        state = state.reshape(kernel_size_t, n_band_in, d_band_in)
        # apply padding
        state = np.pad(state, pad_width=[(0, 0), (padding_band, padding_band), (0, 0)])
        # shape: (kernel_size_t, n_band_in+2*padding, d_band_in)

        # apply the conv2d over "state"
        n_idxs = np.arange(kernel_size_band) * dilation_band
        outs = []
        while np.max(n_idxs) < n_band_in + 2 * padding_band:
            if bias is None:
                out = 0
            else:
                out = lshift(bias, shamt_bias)
            for kt in range(kernel_size_t):
                for kn, n_idx in enumerate(n_idxs):
                    w = weight[:, :, kn, kt]
                    x_tn = state[kt, n_idx]
                    if kernel_type == "matrix":
                        # w.shape: [d_band_out, d_band_in]
                        out += w @ x_tn
                    elif kernel_type == "depthwise":
                        # w.shape: [d_band_out, 1]
                        out += w[:, 0] * x_tn
                    else:
                        # shouldn't end up here
                        raise Exception(f"{kernel_type=} not recognized")

            out = truncate(rounded_lshift(out, shamt_bwred, rounded=False), bw)
            outs.append(out)

            n_idxs += stride_band

        output = np.concatenate(outs, axis=0)

        if buffer is not None:
            return {self._outputs[0].name: output, self._inputs["buffer"].name: buffer}
        else:
            return output


class SUM(OpType):
    def __init__(self):
        super().__init__(
            name="sum",
            inputs=["x"],
            constants=["dim", "keepdim", "shamt_bwred", "bw"],
            opcounter=ReductionCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, dim, keepdim, shamt_bwred, bw):
        """Sum the elements of x along a dim

        Runtime Signature:
            sum(x)
        Arguments:
            x: Input
        Constants:
            dim (int or List[int]): Dimension(s) to reduce
            keepdim (bool): Whether output has "dim" retained
            shamt_bwred (int): Left-shift-amount for resultant sum
            bw: Output bitwidth

        Description:
            1. Accumulate entries along dimension(s) "dim"
            2. Reduce bitwidth with a saturating left-shift according to "shamt_bwred"
        """
        z = np.sum(x, axis=dim, keepdims=keepdim)
        return truncate(lshift(z, shamt_bwred), bw)


class CONSTANT_LIKE(OpType):
    def __init__(self):
        super().__init__(
            name="constant_like",
            inputs=["x"],
            constants=["imm"],
            opcounter=CopyCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, imm):
        """Return a tensor of the same shape as the input, filled with constant "imm".

        Runtime Signature:
            constant_like(x)
        Arguments:
            x: Input
        Constants:
            imm: Integer immediate with which to fill the vector
        """
        return np.ones_like(x) * imm


class COPY(OpType):
    def __init__(self):
        super().__init__(
            name="copy",
            inputs=["x"],
            constants=[],
            opcounter=CopyCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x):
        """Copies a tensor

        Runtime Signature:
            copy(x)
        Arguments:
            x: Input
        """
        return x


class SHIFT(OpType):
    def __init__(self):
        super().__init__(
            name="shift",
            inputs=["x"],
            constants=["shamt", "bw", "rounded"],
            opcounter=ShiftCounter(),
            repr_settings=NodeReprSettings(
                # operator_symbol='<<',
                constants_to_rep=["shamt"],
                use_var_names=False,
            ),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, shamt, bw, rounded=False):
        """Shift and saturate a vector

        Runtime Signature:
            shift(x)
        Arguments:
            x: Input
        Constants:
            shamt: Left-shift amount
            bw: Output bitwidth

        Description:
            Applies a saturating integer shift to a tensor. May also change the bitwidth/datatype.
        """
        return truncate(rounded_lshift(x, shamt, rounded=rounded), bw)


class GT0(OpType):
    def __init__(self):
        super().__init__(
            name="gt0",
            inputs=["x"],
            constants=["bw"],
            opcounter=VCounter(op=None),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, bw):
        """Elementwise greater than zero. Returns a masking tensor of 0/1's.

        Runtime Signature:
            gt0(x)
        Arguments:
            x: Input
        Constants:
            bw: The output bitwidth, decides what the shift-amounts should be.
                With bw=<BW>, the pseudo-fqir is:
                    x1: fqint<BW> = relu(x=x0)
                    x2: fqint<BW> = shift[shamt=<BW>-1, bw=<BW>](x=x1)
                    x3: fqint<BW> = shift[shamt=-<BW>+1, bw=<BW>](x=x2)

        Description:
            This operation is equivalent to the following (in pseudo-fqir):
                x1: fqint8 = relu(x=x0)
                x2: fqint8 = shift[shamt=7, bw=8](x=x1)
                x3: fqint8 = shift[shamt=-7, bw=8](x=x2)
            The first shift saturates the output of the relu so that the vector elements are either 0
            or 125. The second shift results in elements that are either 0 or 1.
        """
        return (x > 0).astype(int)


class PRINT(OpType):
    def __init__(self):
        super().__init__(
            name="print",
            inputs=["x"],
            constants=["func"],
            opcounter=VCounter(op=None),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(x, func):
        """Prints a string given by func(x), where x is a numpy array"""
        print(func(x))


class LSTM(OpType):
    def __init__(self):
        super().__init__(
            name="lstm",
            inputs=["x"],
            constants=[
                "num_layers",
                "input_size",
                "hidden_size",
                "batch_first",
                "sigmoid",
                "tanh",
                "layers",  # layers contains layer-specific constants
            ],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(
        x, num_layers, input_size, hidden_size, batch_first, sigmoid, tanh, layers
    ):
        raise NotImplementedError


class PWLIN(OpType):
    def __init__(self):
        super().__init__(
            name="pwlin",
            inputs=["x"],
            constants=["c0", "c1", "q_c0", "q_c1", "name", "q_addr"],
            opcounter=NullCounter(),
            can_bcast_in=False,
        )

    @staticmethod
    def runtime(
        x,
        c0,
        c1,
        q_c0,
        q_c1,
        name,
        q_addr,
    ):
        raise NotImplementedError


class LOOP(OpType):
    """
    Subgraph-calling LOOP node

    input arguments types:
        - x_recurse_i: initial value for the ith recursed input
        - x_sliced_i: ith input that will be sliced. This is configured by:
            - block_size (int): size of each sliced block
            - stride (int): positive integer, stride between slices. In most cases, `stride == block_size`,
                but `stride < block_size` can lead to overlapping input frames.

                at iteration index n:

                    x_i[n] = x_sliced_i[stride * n: stride * n + block_size]

            - reversed (bool): if True, the input is indexed in reverse order -- n in the expression above
                will be reverse-ordered from [(niter-1), (niter-2), ..., 1, 0]. The underlying data is not
                itself flipped.

    output types:
        y_concat_i: concatenated sequence of outputs, configured by:
            - reversed (bool): if True, the output is concatenated in reverse order
        y_final_i: returned final value

    subgraph signature wrapping:
        We need to annotate how we are going to pass inputs into the subgraph, and how to pull out the
        subgraph's outputs.

        annotation types:
            * recursed input annotations:
                {"x_recurse_i": (input_idx, output_idx)} -- mapping from the recursed input name to the
                    input and output index from the graph
            * sliced input annotations:
                {"x_sliced_i": input_idx}
            * concatenated output annotations:
                {"x_concat_i": output_idx}
            * final output annotations:
                {"y_final_i": output_idx}

    The OpNode's runtime returns output in this order:

        final outputs first, in increasing order
        followed by concat outputs, in increasing order.

        [y_final_0, y_final_1, ..., y_concat_0, y_concat_1, ...]

    """

    def __init__(self):
        super().__init__(
            name="loop",
            inputs=["kwargs"],
            constants=[
                "n_iter",
                "n_recurse",
                "n_sliced",
                "n_scope",
                "n_concat",
                "n_final",
                "block_size_sliced",
                "reverse_sliced",
                "reverse_concat",
            ],
            opcounter=NullCounter(),
            can_bcast_in=False,
            repr_settings=NodeReprSettings(
                constants_to_rep=[
                    "n_iter",
                    "n_recurse",
                    "n_sliced",
                    "n_concat",
                    "n_scope",
                    "n_final",
                    "block_size_sliced",
                    "reverse_sliced",
                    "reverse_concat",
                ]
            ),
        )

    @staticmethod
    def runtime(
        n_iter: int,
        n_recurse: int,
        n_sliced: int,
        n_scope: int,
        n_concat: int,
        n_final: int,
        block_size_sliced: list[int],
        reverse_sliced: list[bool],
        reverse_concat: list[bool],
        subgraph,
        **kwargs,
    ):
        assert n_iter > 0

        # initialize recursed state
        recursed_state = []
        for i in range(n_recurse):
            key = f"x_recurse_{i}"
            recursed_state.append(kwargs[key])

        # initialize scope state
        scope_state = []
        for i in range(n_scope):
            key = f"x_scope_{i}"
            scope_state.append(kwargs[key])

        # initialize concatenated outputs
        concat_outputs = [[] for _ in range(n_concat)]

        for n in range(n_iter):
            # get sliced inputs
            sliced_inputs = []
            for i, block_size, reversed in zip(
                range(n_sliced), block_size_sliced, reverse_sliced
            ):
                key = f"x_sliced_{i}"
                x = kwargs[key]
                k = n
                if reversed:
                    k = n_iter - n - 1
                x_sliced = x[block_size * k : block_size * (k + 1)]
                sliced_inputs.append(x_sliced)

            # input order: recursed, sliced
            inputs = list(recursed_state) + list(sliced_inputs) + list(scope_state)

            # run loop body, get list of outputs
            outputs = subgraph.run(*inputs, dequant=False)
            if isinstance(outputs, np.ndarray):
                outputs = [outputs]
            elif isinstance(outputs, tuple):
                outputs = list(outputs)

            # update recursed state
            new_recursed_state = outputs[:n_recurse]
            for x, y in zip(recursed_state, new_recursed_state):
                assert x.shape == y.shape
            recursed_state = new_recursed_state

            # update concatenated output lists
            for i in range(n_concat):
                concat_outputs[i].append(outputs[n_recurse + i])

        # put together the final package
        ret = []

        # concatenate the concatenated outputs
        for concat_list, reverse in zip(concat_outputs, reverse_concat):
            if reverse:
                concat_list = concat_list[::-1]
            ret.append(np.concatenate(concat_list, axis=0))

        # extract the final values
        for i in range(n_final):
            ret.append(outputs[i + n_recurse + n_concat])

        return tuple(ret)


registry_v1 = OpRegistry("fmot_atomics_v1.2")


def register(*optypes):
    for optype in optypes:
        op = optype()
        assert isinstance(op, OpType)
        registry_v1.register_op(op)


register(
    VVADD,
    VIADD,
    VVSUB,
    VNEG,
    VVMUL,
    VIMUL,
    MATMUL,
    ADDMM,
    RELU,
    LUT,
    TRANSPOSE,
    RESHAPE,
    QUANTIZE,
    DEQUANTIZE,
    CHUNK,
    SPLIT,
    CAT,
    STACK,
    SQUEEZE,
    ZEROS,
    CONSTANT,
    ASSIGN,
    SUM,
    CONSTANT_LIKE,
    COPY,
    SHIFT,
    GT0,
    LSTM,
    TEMPORAL_UNFOLD,
    TEMPORAL_UNFOLD_UNKERNELIZED,
    PRINT,
    TEMPORAL_TRANSPOSE_FOLD_UNKERNELIZED,
    TEMPORAL_CONV2D,
    PWLIN,
    GMACv2,
    LOOP,
)
