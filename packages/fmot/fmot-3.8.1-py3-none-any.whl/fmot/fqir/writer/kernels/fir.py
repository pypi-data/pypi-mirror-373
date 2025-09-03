from fmot.fqir.writer import FQIRWriter
from fmot.fqir import TensorProto
import numpy as np
import math
from typing import Optional, Literal


def write_fir(
    writer: FQIRWriter,
    b: np.ndarray,
    x: TensorProto,
    quanta: Optional[int] = None,
    dot_method: Literal["tree", "matrix"] = "tree",
):
    """Generate a time-domain FIR filter with static filter weights.

    This implementation uses a per-sample for-loop to iteratively apply the FIR filter to the input
    signal.

    Arguments:
        writer (FQIRWriter): FQIRWriter instance
        b (np.ndarray): feedforward filter coefficients, [b[0], b[1], ..., b[n_taps-1]]
        x (TensorProto): a time-domain signal, to apply the FIR filter to. This
            tensor represents one hop of the time-domain signal, and a stateful
            buffer will be used to carry the relevant history of the signal.
        quanta (int, Optional): desired output quanta for the output signal. If None is provided,
            will be optimized based on the L1 norm of the FIR weights
        dot_method ("tree" | "matrix", optional): method of performing reduction inside of dot-product.
            "tree" results in a significant reduction in quantization error, but requires slightly more operations.
            Default "tree".
    """

    n_taps = len(b)
    # this buffer will hold values of x --> should have x's quanta
    x_buffer = writer.add_zeros_buffer(
        channels=n_taps, quanta=x.quanta, precision=writer.output_precision
    )

    if quanta is None:
        # use the L1 norm of the FIR coefficients to predict that maximum output amplitude.
        # this is for the worst-case scenario where `x[n] = sign(b[n])`, this yielding `y[n] = sum(abs(b[n]))``
        b_norm = np.sum(np.abs(b))
        b_norm_delta_quanta = int(math.ceil(math.log2(b_norm)))
        quanta = x.quanta + b_norm_delta_quanta

    with writer.for_loop_writer(
        n_iter=x.shape[0], x_to_slice=[x], x_recurse_init=[x_buffer]
    ) as lwriter:
        # unpack loop inputs (note that if there is a single input, we need to add the "," because this is a list-unpack)
        (x_t,) = lwriter.sliced_inputs
        (buff_in,) = lwriter.recursed_inputs

        # register a parameter for the FIR weights (we do this locally inside of the loop itself)
        fir_weights = lwriter.add_parameter(b, precision=writer.output_precision)

        # rotate the buffer (of length n_taps)
        buff_new = lwriter.rotate(buff_in, x_t, insert_end=False)

        # perform dot protduct with FIR weights. Use the desired output quanta
        y_t = lwriter.dot(buff_new, fir_weights, quanta=quanta, method=dot_method)

        # loop outputs:
        # - update the buffer buff_in' = buff_new
        # - return concatenation of y_t
        # - return the final value of the buffer (for use in top-level graph assign node)]

        lwriter.update_recursed_state(buff_in, buff_new)
        y_concat = lwriter.return_concatenated(y_t)

        buff_final = lwriter.return_final(buff_new)

    # add an assign node for the buffer --> this ensures that the buffer state is updated between time-steps
    # equivalent to: x_buffer = buff_final
    writer.assign(x_buffer, buff_final)

    return y_concat
