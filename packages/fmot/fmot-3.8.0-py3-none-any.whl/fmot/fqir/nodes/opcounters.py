from ..variables import TensorProto
from ..utils import get_tensor_length
import numpy as np
import warnings
from .opcount import OpCount


class OpCounter:
    DEFAULT_ST_LD_PESSIMISM = 0.5
    """
    Base class for an op-counting function
    """

    def count(
        self,
        inputs,
        outputs,
        constants,
        st_ld_pessimism,
        input_length=1,
        output_length=1,
    ):
        """
        Needs to be implemented for each opcount class.
        Args:
            inputs (dict): A dictionary mapping argnames to TensorProtos
            outputs (list): A list of output TensorProtos
            st_ld_pessimism (float): A float between 0 and 1.
                What fraction of store-loads do we expect to be unable
                to elimate?
                0: All store-loads are eliminated.
                1: No store-loads are eliminated.
            input_length (int): Number of input frames in complete sequence.
            output_length (int): Number of output frames in complete sequence.
                `input_length != output_length` in the case of conditionally-executed
                layers like strided convolutions.
        Returns:
            OpCount
        """
        raise NotImplementedError

    def __call__(self, inputs, outputs, constants, st_ld_pessimism=None, debug=False):
        input_shape = get_tensor_length(inputs.values())
        output_shape = get_tensor_length(outputs)
        if input_shape is None:
            input_length = 1
        else:
            input_length = np.prod(input_shape)
        if output_shape is None:
            output_length = 1
        else:
            output_length = np.prod(output_shape)
        if st_ld_pessimism is None:
            st_ld_pessimism = self.DEFAULT_ST_LD_PESSIMISM
        assert 0 <= st_ld_pessimism and st_ld_pessimism <= 1
        output = self.count(
            inputs, outputs, constants, st_ld_pessimism, input_length, output_length
        )
        assert isinstance(output, OpCount)
        if False:
            print(f"Input shape: {input_shape} -> Output shape: {output_shape}")
            print(output.energy())
            print()
        return output


class VVCounter(OpCounter):
    """
    OpCounter for vvadd, vvmul, vvsub

    .. todo::

        - Effects of mixed-precision casting??
    """

    _ops = ["add", "mul"]

    def __init__(self, op="add"):
        assert op in self._ops
        self.op = op

    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        x_bytes = inputs["x"].nbytes(nonzero_only=False)
        y_bytes = inputs["y"].nbytes(nonzero_only=False)
        numel = outputs[0].numel(nonzero_only=False)
        z_bytes = outputs[0].nbytes(nonzero_only=False)

        # Load first operand into accumulator. Maybe store-load elimination
        load_first = (
            OpCount(mem_read_bytes=(x_bytes + y_bytes) / 2, acc_write_numel=numel)
            * st_ld_pessimism
        )
        # Load second operand into accumulator while performing arithmetic
        load_and_op_second = OpCount(
            mem_read_bytes=(x_bytes + y_bytes) / 2,
            acc_read_numel=numel,
            acc_write_numel=numel,
        )
        if self.op == "add":
            load_and_op_second += OpCount(additions=numel)
        else:
            load_and_op_second += OpCount(multiplies=numel)
        # Write output to accumulator. Maybe store-load elimination
        write_output = (
            OpCount(acc_read_numel=numel, mem_write_bytes=z_bytes) * st_ld_pessimism
        )

        # multiply by input_length
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )
        return input_length * (load_first + load_and_op_second + write_output)


class VCounter(OpCounter):
    """
    OpCounter for viadd, vimul, vneg, relu
    """

    _ops = ["add", "mul", None]

    def __init__(self, op=None, sparse_out=False):
        assert op in self._ops
        self.op = op
        self.sparse_out = sparse_out

    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        x_bytes = inputs["x"].nbytes(nonzero_only=False)
        y_bytes = outputs[0].nbytes(nonzero_only=self.sparse_out)
        numel = inputs["x"].numel(nonzero_only=False)

        load_x = (
            OpCount(mem_read_bytes=x_bytes, acc_write_numel=numel) * st_ld_pessimism
        )
        # read acc, perform op, overwrite acc
        logic = OpCount(acc_read_numel=numel, acc_write_numel=numel)
        if self.op == "add":
            logic += OpCount(additions=numel)
        elif self.op == "mul":
            logic += OpCount(multiplies=numel)
        else:
            logic += OpCount(other_logic=numel)
        write_y = (
            OpCount(acc_read_numel=numel, mem_write_bytes=y_bytes) * st_ld_pessimism
        )

        # multiply by input_length
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )

        return input_length * (load_x + logic + write_y)


class MatmulCounter(OpCounter):
    @staticmethod
    def matmul_count(
        matrix, vector, output, bias=None, st_ld_pessimism=0, mat_first=True
    ):
        """
        Args:
            matrix: TensorProto
            vector: TensorProto
            output: TensorProto
            bias: TensorProto, optional
        Returns:
            OpCount
        """
        if vector.avg_sparsity is not None:
            vector_density = 1 - vector.avg_sparsity
        else:
            vector_density = 1

        matrix_density = matrix.nbytes(nonzero_only=True) / matrix.nbytes(
            nonzero_only=False
        )

        if vector_density == 1 and matrix_density == 1:
            return MatmulCounter.wvprod_count(
                matrix, vector, output, bias, st_ld_pessimism
            )
        elif vector_density == 1 and matrix_density != 1:
            return MatmulCounter.uvprod_count(
                matrix, vector, output, bias, st_ld_pessimism
            )
        else:
            return MatmulCounter.usprod_count(
                matrix, vector, output, bias, st_ld_pessimism, mat_first=mat_first
            )

    @staticmethod
    def acc_init(output, bias=None):
        """
        Returns an OpCount for initializing the accumulator before starting
        a matmul. Either zeros init or bias-load init.
        """
        if bias is not None:
            # initialize with bias
            return OpCount(
                mem_read_bytes=bias.nbytes(),
                acc_write_numel=bias.numel(),
                additions=bias.numel(),
            )
        else:
            # initialize with zeros
            return OpCount(acc_write_numel=output.numel())

    @staticmethod
    def wvprod_count(matrix, vector, output, bias=None, st_ld_pessimism=0):
        """
        Returns an opcount for a dense matmul
        """
        acc_init = MatmulCounter.acc_init(output, bias)

        # memory and accumulator count for the matmul itself
        matmul = OpCount(
            mem_read_bytes=matrix.nbytes() + vector.nbytes(),
            acc_read_numel=matrix.numel(),
            acc_write_numel=matrix.numel(),
            macs=matrix.numel(),
            emacs=matrix.numel(),
        )

        # writing result to memory
        output_write = (
            OpCount(acc_read_numel=output.numel(), mem_write_bytes=output.nbytes())
            * st_ld_pessimism
        )

        return acc_init + matmul + output_write

    @staticmethod
    def usprod_count(
        matrix, vector, output, bias=None, st_ld_pessimism=0, mat_first=True
    ):
        """
        Returns an opcount for a sparse-sparse matmul
        """
        acc_init = MatmulCounter.acc_init(output, bias)

        ### COUNT NUMBER OF MACS
        # uncorrelated:
        vector_density = 1 - vector.avg_sparsity
        macs = vector_density * matrix.numel(nonzero_only=True)
        emacs = matrix.numel(nonzero_only=False)

        # if density-per-element annotation exists, use correlated count:
        density_per_el = vector.density_per_element
        if density_per_el is not None:
            mat = matrix._value()
            if mat is not None:
                ### CORRECTION: Count sparsity based on pencil pattern
                mat_nz = (mat != 0).astype(float)
                ###
                if mat_first:
                    macs = (mat_nz @ density_per_el).sum()
                else:
                    macs = (density_per_el @ mat_nz).sum()
        matrix_bytes_per_el = matrix.nbytes() / matrix.numel()

        # OpCount for the multiply operation
        matmul = OpCount(
            mem_read_bytes=macs * matrix_bytes_per_el
            + vector.nbytes(nonzero_only=True),
            acc_read_numel=macs,
            acc_write_numel=macs,
            macs=macs,
            emacs=emacs,
        )

        # writing result to memory
        output_write = (
            OpCount(acc_read_numel=output.numel(), mem_write_bytes=output.nbytes())
            * st_ld_pessimism
        )

        return acc_init + matmul + output_write

    @staticmethod
    def uvprod_count(matrix, vector, output, bias=None, st_ld_pessimism=0):
        """
        Returns an OpCount for a sparse-matrix, dense-vector matmul. Adds additional
        overhead to account for the following kernelization:

            x_pos = relu(x)
            x_neg = relu(-x)
            y_pos = W @ x_pos
            y_neg = W @ x_neg
            y = y_pos - y_neg

        """
        vector_bytes = vector.nbytes(nonzero_only=False)
        vector_numel = vector.numel(nonzero_only=False)

        # Positive ReLU
        pos_relu = (
            # load vector
            OpCount(mem_read_bytes=vector_bytes, acc_write_numel=vector_numel)
            * st_ld_pessimism
            +
            # perform relu op
            OpCount(acc_read_numel=vector_numel, acc_write_numel=vector_numel)
            +
            # store
            OpCount(acc_read_numel=vector_numel, mem_write_bytes=0.5 * vector_bytes)
        )

        # Negative ReLU
        neg_relu = (
            # load vector
            OpCount(mem_read_bytes=vector_bytes, acc_write_numel=vector_numel)
            +
            # neg
            OpCount(acc_read_numel=vector_numel, acc_write_numel=vector_numel)
            +
            # relu (no store in between)
            OpCount(acc_read_numel=vector_numel, acc_write_numel=vector_numel)
            +
            # store
            OpCount(acc_read_numel=vector_numel, mem_write_bytes=0.5 * vector_bytes)
        )

        # Initialize state for 2 matmuls
        # first one with bias, second with zeros
        acc_init = MatmulCounter.acc_init(output, bias) + MatmulCounter.acc_init(
            output, None
        )

        # Perform matmul operation
        ### CORRECTION: Count sparsity of matrix based on pencil pattern!!!
        macs = matrix.numel(nonzero_only=True)
        emacs = matrix.numel(nonzero_only=False)
        matmul = OpCount(
            mem_read_bytes=vector.nbytes(nonzero_only=False)
            + matrix.nbytes(nonzero_only=True),
            acc_read_numel=macs,
            acc_write_numel=macs,
            macs=macs,
            emacs=emacs,
        )

        # store first output
        partial_store = OpCount(
            acc_read_numel=output.numel(), mem_write_bytes=output.nbytes()
        )

        # perform subtraction (keep partial sum in accumulator, load other)
        sub_count = OpCount(
            mem_read_bytes=output.nbytes(),
            acc_read_numel=output.nbytes(),
            acc_write_numel=output.nbytes(),
        )

        # writing result to memory
        output_write = OpCount(acc_read_numel=output.nbytes() * st_ld_pessimism)

        return (
            pos_relu
            + neg_relu
            + acc_init
            + matmul
            + partial_store
            + sub_count
            + output_write
        )

    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        output = outputs[0]
        if len(inputs["x"].shape) == 2:
            matrix, vector, mat_first = inputs["x"], inputs["y"], True
        else:
            matrix, vector, mat_first = inputs["y"], inputs["x"], False

        bias = inputs.get("bias", None)

        opcount = MatmulCounter.matmul_count(
            matrix, vector, output, bias, st_ld_pessimism, mat_first
        )

        # multiply by input_length
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )

        return opcount * input_length


class ConvCounter(OpCounter):
    @staticmethod
    def matmul_count(
        x,
        weight,
        output,
        input_length,
        output_length,
        constants,
        bias=None,
        st_ld_pessimism=0,
    ):
        buffer_rotation = OpCount(
            mem_read_bytes=x.nbytes() * st_ld_pessimism,
            acc_write_numel=x.numel() * st_ld_pessimism,
            acc_read_numel=x.numel(),
            mem_write_bytes=x.numel(),
        )

        matrix = weight._value()
        shp = matrix.shape
        kernel_size = shp[2:]
        in_channels = shp[1]
        out_channels = shp[0]
        stacked_input_size = in_channels * np.prod(kernel_size)
        matrix = matrix.reshape(out_channels, stacked_input_size)
        matrix_tproto = TensorProto(
            name="matrix_temp",
            dtype=weight.dtype,
            shape=list(matrix.shape),
            value=matrix,
        )

        if x.density_per_element is None:
            density_per_element = None
        else:
            density_per_element = np.concatenate(
                [x.density_per_element] * np.prod(kernel_size)
            )
        stacked_vec_tproto = TensorProto(
            name="vector_temp",
            dtype=x.dtype,
            shape=[stacked_input_size],
            avg_sparsity=x.avg_sparsity,
            density_per_element=density_per_element,
        )

        matmul = MatmulCounter.matmul_count(
            matrix_tproto,
            stacked_vec_tproto,
            output,
            bias,
            st_ld_pessimism,
            mat_first=True,
        )

        return buffer_rotation * input_length + matmul * output_length

    @staticmethod
    def depthwise_count(
        x,
        weight,
        output,
        input_length,
        output_length,
        constants,
        bias=None,
        st_ld_pessimism=0,
    ):
        buffer_rotation = OpCount(
            mem_read_bytes=x.nbytes() * st_ld_pessimism,
            acc_write_numel=x.numel() * st_ld_pessimism,
            acc_read_numel=x.numel(),
            mem_write_bytes=x.numel(),
        )

        acc_init = MatmulCounter.acc_init(output, bias)
        x_fmt = x.nbytes() / x.numel()

        macs = weight.numel()
        dw_product = OpCount(
            mem_read_bytes=weight.nbytes() + x_fmt * weight.numel(),
            acc_read_numel=macs,
            acc_write_numel=macs,
            emacs=macs,
        )

        output_write = (
            OpCount(acc_read_numel=output.numel(), mem_write_bytes=output.nbytes())
            * st_ld_pessimism
        )

        return (
            buffer_rotation * input_length + (dw_product + output_write) * output_length
        )

    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        output = outputs[0]
        if "x" in inputs:
            x = inputs["x"]
        elif "input" in inputs:
            x = inputs["input"]
        else:
            assert False
        weight = inputs["weight"]
        bias = inputs.get("bias", None)

        if constants["groups"] == 1:
            return self.matmul_count(
                x,
                weight,
                output,
                input_length,
                output_length,
                constants,
                bias,
                st_ld_pessimism,
            )
        elif constants["groups"] == weight.shape[0]:
            return self.depthwise_count(
                x,
                weight,
                output,
                input_length,
                output_length,
                constants,
                bias,
                st_ld_pessimism,
            )
        else:
            assert (
                False
            ), f"input_length={input_length} was expected to be tuple or list"


class VLUTCounter(OpCounter):
    _table_always_16b = True

    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        x_bytes = inputs["x"].nbytes(nonzero_only=False)
        y_bytes = outputs[0].nbytes(nonzero_only=False)
        numel = inputs["x"].numel(nonzero_only=False)

        # load address into accumulator
        addr_load = (
            OpCount(mem_read_bytes=x_bytes, acc_write_numel=numel) * st_ld_pessimism
        )

        # perform lut operation
        lut = OpCount(
            acc_read_numel=numel,
            acc_write_numel=numel,
            table_read_bytes=2 * numel if self._table_always_16b else y_bytes,
            luts=numel,
        )

        # write result
        output_write = (
            OpCount(acc_read_numel=numel, mem_write_bytes=y_bytes) * st_ld_pessimism
        )

        # multiply by input_length
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )
        return input_length * (addr_load + lut + output_write)


class NullCounter(OpCounter):
    def count(self, *args, **kwargs):
        return OpCount()


class CopyCounter(OpCounter):
    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        mem_reads = OpCount()
        N_read = 0
        for x in inputs.values():
            mem_reads += OpCount(mem_read_bytes=x.nbytes(), acc_write_numel=x.numel())
            N_read += 1
        # one of the inputs may have already been in the accumulator
        mem_reads *= (N_read - 1 + st_ld_pessimism) / N_read

        mem_writes = OpCount()
        N_write = 0
        for x in outputs:
            mem_writes += OpCount(mem_write_bytes=x.nbytes(), acc_read_numel=x.numel())
            N_write += 1
        # the output may stay in the accumulator
        if N_write != 0:
            mem_writes *= (N_write - 1 + st_ld_pessimism) / N_write

        # multiply by input_length
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )
        return (mem_reads + mem_writes) * input_length


class ShiftCounter(OpCounter):
    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        x = inputs["x"]
        y = outputs[0]
        shamt = constants["shamt"]
        if shamt == 0 and x.dtype == y.dtype:
            return OpCount()
        else:
            numel = x.numel(nonzero_only=False)

            mem_read_bytes = 0
            mem_write_bytes = 0
            acc_read_numel = 0
            acc_write_numel = 0

            # 1. load x in accumulator. It may already be there
            mem_read_bytes += st_ld_pessimism * x.nbytes(nonzero_only=False)
            acc_write_numel += st_ld_pessimism * numel
            # 2. write back to memory. It may be able to stay in accumulator
            mem_write_bytes += st_ld_pessimism * y.nbytes(nonzero_only=False)
            acc_read_numel += st_ld_pessimism * numel

            # multiply by input_length
            if input_length != output_length:
                warnings.warn(
                    f"input_length != output_length ({input_length} != {output_length})"
                )
            mem_read_bytes *= input_length
            mem_write_bytes *= input_length
            acc_read_numel *= input_length
            acc_write_numel *= input_length
            return OpCount(
                mem_read_bytes=mem_read_bytes,
                mem_write_bytes=mem_write_bytes,
                acc_read_numel=acc_read_numel,
                acc_write_numel=acc_write_numel,
            )


class ReductionCounter(OpCounter):
    def count(
        self, inputs, outputs, constants, st_ld_pessimism, input_length, output_length
    ):
        x = inputs["x"]
        y = outputs[0]
        # Without hw support for now, this is a rough sketch of what would happen
        if input_length != output_length:
            warnings.warn(
                f"input_length != output_length ({input_length} != {output_length})"
            )
        return input_length * OpCount(
            mem_read_bytes=x.nbytes(nonzero_only=False),
            mem_write_bytes=y.nbytes(nonzero_only=False),
            acc_read_numel=x.numel(nonzero_only=False),
            acc_write_numel=x.numel(nonzero_only=False),
            additions=x.numel(),
        )
