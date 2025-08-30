from fmot.fqir import GraphProto, NodeProto, TensorProto, registry_v1
import numpy as np
from fmot.tracing.utils import autogen_name
import math
from typing import Literal, Optional, Union
from functools import partial
from contextlib import contextmanager
from typing import Callable
from fmot.qat.nn.luts import Table

__all__ = ["working_graph", "add", "scale_by_float"]

MAX_IMM_BITS = 24


FUNC_TYPE = Callable[[np.ndarray], tuple[np.ndarray]]


class FQIRShapeError(Exception):
    """Raised when tensor shapes are incompatible for the requested operation."""

    pass


class NoActiveGraphError(Exception):
    """Raised when a graph operation is attempted without an active working graph."""

    pass


class PrecisionError(Exception):
    """Raised when encountering unknown/unexpected precisions"""

    pass


@contextmanager
def working_graph(
    graph: GraphProto, init: Optional[GraphProto] = None, act_precision="int16"
):
    """
    Context manager that sets the active FQIR working graphs and returns an FQIRWriter.

    Args:
        graph (GraphProto): The FQIR graph to set as active.
        init (GraphRroto, optional): Init graph
        act_precision (str, optional): precision to use for activations as they are created

    Example:
        with working_graph(my_graph) as writer:
            writer.add(x, y)
    """

    try:
        yield FQIRWriter(graph, init, act_precision)
    finally:
        pass


def shapes_broadcastable(x: TensorProto, y: TensorProto) -> bool:
    """
    Check whether two 1D tensors can be broadcast together under FQIR rules.

    Only supports 1D tensors. Two tensors are broadcastable if:
      - Their lengths are equal, or
      - One of them has length 1.

    Args:
        x (TensorProto): First input tensor.
        y (TensorProto): Second input tensor.

    Returns:
        bool: True if tensors can be broadcasted, False otherwise.

    Raises:
        FQIRShapeError: If either tensor is not 1D.
    """
    if len(x.shape) != 1 or len(y.shape) != 1:
        raise FQIRShapeError(
            f"FQIR currently only supports broadcasting 1D tensors. "
            f"Received shapes: x.shape={x.shape}, y.shape={y.shape}."
        )

    l_x = x.shape[0]
    l_y = y.shape[0]

    if l_x == l_y or l_x == 1 or l_y == 1:
        return True

    return False


def broadcasted_shape(x: TensorProto, y: TensorProto) -> list[int]:
    """
    Compute the broadcasted shape for two 1D tensors.

    Args:
        x (TensorProto): First input tensor.
        y (TensorProto): Second input tensor.

    Returns:
        list[int]: The resulting broadcasted shape (always a 1-element list).

    Raises:
        FQIRShapeError: If tensors are not broadcastable.
    """
    if not shapes_broadcastable(x, y):
        raise FQIRShapeError(f"Cannot broadcast shapes {x.shape} and {y.shape}.")

    l_x = x.shape[0]
    l_y = y.shape[0]

    return [max(l_x, l_y)]


def get_bw(
    dtype: Literal["int8", "int16", "int24", "fqint8", "fqint16", "fqint24"]
) -> int:
    """
    Get the bit-width associated with a given precision setting.

    Args:
        dtype (str): precision string, for example "fqint8" or "fqint16

    Returns:
        int: The corresponding bit-width (8 or 16).

    Raises:
        PrecisionError: If the provided precision is not recognized.
    """

    if dtype in ["int8", "fqint8"]:
        return 8
    elif dtype in ["int16", "fqint16"]:
        return 16
    elif dtype in ["int24", "fqint24"]:
        return 24
    else:
        raise PrecisionError(
            f"Unexpected precision '{dtype}'. Expected 'fqint8', 'fqint16', or 'fqint24'."
        )


def quantize(
    x: Union[float, np.ndarray], bits: int = 16
) -> tuple[Union[int, np.ndarray], int]:
    """
    Quantize a float or float array to fixed-point integers using a given bit-width.

    The quantization scales values based on the maximum absolute magnitude of `x`, ensuring
    the range fits into the specified number of bits.

    Args:
        x (Union[float, np.ndarray]): Input float or array of floats to quantize.
        bits (int, optional): Number of bits for the target quantization (e.g., 8 or 16). Defaults to 16.

    Returns:
        tuple:
            - y (Union[int, np.ndarray]): Quantized integer or array of integers.
            - quanta (int): Scaling exponent used for quantization (i.e., the power-of-two shift applied).

    Notes:
        - If the input maximum absolute value is 0, a quanta of 0 is returned and all outputs are 0.
        - The output values are clipped to the representable range [-2^(bits-1), 2^(bits-1) - 1].

    Example:
        >>> quantize(0.5, bits=8)
        (64, -7)

        >>> quantize(np.array([0.1, 0.5, -1.2]), bits=8)
        (array([ 21.,  64., -153.]), -7)
    """
    if isinstance(x, np.ndarray):
        maxabs = np.max(np.abs(x))
    else:
        maxabs = np.abs(x)

    if maxabs == 0:
        quanta = -bits + 1
    else:
        quanta = int(np.ceil(np.log2(maxabs))) + 1 - bits

    y = np.clip(np.round(x * 2**-quanta), -(2 ** (bits - 1)), 2 ** (bits - 1) - 1)

    if isinstance(x, (float, int)) and isinstance(y, np.ndarray):
        y = int(y.item())
    else:
        y = y.astype(np.int32)

    return y, quanta


def get_add_sub_quanta(bw_x: int, q_x: int, bw_y: int, q_y: int, bw_out: int) -> int:
    """Determines the optimal output quanta for the given input operands
    for an add/sub operation, such that the quanta is above the saturation limit.

    Arguments:
        bw_x (int): bitwidth for operand x
        q_x (int): quanta for operand x
        bw_y (int): bitwidth for operand y
        q_y (int): bitwidth for operand y
        bw_out (int): bitwidth for output

    Returns:
        quanta (int)
    """
    maxval_x = 2 ** (bw_x + q_x - 1)
    maxval_y = 2 ** (bw_y + q_y - 1)

    maxval_x_plus_y = maxval_x + maxval_y

    _, quanta = quantize(maxval_x_plus_y, bw_out)
    return quanta


def new_fqir_graph(inputs: list[TensorProto] = []) -> GraphProto:
    """Creates an empty FQIR graph with ARITH, INIT, and empty QUANT subgraphs"""
    main = GraphProto()
    arith = GraphProto("ARITH")
    init = GraphProto("INIT")
    quant = GraphProto("QUANT")

    quant_node = NodeProto(
        name="QUANT",
        subgraph=quant,
        inputs={f"x{i}": x for i, x in enumerate(inputs)},
        outputs=inputs.copy(),
        optype=None,
    )
    main.add_node(quant_node)
    main.add_subgraph("QUANT", quant)

    arith_node = NodeProto(
        name="ARITH",
        subgraph=arith,
        inputs={f"x{i}": x for i, x in enumerate(inputs)},
        outputs=[],
        optype=None,
    )
    main.add_node(arith_node)
    main.add_subgraph("ARITH", arith)

    init_node = NodeProto(
        name="INIT", subgraph=init, inputs={}, outputs=[], optype=None
    )
    main.add_node(init_node)
    main.add_subgraph("INIT", init)

    main.inputs = inputs.copy()
    arith.inputs = inputs.copy()
    return main


class FQIRWriter:
    """
    A high-level API for constructing quantized graphs and merging models.
    This class is designed to generate and manipulate arithmetic computation graphs using
    quantized integers. This can be used to generate algorithms in FQIR
    without the need to define them in PyTorch using fmot, or to extend FQIR generated from fmot with
    custom arithmetic kernels.
    """

    def __init__(
        self,
        arith: GraphProto,
        init: GraphProto,
        act_precision: str,
        main: Optional[GraphProto] = None,
    ):
        self.arith = arith
        self.init = init
        self.main = main
        self.act_precision = act_precision
        self.disable_gt0_decomp = False

        self.quant_node: Optional[NodeProto] = None
        if main is not None:
            for node in main.nodes:
                if node.name == "QUANT":
                    self.quant_node = node
                    break

    @classmethod
    def from_fqir(cls, graph: GraphProto, act_precision: str = "int16"):
        """Convenience method to easily construct FQIRWriter around an FQIR graph.

        Arguments:
            graph (GraphProto): FQIR graph to write (can be empty).
            act_precision (str): activation precision, default "int16". Can be "int8",
                "int16", or "int24".
        """
        new = cls(
            arith=graph.subgraphs["ARITH"],
            init=graph.subgraphs["INIT"],
            main=graph,
            act_precision=act_precision,
        )
        return new

    @property
    def output_precision(self):
        if self.act_precision == "int16":
            return "fqint16"
        elif self.act_precision == "int8":
            return "fqint8"
        elif self.act_precision == "int24":
            return "fqint24"
        else:
            raise PrecisionError(f"precision {self.act_precision} not recognized")

    def add_parameter(
        self,
        x: np.ndarray,
        name: Optional[str] = None,
        precision: Literal["int16", "int8", "int24"] = "int16",
        quanta: int = None,
    ) -> TensorProto:
        """Adds a new parameter to the graph.
        If the provided array is floating-point, it will be quantized first.

        Arguments:
            x (np.ndarray): a float or integer array. If it is integer, then the
                `quanta` argument is required. If it is floating-point, it will be
                quantized an a `quanta` will be chosen to minimize quantization error.
            name (str, optional): an optional name to give the Tensor in the graph
            precision (str, optional): "int24", "int16" or "int8", default "int16"
            quanta (int, optional): Only used if x is integral type.
        """

        if precision.startswith("int"):
            precision = "fq" + precision

        if np.issubdtype(x.dtype, np.integer):
            if quanta is None:
                raise RuntimeError(
                    "Cannot construct a parameter for an integer tensor without a quanta."
                )

        else:
            if quanta is None:
                x, quanta = quantize(x, bits=get_bw(precision))
            else:
                x = x * 2 ** (-quanta)
                bits = get_bw(precision)
                x = np.clip(x, -(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
                x = x.astype(np.int32)

        param = TensorProto(
            name=name if name is not None else autogen_name(prefix="param"),
            dtype=precision,
            shape=list(x.shape),
            value=x,
            quanta=quanta,
        )

        self.arith.add_parameter(param)

        return param

    def add_zeros_buffer(
        self,
        channels: int,
        quanta: int,
        name: Optional[str] = None,
        precision: Literal["int24", "int16", "int8"] = "int16",
    ) -> TensorProto:
        """Adds a new zero-initialized state-buffer to the graph.
        Inserts the zeros initialization of the buffer into the INIT graph

        Arguments:
            channels (int): number of channels in the buffer
            quanta (int): integer power of two for scaling factor, required.
            name (str, optional): an optional name to give the Tensor in the graph
            precision (str, optional): "int24", "int16" or "int8", default "int16"
        """

        if precision.startswith("int"):
            precision = "fq" + precision

        x = TensorProto(
            name=name if name is not None else autogen_name(prefix="buffer"),
            dtype=precision,
            shape=[channels],
            quanta=quanta,
        )

        zeros = NodeProto(
            name=f"{x.name}-init",
            optype=registry_v1["zeros"],
            inputs={},
            outputs=[x],
            constants={"shape": x.shape},
        )

        self.init.add_node(zeros)

        return x

    def add_input(
        self,
        channels: int,
        quanta: int,
        name: Optional[str] = None,
        precision: Literal["int24", "int16", "int8"] = "int16",
    ) -> TensorProto:
        """Adds a new input to the graph. This will append to the end of the list of inputs if any inputs already exist.

        Arguments:
            channels (int): number of channels in the input
            quanta (int): integer power of two for scaling factor, required.
            name (str, optional): an optional name to give the Tensor in the graph
            precision (str, optional): "int24", "int16" or "int8", default "int16"

        Returns:
            TensorProto: the input tensor
        """

        if precision.startswith("int"):
            precision = "fq" + precision

        x = TensorProto(
            name=name if name is not None else autogen_name(prefix="input"),
            dtype=precision,
            shape=[channels],
            quanta=quanta,
        )

        if self.main is not None:
            self.main.inputs.append(x)

        if self.quant_node is not None:
            self.quant_node.inputs[f"x{len(self.quant_node.inputs)}"] = x
            self.quant_node.outputs.append(x)

        self.arith.inputs.append(x)

        return x

    def add_inputs_like(
        self, inputs: list[TensorProto], copy_names=True
    ) -> list[TensorProto]:
        """Adds a multiple inputs to the graph, matching shapes, quantas, and datatypes for the given list of tensors.
        These new inputs are appended to the end of the list of inputs if any inputs already exist.

        Arguments:
            inputs (list[TensorProto]): list of TensorProtos to match
            copy_names (bool, optional): If True, the names are copied from this list of tensors. Default True.

        Returns:
            list[TensorProto]: list of input tensors
        """
        new_inputs = []
        for x in inputs:
            x_new = self.add_input(
                channels=x.shape[0],
                quanta=x.quanta,
                precision=x.dtype,
                name=x.name if copy_names else None,
            )
            new_inputs.append(x_new)

        return new_inputs

    def add_inputs_from_graph(
        self, graph: GraphProto, copy_names=True
    ) -> list[TensorProto]:
        """Adds a multiple inputs to the current graph, like the inputs to the provided graph.
        These new inputs are appended to the end of the list of inputs if any inputs already exist.

        Arguments:
            graph (GraphProto): graph to create inputs like
            copy_names (bool, optional): If True, the names are copied from this list of tensors. Default True.

        Returns:
            list[TensorProto]: list of input tensors
        """
        arith = graph.subgraphs.get("ARITH", graph)
        inputs = arith.inputs
        return self.add_inputs_like(inputs, copy_names=copy_names)

    def assign(self, x: TensorProto, y: TensorProto):
        assert shapes_broadcastable(x, y)
        assert x.quanta == y.quanta

        node = NodeProto(
            name=f"assign:{y.name}={x.name}",
            optype=registry_v1["assign"],
            inputs={"y": x, "x": y},
            outputs=[],
            constants={},
        )

        self.arith.add_node(node)

    def add_outputs(self, outputs: list[TensorProto], append=True):
        """Register a list of Tensors to be output from the graph.
        Note that this overwrites any pre-existing outputs if append=False
        """
        if append:
            self.arith.outputs += outputs
            if self.main is not None:
                self.main.outputs += outputs
        else:
            self.arith.outputs = outputs
            if self.main is not None:
                self.main.outputs = outputs

    def _add_sub(
        self,
        optype: Literal["add", "sub"],
        x: TensorProto,
        y: TensorProto,
        name: Optional[str] = None,
        round: bool = True,
        quanta: Optional[int] = None,
    ) -> TensorProto:
        """
        Inserts an FQIR node computing `z = x +/- y` into the current working graph.

        Args:
            optype (str): "add" or "sub"
            x (TensorProto): First input operand.
            y (TensorProto): Second input operand.
            name (str, optional): Name to give the output variable. If None, an autogenerated name is used.
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to ``max(x.quanta + x.bw, y.quanta + y.bw) - output_bw``.
        Returns:
            TensorProto: A tensor representing the sum/difference `z = x +/- y`.

        Raises:
            FQIRShapeError: If the input tensors cannot be broadcast together.
        """
        graph = self.arith

        q_x = x.quanta
        q_y = y.quanta

        x_bw = get_bw(x.dtype)
        y_bw = get_bw(y.dtype)
        z_bw = get_bw(self.output_precision)

        q_z = (
            quanta
            if quanta is not None
            else get_add_sub_quanta(x_bw, q_x, y_bw, q_y, z_bw)
        )

        if not shapes_broadcastable(x, y):
            raise FQIRShapeError(
                f"Incompatible shapes for addition: {x.shape} and {y.shape}"
            )

        if name is None:
            name = autogen_name(prefix="add")

        z = TensorProto(
            name=name,
            shape=broadcasted_shape(x, y),
            dtype=self.output_precision,
            value=None,
            quanta=q_z,
        )

        # determine shift-amounts
        q_buff = max(q_x, q_y)
        shamt_x = q_x - q_buff
        shamt_y = q_y - q_buff
        shamt_z = q_buff - q_z

        node = NodeProto(
            name=f"{optype}.{x.name}.{y.name}",
            optype=registry_v1[f"vv{optype}"],
            inputs={"x": x, "y": y},
            outputs=[z],
            constants={
                "rounded": round,
                "shamt_x": shamt_x,
                "shamt_y": shamt_y,
                "shamt_bwred": shamt_z,
                "bw_x": get_bw(x.dtype),
                "bw_y": get_bw(y.dtype),
                "bw": get_bw(z.dtype),
            },
        )

        graph.add_node(node)

        return z

    def _add_float(
        self,
        x: TensorProto,
        y: float,
        round: bool = True,
        quanta: Optional[int] = None,
    ) -> TensorProto:
        """
        Inserts an FQIR node computing `z = x + y` into the current working graph, where y is a float scalar that has been quantized.

        Args:
            x (TensorProto): First input operand.
            y (float): Second input, a scalar constant float.
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to max(x.quanta, y.quanta).
        Returns:
            TensorProto: A tensor representing the sum `z = x + y`.
        """
        if y == 0:
            return x

        graph = self.arith

        bw_y = min(get_bw(self.output_precision), MAX_IMM_BITS)
        y, q_y = quantize(y, bits=bw_y)

        q_x = x.quanta
        bw_x = get_bw(x.dtype)
        bw_out = get_bw(self.output_precision)

        if quanta is not None:
            q_z = quanta
        else:
            mv_out = abs(y) * 2**q_y + 2 ** (q_x + bw_x - 1)
            _, q_z = quantize(mv_out, bw_out)

        name = autogen_name(prefix="addi")

        z = TensorProto(
            name=name,
            shape=x.shape,
            dtype=self.output_precision,
            value=None,
            quanta=q_z,
        )

        # determine shift-amounts
        q_buff = max(q_x, q_y)
        shamt_x = q_x - q_buff
        shamt_y = q_y - q_buff
        shamt_z = q_buff - q_z

        node = NodeProto(
            name=f"add.{x.name}.{y}",
            optype=registry_v1["viadd"],
            inputs={"x": x},
            outputs=[z],
            constants={
                "y": y,
                "rounded": round,
                "shamt_x": shamt_x,
                "shamt_y": shamt_y,
                "shamt_bwred": shamt_z,
                "bw_x": get_bw(x.dtype),
                "bw_y": get_bw(self.output_precision),
                "bw": get_bw(z.dtype),
            },
        )

        graph.add_node(node)

        return z

    def add(
        self,
        x: TensorProto | float,
        y: TensorProto | float,
        round: bool = True,
        quanta: Optional[int] = None,
    ):
        """
        Inserts an FQIR node computing `z = x + y` into the graph.

        Args:
            x (TensorProto | float): First input operand.
            y (TensorProto | float): Second input operand.
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to ``max(x.quanta + x.bw, y.quanta + y.bw) - output_bw``.
        Returns:
            TensorProto: A tensor representing the sum `z = x + y`.

        Raises:
            FQIRShapeError: If the input tensors cannot be broadcast together.
        """
        if isinstance(x, TensorProto):
            if isinstance(y, TensorProto):
                return self._add_sub("add", x, y, None, round, quanta)
            else:
                return self._add_float(x, y, round, quanta)
        else:
            if isinstance(y, TensorProto):
                return self._add_float(y, x, round, quanta)
            else:
                raise ValueError(
                    f"One of x or y should be a TensorProto, got ({type(x)}, {type(y)})"
                )

    def sub(
        self,
        x: TensorProto,
        y: TensorProto,
        round: bool = True,
        quanta: Optional[int] = None,
    ) -> TensorProto:
        """
        Inserts an FQIR node computing `z = x - y` into the graph.

        This must be called inside a `working_graph` context manager.

        Args:
            x (TensorProto): First input operand.
            y (TensorProto): Second input operand.
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to ``max(x.quanta + x.bw, y.quanta + y.bw) - output_bw``.

        Returns:
            TensorProto: A tensor representing the difference `z = x - y`.

        Raises:
            FQIRShapeError: If the input tensors cannot be broadcast together.
        """
        if isinstance(x, TensorProto):
            if isinstance(y, TensorProto):
                return self._add_sub("sub", x, y, None, round, quanta)
            else:
                return self._add_float(x, -y, round, quanta)
        else:
            if isinstance(y, TensorProto):
                neg_y = self.multiply(y, -1, round, quanta=x.quanta)
                return self.add(neg_y, x, round, quanta)
            else:
                raise ValueError(
                    f"One of x or y should be a TensorProto, got ({type(x)}, {type(y)})"
                )

    def _multiply(
        self,
        x: TensorProto,
        y: TensorProto,
        round: bool = True,
        quanta: Optional[int] = None,
    ):
        """
        Inserts an FQIR node computing `z = x * y` into the graph.

        Args:
            x (TensorProto): First input operand.
            y (TensorProto): Second input operand
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to `x.quanta + y.quanta - bw_out`.
        Returns:
            TensorProto: A tensor representing the product `z = x * y`.
        """
        graph = self.arith

        q_x = x.quanta
        q_y = y.quanta

        assert shapes_broadcastable(x, y)

        bw = get_bw(self.output_precision)
        bw_x = get_bw(x.dtype)
        bw_y = get_bw(y.dtype)

        q_z = quanta if quanta is not None else q_x + q_y + bw_x + bw_y - bw

        name = autogen_name(prefix="mul")

        z = TensorProto(
            name=name,
            shape=broadcasted_shape(x, y),
            dtype=self.output_precision,
            value=None,
            quanta=q_z,
        )

        # determine shift-amounts
        shamt_z = q_x + q_y - q_z

        node = NodeProto(
            name=f"mul.{x.name}.{y.name}",
            optype=registry_v1["vvmul"],
            inputs={"x": x, "y": y},
            outputs=[z],
            constants={"shamt_bwred": shamt_z, "bw": bw, "rounded": round},
        )

        # insert the node after the creation ops for x and y
        graph.add_node(node)

        return z

    def _multiply_by_float(
        self,
        x: TensorProto,
        multiplier: float,
        round: bool = True,
        quanta: Optional[int] = None,
    ):
        """
        Inserts an FQIR node computing `z = x * y` into the current working graph, where y is a float scalar that has been quantized.

        Args:
            x (TensorProto): First input operand.
            y (float): Second input, a scalar constant float.
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to `x.quanta + y.quanta - bw_out`.
        Returns:
            TensorProto: A tensor representing the product `z = x * y`.
        """
        graph = self.arith

        q_x = x.quanta
        bw = get_bw(self.output_precision)

        y, q_y = quantize(multiplier, min(bw, MAX_IMM_BITS))

        if quanta is not None:
            q_z = quanta
        else:
            mv = abs(multiplier) * 2 ** (q_x + get_bw(x.dtype) - 1)
            _, q_z = quantize(mv, bw)

        name = autogen_name(prefix="muli")

        z = TensorProto(
            name=name,
            shape=x.shape,
            dtype=self.output_precision,
            value=None,
            quanta=q_z,
        )

        # determine shift-amounts
        shamt_z = q_x + q_y - q_z

        node = NodeProto(
            name=f"mul.{x.name}.{multiplier:3E}",
            optype=registry_v1["vimul"],
            inputs={"x": x},
            outputs=[z],
            constants={"y": y, "shamt_bwred": shamt_z, "bw": bw, "rounded": round},
        )

        # insert the node after the creation op for x
        graph.add_node(node)

        return z

    def multiply(
        self,
        x: TensorProto | float,
        y: TensorProto | float,
        round: bool = True,
        quanta: Optional[int] = None,
    ):
        """
        Inserts an FQIR node computing `z = x * y` into the graph.

        Args:
            x (TensorProto | float): First input operand.
            y (TensorProto | float): Second input operand
            round (bool, optional): Whether to enable rounding on right shifts. Defaults to True.
            quanta (int, optional): Explicit quanta to assign to the output tensor.
                If None, defaults to `x.quanta + y.quanta - bw_out`.
        Returns:
            TensorProto: A tensor representing the product `z = x * y`.
        """
        if isinstance(x, TensorProto):
            if isinstance(y, TensorProto):
                return self._multiply(x, y, round, quanta)
            else:
                return self._multiply_by_float(x, y, round, quanta)
        else:
            if isinstance(y, TensorProto):
                return self._multiply_by_float(y, x, round, quanta)
            else:
                raise ValueError(
                    f"One of x or y should be a TensorProto, got ({type(x)}, {type(y)})"
                )

    def matmul(
        self,
        weight: TensorProto,
        x: TensorProto,
        round=True,
        quanta: int = None,
    ):
        """Performs a matrix-vector product

        Arguments:
            weight (TensorProto): a 2D weight matrix
            x (TensorProto): 1D vector
            round (bool, optional): if True, uses round-nearest rather than floor-rounding behavior.
                Default True.
            quanta (int, optional): quanta, optional. If not provided, quanta will be optimized
                (TODO).
        """
        assert len(weight.shape) == 2
        assert len(x.shape) == 1
        assert x.shape[0] == weight.shape[1]

        bw_in = get_bw(x.dtype)
        bw_out = get_bw(self.output_precision)

        if bw_in in [8, 16] and bw_out in [8, 16]:
            q_x = x.quanta
            q_w = weight.quanta

            if quanta is None:
                raise NotImplementedError(
                    "need to implement automatic output quanta for `matmul`"
                )

            else:
                q_z = quanta

            y = TensorProto(
                name=autogen_name("matmul"),
                dtype=self.output_precision,
                shape=[weight.shape[0]],
                quanta=q_z,
            )

            shamt_z = q_x + q_w - q_z

            node = NodeProto(
                name=f"matmul.{x.name}.{weight.name}",
                optype=registry_v1["matmul"],
                inputs={"x": weight, "y": x},
                outputs=[y],
                constants={"shamt_bwred": shamt_z, "bw_out": bw_out, "rounded": round},
            )

            self.arith.add_node(node)

            return y

        else:
            x_lo, x_hi = self._precision_split(x, [13, 12], ["int16", "int16"])
            with self.with_precision("int16") as writer:
                y_lo = writer.matmul(weight, x_lo, round=round, quanta=quanta)
                y_hi = writer.matmul(weight, x_hi, round=round, quanta=quanta + 10)
            y = self.add(y_lo, y_hi, round=round, quanta=quanta)
            return y

    def split(self, x: TensorProto, split_sizes: list[int]) -> list[TensorProto]:
        """Split a tensor

        Arguments:
            x (TensorProto): input tensor
            split_size (list[int]): size of each section

        Returns:
            list[TensorProto]: list of each split tensor
        """
        assert sum(split_sizes) == x.shape[0]

        slices = []
        for size in split_sizes:
            slices.append(
                TensorProto(
                    name=autogen_name("split"),
                    shape=[size],
                    dtype=x.dtype,
                    quanta=x.quanta,
                )
            )

        node = NodeProto(
            name=autogen_name("split_op"),
            optype=registry_v1["split"],
            inputs={"x": x},
            outputs=slices,
            constants={"lengths": split_sizes, "dim": -1},
        )
        self.arith.add_node(node)
        return slices

    def gt0(self, x: TensorProto) -> TensorProto:
        """Elementwise greater-than-zero operation, returning a tensor of 0/1"""

        bw = get_bw(x.dtype)
        if bw in [8, 16] or self.disable_gt0_decomp:
            name = autogen_name("gt0")
            y = TensorProto(name=name, dtype="fqint16", shape=x.shape, quanta=0)
            node = NodeProto(
                name=f"gt0.{x.name}",
                optype=registry_v1["gt0"],
                inputs={"x": x},
                outputs=[y],
                constants={"bw": 16},
            )

            self.arith.add_node(node)
            return y

        else:
            x_lo, x_hi = self._precision_split(x, [9, 16], ["int16", "int16"])

            with self.with_precision("int16") as writer:
                hi_gt0 = writer.gt0(x_hi)
                lo_gt0 = writer.gt0(x_lo)
                hi_eq0 = writer.eq(x_hi, 0)
                y = writer.logical_or(
                    hi_gt0,
                    writer.logical_and(lo_gt0, hi_eq0),
                    name=autogen_name("decomp_gt0"),
                )

            return y

    def gt(self, x: TensorProto | float, y: TensorProto | float) -> TensorProto:
        """Elementwise greater-than between x and y, returning a tensor of 0/1"""
        if isinstance(x, TensorProto):
            if isinstance(y, TensorProto):
                x_min_y = self.sub(x, y)
            else:
                x_min_y = self._add_float(x, -y)
        else:
            if isinstance(y, TensorProto):
                x_min_y = self._add_float(
                    self.multiply(y, -1, quanta=y.quanta), x, quanta=y.quanta
                )
            else:
                raise NotImplementedError(
                    "x or y must be a TensorProto, got both float"
                )
        return self.gt0(x_min_y)

    def ge(self, x: TensorProto | float, y: TensorProto | float) -> TensorProto:
        """Elementwise greater-than-or-equal between x and y, returning a tensor of 0/1"""
        return self.logical_not(self.lt(x, y))

    def lt(self, x: TensorProto | float, y: TensorProto | float) -> TensorProto:
        """Elementwise less-than between x and y, returning a tensor of 0/1"""
        return self.gt(y, x)

    def le(self, x: TensorProto, y: TensorProto | float) -> TensorProto:
        """Elementwise less-than-or-equal between x and y, returning a tensor of 0/1"""
        return self.logical_not(self.gt(x, y))

    def eq(self, x: TensorProto | float, y: TensorProto | float):
        """Elementwise equality operation between x and y, returning a tensor of 0/1"""
        return self.logical_and(self.ge(x, y), self.le(x, y))

    def ne(self, x: TensorProto | float, y: TensorProto | float):
        """Elementwise not-equal operation between x and y, returning a tensor of 0/1"""
        return self.logical_or(self.gt(x, y), self.gt(y, x))

    def masked_construct(
        self,
        condition: TensorProto,
        value_true: TensorProto | float,
        value_false: TensorProto | float,
        quanta: Optional[int] = None,
    ) -> TensorProto:
        """
        Masked construct selects between `value_true` and `value_false` to construct its
        output. Similar to PyTorch's masked_fill operation

            y[n] = {value_true[n]; condition[n] == True
                   {value_false[n]; condition[n] == False

        Arguments:
            condition (TensorProto): a boolean 0/1 tensor, e.g. from a comparison op like :attr:`FQIRWriter.gt`.
            value_true (TensorProto | float): value where the condition is true
            value_false (TensorProto | float): value where the condition is false
            quanta (int, Optional): optional integer quanta, default None, in which case the quanta
                is optimized as max(quanta(value_true), quanta(value_false))
        """
        assert condition.quanta == 0
        if quanta is None:
            quanta = max(value_true.quanta, value_false.quanta)
        v_true_msk = self.multiply(value_true, condition, quanta=quanta)
        v_false_msk = self.multiply(
            value_false, self.logical_not(condition), quanta=quanta
        )
        return self.add(v_true_msk, v_false_msk, quanta=quanta)

    def relu(
        self, x: TensorProto, name: Optional[str] = None, quanta: int = None
    ) -> TensorProto:
        """Performs a relu"""
        if name is None:
            name = autogen_name("relu")

        if quanta is None:
            quanta = x.quanta

        y = TensorProto(name, dtype=x.dtype, shape=x.shape, quanta=quanta)
        node = NodeProto(
            name=autogen_name("op.relu"),
            optype=registry_v1["relu"],
            inputs={"x": x},
            outputs=[y],
            constants={},
        )
        self.arith.add_node(node)
        return y

    def abs(self, x: TensorProto, quanta: int = None) -> TensorProto:
        """absolute value"""
        x_pos = self.relu(x)
        x_neg = self.relu(self.multiply(x, -1))
        y = self.add(x_pos, x_neg, quanta=quanta)
        return y

    def maximum(self, x: TensorProto, y: TensorProto) -> TensorProto:
        """Elementwise maximum between x and y"""
        q = max(x.quanta, y.quanta)
        diff = self.sub(x, y, quanta=q + 1)
        relu_diff = self.relu(diff, quanta=q + 1)
        res = self.add(y, relu_diff, quanta=q)
        return res

    def minimum(self, x: TensorProto, y: TensorProto) -> TensorProto:
        """Elementwise minimum between x and y"""
        q = max(x.quanta, y.quanta)
        diff = self.sub(y, x, quanta=q + 1)
        relu_diff = self.relu(diff, quanta=q + 1)
        res = self.sub(y, relu_diff, quanta=q)
        return res

    def cat(self, tensors: list[TensorProto]) -> TensorProto:
        """Concatenate a list of tensors"""
        if len(tensors) == 0:
            raise ValueError("Nothing to concatenate")
        elif len(tensors) == 1:
            return tensors[0]

        quantas = set([x.quanta for x in tensors])
        if None in quantas:
            quantas.remove(None)
        if len(quantas) != 1:
            raise ValueError("inputs do not have matching quantas")

        dtypes = set([x.dtype for x in tensors])
        if len(dtypes) != 1:
            raise ValueError("inputs do not have matching dtypes")

        out = TensorProto(
            name=autogen_name("cat"),
            dtype=next(iter(dtypes)),
            shape=[sum([x.shape[0] for x in tensors])],
            quanta=next(iter(quantas)),
        )

        node = NodeProto(
            name=autogen_name("cat_op"),
            optype=registry_v1["cat"],
            inputs={f"x{i}": x for i, x in enumerate(tensors)},
            outputs=[out],
            constants={"dim": -1},
        )

        self.arith.add_node(node)
        return out

    def rotate(self, buffer: TensorProto, x: TensorProto, insert_end: bool = True):
        """Rotate new values into a given tensor, e.g. for a circular buffer

        Arguments:
            buffer (TensorProto): buffer containing past values
            x (TensorProto): vector of new values
            insert_end (bool, Optional): if True, inserts the new elements to the end of the
                buffer, otherwise inserts them at the beginning.

        """
        n_insert = x.shape[0]
        b_size = buffer.shape[0]

        if x.quanta != buffer.quanta:
            raise ValueError("Quanta mismatch between buffer and x")
        if n_insert >= b_size:
            raise ValueError("x is larger than the buffer, cannot be inserted.")

        if insert_end:
            _, buff_rem = self.split(buffer, [n_insert, b_size - n_insert])
            return self.cat([buff_rem, x])
        else:
            buff_rem, _ = self.split(buffer, [b_size - n_insert, n_insert])
            return self.cat([x, buff_rem])

    def pad(
        self, x: TensorProto, before: int, after: int, value: int = 0
    ) -> TensorProto:
        """Performs padding

        Arguments:
            x (TensorProto): tensor to pad
            before (int): number of padding elements to add at the beginning of the tensor
                (before element 0)
            after (int): number of padding elements to add to the end of the tensor (after element -1)
        """
        if before == 0 and after == 0:
            return x

        tensors_to_cat = []
        if before != 0:
            bef_value = np.ones(before, dtype=np.int32) * value
            bef_tensor = self.add_parameter(
                bef_value, quanta=x.quanta, precision=x.dtype
            )
            tensors_to_cat.append(bef_tensor)

        tensors_to_cat.append(x)

        if after != 0:
            aft_value = np.ones(after, dtype=np.int32) * value
            aft_tensor = self.add_parameter(
                aft_value, quanta=x.quanta, precision=x.dtype
            )
            tensors_to_cat.append(aft_tensor)

        return self.cat(tensors_to_cat)

    def _pad_power2(self, x: TensorProto, pad_value: float):
        n = x.shape[0]
        n_padded = 2 ** (int(math.ceil(math.log2(n))))
        n_padding = n_padded - n
        if n_padding != 0:
            x = self.pad(x, before=0, after=n_padding, value=pad_value)
        return x

    def _tree_reduce(self, x: TensorProto, ewise_operation, pad_value: float):
        """
        Base method to generate a binary tournament for a reduction operation.
        """
        x = self._pad_power2(x, pad_value)

        while x.shape[0] > 1:
            curr_n = x.shape[0]
            a, b = self.split(x, [curr_n // 2, curr_n // 2])
            x = ewise_operation(a, b)

        return x

    def argmax(self, x: TensorProto):
        """Computes the argmax of tensor x"""
        pad_value = -(2 ** (x.quanta)) * 2 ** (get_bw(x.dtype) - 1)
        x = self._pad_power2(x, pad_value)

        ids = self.add_parameter(
            np.arange(x.shape[0], dtype=np.int32), precision="fqint16", quanta=0
        )
        while x.shape[0] > 1:
            curr_n = x.shape[0]
            x_a, x_b = self.split(x, [curr_n // 2, curr_n // 2])
            ids_a, ids_b = self.split(ids, [curr_n // 2, curr_n // 2])

            sel_a = self.ge(x_a, x_b)
            ids = self.masked_construct(sel_a, ids_a, ids_b)
            x = self.masked_construct(sel_a, x_a, x_b)

        return ids

    def argmin(self, x: TensorProto):
        """Computes the argmin of tensor x"""
        pad_value = 2 ** (x.quanta) * 2 ** (get_bw(x.dtype) - 1) - 1
        x = self._pad_power2(x, pad_value)

        ids = self.add_parameter(
            np.arange(x.shape[0], dtype=np.int32), precision="fqint16", quanta=0
        )
        while x.shape[0] > 1:
            curr_n = x.shape[0]
            x_a, x_b = self.split(x, [curr_n // 2, curr_n // 2])
            ids_a, ids_b = self.split(ids, [curr_n // 2, curr_n // 2])

            sel_a = self.le(x_a, x_b)
            ids = self.masked_construct(sel_a, ids_a, ids_b)
            x = self.masked_construct(sel_a, x_a, x_b)

        return ids

    def max(self, x: TensorProto):
        """maximum reduction"""
        pad_value = -(2 ** (x.quanta)) * 2 ** (get_bw(x.dtype) - 1)
        return self._tree_reduce(x, self.maximum, pad_value)

    def min(self, x: TensorProto):
        """minimum reduction"""
        pad_value = 2 ** (x.quanta) * (2 ** (get_bw(x.dtype) - 1) - 1)
        return self._tree_reduce(x, self.minimum, pad_value)

    def sum(self, x: TensorProto, quanta: int = None, method="tree"):
        """sum reduction

        Arguments:
            x (TensorProto): input tensor
            quanta (int, optional): if None, automatically selects a conservative
                output quanta to avoid saturation.
            method (str, optiona): "tree" or "matrix", default "tree"
        """
        if quanta is None:
            quanta = x.quanta + int(math.ceil(math.log2(x.shape[0])))
        if method == "tree":
            return self._tree_reduce(x, partial(self.add, quanta=quanta), pad_value=0)
        elif method == "matrix":
            reduce_matrix = self.add_parameter(
                np.ones([1, x.shape[0]]), precision="fqint8"
            )
            y = self.matmul(reduce_matrix, x, quanta=quanta)
            return y
        else:
            raise ValueError(f"reduce_sum method={method} is not defined.")

    def mean(self, x: TensorProto, quanta: int = None, method="tree"):
        """mean reduction

        Arguments:
            x (TensorProto): input tensor
            quanta (int, optional): if None, automatically selects a conservative
                output quanta to avoid saturation.
            method (str, optiona): "tree" or "matrix", default "tree"
        """
        if quanta is None:
            quanta = x.quanta
        if method == "tree":
            one_over_n = 1 / x.shape[0]
            x = self.multiply(x, one_over_n, quanta=x.quanta)
            return self._tree_reduce(x, partial(self.add, quanta=quanta), pad_value=0)
        elif method == "matrix":
            reduce_matrix = self.add_parameter(
                np.ones([1, x.shape[0]]) / x.shape[0], precision="fqint8"
            )
            y = self.matmul(reduce_matrix, x, quanta=quanta)
            return y
        else:
            raise ValueError(f"reduce_mean method={method} is not defined.")

    def dot(self, x: TensorProto, y: TensorProto, quanta: int = None, method="tree"):
        """dot-product reduction between two vectors

        Arguments:
            x (TensorProto): first input tensor
            y (TensorProto): second input tensor
            quanta (int, optional): if None, automatically selects a conservative
                output quanta to avoid saturation.
            method (str, optiona): "tree" or "matrix", default "tree"
        """
        xy = self.multiply(x, y)
        return self.sum(xy, quanta=quanta, method=method)

    def prod(self, x: TensorProto):
        """product reduction (the product of each element of )

        Arguments:
            x (TensorProto): input tensor
        """
        return self._tree_reduce(x, self.multiply, pad_value=2**x.quanta)

    def all(self, x: TensorProto):
        """logical_all reduction

        Arguments:
            x (TensorProto): input tensor
        """
        return self._tree_reduce(x, self.logical_and, pad_value=1)

    def any(self, x: TensorProto):
        """logical_any reduction

        Arguments:
            x (TensorProto): input tensor
        """
        return self._tree_reduce(x, self.logical_or, pad_value=0)

    def logical_and(self, x: TensorProto, y: TensorProto):
        """elementwise-and between two input tensors

        Arguments:
            x (TensorProto): first input tensor
            y (TensorProto): second input tensor
        """
        # hack: use the product
        return self.multiply(x, y, quanta=0)

    def sign(self, x: TensorProto):
        """sign operation, returns -1 or +1"""
        gt0 = self.gt0(x)
        two_gt0 = self.multiply(gt0, 2, quanta=-13)
        sgn = self._add_float(two_gt0, -1, quanta=-14)
        return sgn

    def logical_not(self, x: TensorProto, name: Optional[str] = None):
        """logical_not operation

        Arguments:
            x (TensorProto): input tensor
        """
        ### SOMETHING WEIRD IS HAPPENING HERE --> NEEDS SOME CAREFUL TESTING!
        # hack: 1 - x
        neg_x = self.multiply(x, -1, quanta=0)
        y = TensorProto(
            name=name if name is not None else autogen_name("logical_not"),
            dtype=x.dtype,
            shape=x.shape,
            quanta=0,
        )
        node = NodeProto(
            name=autogen_name("add1"),
            optype=registry_v1["viadd"],
            inputs={"x": neg_x},
            outputs=[y],
            constants={
                "y": 1,
                "rounded": False,
                "shamt_x": 0,
                "shamt_y": 0,
                "shamt_bwred": 0,
                "bw_x": get_bw(x.dtype),
                "bw_y": get_bw(x.dtype),
                "bw": get_bw(y.dtype),
            },
        )
        self.arith.add_node(node)
        return y

    def logical_or(self, x: TensorProto, y: TensorProto, name: Optional[str] = None):
        """elementwise-or between two input tensors

        Arguments:
            x (TensorProto): first input tensor
            y (TensorProto): second input tensor
        """
        if name is None:
            name = autogen_name("logical_or")
        add_xy = self.add(x, y, quanta=0)
        res = self.gt0(add_xy)
        return res

    def logical_xor(self, x: TensorProto, y: TensorProto, name: Optional[str] = None):
        """elementwise-xor between two input tensors

        Arguments:
            x (TensorProto): first input tensor
            y (TensorProto): second input tensor
        """
        if name is None:
            name = autogen_name("logical_xor")
        x_ny = self.logical_and(x, self.logical_not(y))
        y_nx = self.logical_and(y, self.logical_not(x))
        res = self.logical_or(x_ny, y_nx)
        return res

    # convenience methods:
    def complex_multiply(
        self,
        x_re: TensorProto,
        x_im: TensorProto,
        y_re: TensorProto,
        y_im: TensorProto,
        round: bool = True,
        quanta: Optional[int] = None,
    ) -> tuple[TensorProto, TensorProto]:
        """Convenience wrapper around complex multiplication"""
        re_prime = self.sub(
            self.multiply(x_re, y_re, round=round, quanta=quanta),
            self.multiply(x_im, y_im, round=round, quanta=quanta),
            round=round,
            quanta=quanta,
        )
        im_prime = self.add(
            self.multiply(x_re, y_im, round=round, quanta=quanta),
            self.multiply(x_im, y_re, round=round, quanta=quanta),
            round=round,
            quanta=quanta,
        )

        return re_prime, im_prime

    def _raw_lut(
        self,
        x: TensorProto,
        function: Callable[[np.ndarray], tuple[np.ndarray]],
        name: str = None,
    ):
        if get_bw(x.dtype) != 8:
            raise ValueError(
                f"Cannot call raw_lut on an input of precision {x.dtype}, must be int8"
            )

        vals = np.arange(-128, 128) * 2 ** (x.quanta)
        f_x = function(vals)
        f_x[np.isnan(f_x)] = 0
        f_x[np.isinf(f_x)] = 0

        bits_out = get_bw(self.output_precision)
        if bits_out not in [8, 16]:
            raise ValueError("output_precision must be in int8 or int16 for raw_lut.")

        f_x, q_out = quantize(f_x, bits=get_bw(self.output_precision))

        if name is None:
            name = function.__name__
        table = Table(np.arange(-128, 128, dtype=np.int8), f_x, name=name)

        y = TensorProto(
            name=autogen_name("lut"),
            dtype=self.output_precision,
            quanta=q_out,
            shape=x.shape,
        )

        node = NodeProto(
            name=f"call_{name}",
            optype=registry_v1["lut"],
            inputs={"x": x},
            constants={
                "shamt_address": 0,
                "bw_address": 8,
                "table": table,
                "function": name,
            },
            outputs=[y],
        )

        self.arith.add_node(node)

        return y

    def _precision_split(
        self, x: TensorProto, bits_out: list[int], precs: list[str]
    ) -> list[TensorProto]:
        """Creates a precision-split node, breaking a tensor into subtensors carrying
        msbs and lsbs of the original variable.

        Arguments:
            x (TensorProto): Tensor to split precision
            bits_out (list[int]): bits per subtensor, low to high
            precs (list[str]): precisions per subtensor, low to high

        Example:

            break an int16 tensor into an i8 address (top 8 bits) and i16 remainder (holding
            8 lsbs and a redundent sign bit)

            y_rem, y_addr = _precision_split(x, bits_out=[9, 8], precs=["int16", "int8"])

        """

        for i, prec in enumerate(precs):
            if prec.startswith("int"):
                prec = "fq" + prec
                precs[i] = prec

        assert len(bits_out) == len(precs)

        bw_out = sum(bits_out) - len(bits_out) + 1
        bw_in = get_bw(x.dtype)

        d_bw = bw_in - bw_out

        outs = []
        q_in = x.quanta
        q_out = q_in + d_bw
        q_offset = 0
        for bw, prec in zip(bits_out, precs):
            y = TensorProto(
                name=autogen_name("prec_split"),
                dtype=prec,
                shape=x.shape,
                quanta=q_out + q_offset,
            )
            q_offset += bw - 1

            assert bw <= get_bw(prec)

            outs.append(y)

        node = NodeProto(
            name=autogen_name("prec_split_node"),
            optype=registry_v1["gmac_v2"],
            constants={
                "shamts_vv": [],
                "shamts_vi": [-d_bw],
                "immediates_vi": [1],
                "bits_out": bits_out,
            },
            inputs={"x_vi_0": x},
            outputs=outs,
        )

        self.arith.add_node(node)

        return outs

    def interpolating_lut(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
    ):
        bw = get_bw(self.output_precision)
        rem_bits = min(bw - 8 + 1, 16)

        if d_func is None:
            dx = 2 ** (x.quanta + rem_bits)
            d_func = lambda v: (func(v + dx) - func(v)) / dx

        rem, addr = self._precision_split(x, [rem_bits, 8], ["int16", "int8"])
        with self.with_precision("int16") as writer:
            f_x = writer._raw_lut(addr, func, name=name)
            df_x = writer._raw_lut(
                addr, d_func, name=f"{name}_deriv" if name is not None else None
            )

        if bw <= 16:
            q_out = f_x.quanta
        else:
            q_out = f_x.quanta - bw + 16

        scaled_df = self.multiply(df_x, rem, quanta=q_out)
        y = self.add(f_x, scaled_df, quanta=q_out)
        return y

    def _log_identity_tilut(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
    ):
        if self.act_precision == "int16":
            return self._log_identity_tilut_i16(x, func, d_func, name)
        elif self.act_precision == "int24":
            return self._log_identity_tilut_i24(x, func, d_func, name)
        else:
            raise NotImplementedError(
                "_log_identity_tilut only supports int16 and int24 precision at this time"
            )

    def _log_identity_tilut_i16(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
    ):
        """
        Compute a log using a telescoping-interpolating lookup table.

        Arguments:
            x (TensorProto): input vector
            func (callable): must be a log function, e.g. np.log, np.log2, np.log10, etc.
                Must satisfy the homomorphism f(x * alpha) = f(x) + f(alpha).
                Only functions of form `f(x) = g * log(x)` satisfy this homomorphism.
            d_func (callable, optional): derivative or slope of `func`. If not provided,
                the secant method will be used to define a slope function.
            name (str, optional): name to give the function, for FQIR table annotations.

        log-identity telescoping trick:

            x' = { x;        x > 256
                 { x * 128;  x <= 128
            y' = log(x')

            y = { y';            x > 256
                { y' - log(128); x <= 128
        """
        if self.act_precision != "int16":
            raise NotImplementedError(
                "pos_domain_log_identity_tilut only supports int16 precision at this time"
            )

        q_x = x.quanta

        # x_tele = { x;      x > 256
        #          { x*128   x < 128

        # integer threshold between upper and lower telescoping input domains
        KAPPA = 256
        ALPHA = 128  # multiplier to amplify inputs in the lower telescoping domain
        not_mask = self.gt0(self._add_float(x, -(2**q_x) * KAPPA))
        mask = self.logical_not(not_mask)
        factor = self.multiply(mask, ALPHA, quanta=0)
        factor = self.add(factor, not_mask, quanta=0)
        x_tele = self.multiply(x, factor, quanta=x.quanta)

        # determine the output quanta by evaluating the function over the input domain
        x_vals = np.arange(1, 2**15) * 2**q_x
        y_vals = func(x_vals)
        _, q_out = quantize(y_vals, bits=16)

        # positive-only --> subtract an offset of -2**14 so that the input uses the full i16 range
        offset = -(2 ** (14 + q_x))
        x_tele_offset = self._add_float(x_tele, offset, quanta=q_x - 1)

        # redefine func and d_func with the offset
        def f_offset(x):
            return func(x - offset)

        if d_func is not None:

            def d_func_offset(x):
                return d_func(x - offset)

        else:
            d_func_offset = None

        # apply interpolating lut to x_tele_offset
        y_tele = self.interpolating_lut(
            x_tele_offset, f_offset, d_func=d_func_offset, name=name
        )

        # log-identity trick: subtract out f(128) from the values that were computed on f(x * 128)
        # y = { y_tele;          x > 256
        #     { y_tele - f(128); x < 256
        f_factor = -func(ALPHA)

        y = self.add(y_tele, self.multiply(mask, f_factor, quanta=q_out), quanta=q_out)

        return y

    def _log_identity_tilut_i24(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
    ):
        """
        Compute a log using a telescoping-interpolating lookup table.

        Arguments:
            x (TensorProto): input vector
            func (callable): must be a log function, e.g. np.log, np.log2, np.log10, etc.
                Must satisfy the homomorphism f(x * alpha) = f(x) + f(alpha).
                Only functions of form `f(x) = g * log(x)` satisfy this homomorphism.
            d_func (callable, optional): derivative or slope of `func`. If not provided,
                the secant method will be used to define a slope function.
            name (str, optional): name to give the function, for FQIR table annotations.

        log-identity telescoping trick:

            x' = { x;         x > 2**15
                 { x * 2**7;  2**7 < x <= 2**15
                 { x * 2**15; x <= 2**7

            y' = log(x')

            y = { y';              x > 2**15
                { y' - log(2**7);  2**7 < x <= 2**15
                { y - log(2**15);  x < 2**7
        """

        q_x = x.quanta

        # upper thresholds for the middle and low regions of the telescoping LUT
        THETA_MID = 2**15
        THETA_LOW = 2**8
        # gains for the middle and low regisions
        ALPHA_MID = 2**8
        ALPHA_LOW = 2**15

        # identify which region the input is in
        is_low = self.le(x, THETA_LOW * 2**q_x)
        is_hi = self.gt(x, THETA_MID * 2**q_x)
        is_mid = self.logical_not(self.logical_or(is_hi, is_low))

        # construct the multiplication factor
        factor = self.add(
            self.multiply(is_low, ALPHA_LOW, quanta=0),
            self.multiply(is_mid, ALPHA_MID, quanta=0),
            quanta=0,
        )
        factor = self.add(factor, is_hi, quanta=0)

        x_tele = self.multiply(x, factor, quanta=x.quanta)

        # determine the output quanta by evaluating the function over the input domain
        x_vals = 2.0 ** (np.linspace(0, 23, 10000)) * 2**q_x
        y_vals = func(x_vals)
        _, q_out = quantize(y_vals, bits=24)

        # positive-only --> subtract an offset of -2**22 so that the input uses the full i24 range
        offset = -(2 ** (22 + q_x))
        x_tele_offset = self._add_float(x_tele, offset, quanta=q_x - 1)

        # redefine func and d_func with the offset
        def f_offset(x):
            return func(x - offset)

        if d_func is not None:

            def d_func_offset(x):
                return d_func(x - offset)

        else:
            d_func_offset = None

        # apply interpolating lut to x_tele_offset
        y_tele = self.interpolating_lut(
            x_tele_offset, f_offset, d_func=d_func_offset, name=name
        )

        # log-identity trick: subtract out f(128) from the values that were computed on f(x * 128)
        # y = { y_tele;          x > 256
        #     { y_tele - f(128); x < 256
        f_low = -func(ALPHA_LOW)
        f_mid = -func(ALPHA_MID)
        _, q_low = quantize(f_low, 24)
        _, q_mid = quantize(f_mid, 24)
        f_alpha_low = self.multiply(is_low, -func(ALPHA_LOW), quanta=q_low)
        f_alpha_mid = self.multiply(is_mid, -func(ALPHA_MID), quanta=q_mid)

        y = self.add(y_tele, f_alpha_low, quanta=q_out)
        y = self.add(y, f_alpha_mid, quanta=q_out)

        return y

    def log(self, x: TensorProto, eps_int: int = 0):
        q_x = x.quanta

        if eps_int != 0:
            x = self._add_float(x, 2**q_x * eps_int)

        def f_x(x):
            x = np.maximum(x, 2**q_x)
            return np.log(x)

        return self._log_identity_tilut(x, func=f_x, d_func=None, name="log")

    def log2(self, x: TensorProto, eps_int: int = 0):
        q_x = x.quanta

        if eps_int != 0:
            x = self._add_float(x, 2**q_x * eps_int)

        def f_x(x):
            x = np.maximum(x, 2**q_x)
            return np.log2(x)

        return self._log_identity_tilut(x, func=f_x, d_func=None, name="log2")

    def log10(self, x: TensorProto, eps_int: int = 0):
        q_x = x.quanta

        if eps_int != 0:
            x = self._add_float(x, 2**q_x * eps_int)

        def f_x(x):
            x = np.maximum(x, 2**q_x)
            return np.log10(x)

        return self._log_identity_tilut(x, func=f_x, d_func=None, name="log10")

    def _pow_identity_tilut_i16(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
        kappa=256,
        alpha=128,
        pos_only=False,
    ):
        """
        Compute a power function using a telescoping-interpolating lookup table.

        Arguments:
            x (TensorProto): input vector
            func (callable): must be a power function, e.g. sqrt, rsqrt, reciprocal, x**k, etc.
                Must satisfy the homomorphism f(x * alpha) = f(x) * f(alpha).
                Only functions of form `f(x) = x^k` satisfy this homomorphism.
            d_func (callable, optional): derivative or slope of `func`. If not provided,
                the secant method will be used to define a slope function.
            name (str, optional): name to give the function, for FQIR table annotations.
            pos_only (bool, Optional): If true, will offset the domain to utilize the full
                positive and negative domain for the function.

        pow-identity telescoping trick:

            x' = { x;        x > 256
                 { x * 128;  x <= 128
            y' = pow(x', k)

            y = { y';            x > 256
                { y' / 128**k;   x <= 128
        """
        if self.act_precision != "int16":
            raise NotImplementedError(
                "pow_identity_tilut only supports int16 precision at this time"
            )

        q_x = x.quanta

        if pos_only:
            x_to_mask = x
        else:
            x_to_mask = self.abs(x)

        not_mask = self.gt0(self._add_float(x_to_mask, -(2**q_x) * kappa))
        mask = self.logical_not(not_mask)
        factor = self.multiply(mask, alpha, quanta=0)
        factor = self.add(factor, not_mask, quanta=0)

        x_tele = self.multiply(x, factor, quanta=x.quanta)

        if pos_only:
            x_vals = np.arange(0, 2**15) * 2**q_x
            y_vals = func(x_vals)

            _, q_out = quantize(y_vals, bits=16)

            offset = -(2 ** (14 + q_x))
            x_tele = self._add_float(x_tele, offset, quanta=q_x - 1)

            wrapped_func = lambda x: func(x - offset)
            if d_func is not None:
                wrapped_d_func = lambda x: d_func(x - offset)
            else:
                wrapped_d_func = None

        else:
            x_vals = np.arange(-(2**7), 2**7) * 2 ** (q_x + 8)
            y_vals = func(x_vals)
            y_vals = np.max(np.abs(y_vals)) / func(alpha)

            _, q_out = quantize(y_vals, bits=16)

            wrapped_func = func
            wrapped_d_func = d_func

        y_tele = self.interpolating_lut(x_tele, wrapped_func, wrapped_d_func, name)

        f_factor = 1 / func(alpha) - 1

        _, q_factor = quantize(f_factor, 16)
        inv_mask = self.multiply(mask, f_factor, quanta=q_factor)

        y = self.multiply(y_tele, inv_mask, quanta=q_out + 1)
        y = self.add(y, y_tele, quanta=q_out)

        return y

    def _pow_identity_tilut_i24(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
        pos_only=False,
    ):
        """
        Compute a power function using a telescoping-interpolating lookup table.

        Arguments:
            x (TensorProto): input vector
            func (callable): must be a power function, e.g. sqrt, rsqrt, reciprocal, x**k, etc.
                Must satisfy the homomorphism f(x * alpha) = f(x) * f(alpha).
                Only functions of form `f(x) = x^k` satisfy this homomorphism.
            d_func (callable, optional): derivative or slope of `func`. If not provided,
                the secant method will be used to define a slope function.
            name (str, optional): name to give the function, for FQIR table annotations.
            pos_only (bool, optional): If true, will offset the domain to utilize the full
                positive and negative domain for the function.

        pow-identity telescoping trick:

            x' = { x;         x > 2**15
                 { x * 2**7;  2**7 < x <= 2**15
                 { x * 2**15; x <= 2**7

            y' = pow(x', k)

            y = { y';              x > 2**15
                { y' / (2**7)**k;  2**7 < x <= 2**15
                { y / (2**15)**k;  x < 2**7
        """
        q_x = x.quanta

        # upper thresholds for the middle and low regions of the telescoping LUT
        THETA_MID = 2**15
        THETA_LOW = 2**8 * 1.001
        # gains for the middle and low regisions
        ALPHA_MID = 2**7
        ALPHA_LOW = 2**15

        # identify which region the input is in
        is_low = self.le(x, THETA_LOW * 2**q_x)
        is_hi = self.gt(x, THETA_MID * 2**q_x)
        is_mid = self.logical_not(self.logical_or(is_hi, is_low))

        # construct the multiplication factor
        factor = self.add(
            self.multiply(is_low, ALPHA_LOW, quanta=0),
            self.multiply(is_mid, ALPHA_MID, quanta=0),
            quanta=0,
        )
        factor = self.add(factor, is_hi, quanta=0)

        x_tele = self.multiply(x, factor, quanta=x.quanta)

        # determine the output quanta by evaluating the function over the input domain
        x_vals = 2.0 ** (np.linspace(0, 23, 10000)) * 2**q_x
        y_vals = func(x_vals)
        _, q_out = quantize(y_vals, bits=24)

        # positive-only --> subtract an offset of -2**22 so that the input uses the full i24 range
        if pos_only:
            offset = -(2 ** (22 + q_x))
            x_tele_offset = self._add_float(x_tele, offset, quanta=q_x - 1)

            # redefine func and d_func with the offset
            def f_offset(x):
                return func(x - offset)

            if d_func is not None:

                def d_func_offset(x):
                    return d_func(x - offset)

            else:
                d_func_offset = None

        else:
            x_tele_offset = x_tele
            f_offset = func
            d_func_offset = d_func

        # x_tele_offset.name = "X_TELE"

        # apply interpolating lut to x_tele_offset
        y_tele = self.interpolating_lut(
            x_tele_offset, f_offset, d_func=d_func_offset, name=name
        )

        # pow-identity trick:
        inv_f_low = 1 / func(ALPHA_LOW) - 1
        inv_f_mid = 1 / func(ALPHA_MID) - 1
        _, q_low = quantize(inv_f_low, 24)
        _, q_mid = quantize(inv_f_mid, 24)
        inv_f_alpha_low = self.multiply(is_low, inv_f_low, quanta=q_low)
        inv_f_alpha_mid = self.multiply(is_mid, inv_f_mid, quanta=q_mid)
        q_mult = max(q_low, q_mid)
        mult = self.add(inv_f_alpha_low, inv_f_alpha_mid, quanta=q_mult)
        y = self.multiply(y_tele, mult, quanta=q_out)
        y = self.add(y, y_tele, quanta=q_out)
        return y

    def _pow_identity_tilut_i24_v3(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
        pos_only=False,
    ):
        """
        Compute a power function using a telescoping-interpolating lookup table.

        Arguments:
            x (TensorProto): input vector
            func (callable): must be a power function, e.g. sqrt, rsqrt, reciprocal, x**k, etc.
                Must satisfy the homomorphism f(x * alpha) = f(x) * f(alpha).
                Only functions of form `f(x) = x^k` satisfy this homomorphism.
            d_func (callable, optional): derivative or slope of `func`. If not provided,
                the secant method will be used to define a slope function.
            name (str, optional): name to give the function, for FQIR table annotations.
            pos_only (bool, optional): If true, will offset the domain to utilize the full
                positive and negative domain for the function.

        pow-identity telescoping trick:

            x' = { x;         x > 2**15
                 { x * 2**7;  2**7 < x <= 2**15
                 { x * 2**15; x <= 2**7

            y' = pow(x', k)

            y = { y';              x > 2**15
                { y' / (2**7)**k;  2**7 < x <= 2**15
                { y / (2**15)**k;  x < 2**7
        """
        q_x = x.quanta

        # upper threshold and gain
        THETA = 2**8
        ALPHA = 2**-8

        # identify which region the input is in
        is_hi = self.gt(x, THETA * 2**q_x)
        mult = self.masked_construct(is_hi, ALPHA, 1.0, quanta=-23)
        x_tele = self.multiply(x, mult)

        x16, _ = self._precision_split(x_tele, [16, 8], ["int16", "int16"])
        with self.with_precision("int16") as writer:
            y16 = writer._pow_identity_tilut_i16(
                x16, name=name, func=func, d_func=d_func, pos_only=pos_only
            )

        # determine optimal output quanta
        x_vals = 2.0 ** (np.linspace(0, 23, 10000)) * 2**q_x
        y_vals = func(x_vals)
        _, q_out = quantize(y_vals, bits=24)

        inv_f = 1 / func(ALPHA) - 1
        _, q_f = quantize(inv_f, 24)
        inv_f_hi = self.multiply(is_hi, inv_f, quanta=q_f)

        y = self.multiply(y16, inv_f_hi, quanta=q_out)
        y = self.add(y, y16, quanta=q_out)
        return y

    def _pow_identity_tilut(
        self,
        x: TensorProto,
        func: FUNC_TYPE,
        d_func: Optional[FUNC_TYPE] = None,
        name: str = None,
        pos_only=False,
    ):
        if self.act_precision == "int16":
            return self._pow_identity_tilut_i16(
                x, func, d_func, name, pos_only=pos_only
            )
        elif self.act_precision == "int24":
            return self._pow_identity_tilut_i24_v3(
                x, func, d_func, name, pos_only=pos_only
            )
        else:
            raise NotImplementedError(
                "_pow_identity_tilut only supports int16 and int24 precision at this time"
            )

    def pow(self, x: TensorProto, power: float):
        EPS = 1
        if power == 0:
            vals = np.ones(x.shape)
            return self.add_parameter(
                vals, precision=self.output_precision, name=autogen_name("ones")
            )

        elif power == 1:
            return x

        elif power < 0:
            qx = x.quanta

            if power % 2 == 0:

                def func(x):
                    x = np.asarray(x)
                    min_mag = 2**qx * EPS
                    mask_pos = np.logical_and(x > 0, x <= min_mag)
                    x[mask_pos] = min_mag
                    mask_neg = np.logical_and(x < 0, x >= -min_mag)
                    x[mask_neg] = -min_mag

                    y = np.power(x, float(power))
                    y = np.asarray(y)
                    y[x == 0] = min_mag**-2

                    return y

            else:
                # create a safe masked version of the function, intercepting y = 0 at x = 0
                def func(x):
                    x = np.asarray(x)
                    y = np.power(x, float(power))
                    y = np.asarray(y)
                    y[x == 0] = 0
                    return y

            return self._pow_identity_tilut(
                x,
                func=func,
                d_func=None,
                name=f"pow(x, {power})",
                pos_only=power % 1 != 0,
            )

        elif power == 2:
            return self.multiply(x, x)

        elif power == 3:
            return self.multiply(self.multiply(x, x), x)

        elif power % 1 == 0:
            result = None
            pow_remaining = int(power)
            base = x
            while pow_remaining > 0:
                if pow_remaining % 2 == 1:
                    if result is not None:
                        result = self.multiply(result, base)
                    else:
                        result = x
                if pow_remaining > 1:
                    base = self.multiply(base, base)
                pow_remaining //= 2

            assert result is not None

            return result

        else:

            def func(x):
                y = np.array(np.power(x, power))
                y[np.isnan(y)] = 0
                return y

            return self._pow_identity_tilut(
                x, func=func, d_func=None, name=f"pow(x, {power})", pos_only=True
            )

    def reciprocal(self, x: TensorProto, pos_only: bool, eps_int: int = 1):
        q_x = x.quanta

        def safe_reciprocal(x):
            x = np.asarray(x)
            kappa = 2 ** (q_x) * eps_int
            mask_pos = np.logical_and(x > 0, x < kappa)
            x[mask_pos] = kappa
            mask_neg = np.logical_and(x < 0, x > -kappa)
            x[mask_neg] = -kappa

            y = np.asarray(1 / x)

            if pos_only:
                y[x == 0] = 1 / kappa
            else:
                y[x == 0] = 0

            return y

        return self._pow_identity_tilut(
            x, safe_reciprocal, name="reciprocal", pos_only=pos_only
        )

    def copy_fqir_node(self, node: NodeProto, varmap: dict[TensorProto, TensorProto]):
        """Copies an FQIR node (e.g. from a graph that is being imported), updating in-place a variable
        map to map tensors in the original graph to tensors in this new graph"""
        inputs = {name: varmap[x] for name, x in node.inputs.items()}
        outputs = []
        for x in node.outputs:
            x_prime = TensorProto(
                name=autogen_name(x.name), dtype=x.dtype, shape=x.shape, quanta=x.quanta
            )
            outputs.append(x_prime)
            varmap[x] = x_prime

        node_copy = NodeProto(
            name=autogen_name(node.name),
            optype=node.optype,
            inputs=inputs,
            outputs=outputs,
            constants=node.constants,
            subgraph=node.subgraph,
        )
        self.arith.add_node(node_copy)
        return outputs, varmap

    def inline_fqir_graph(
        self,
        graph: GraphProto,
        inputs: list[TensorProto],
        enable_quanta_matching: bool = True,
    ) -> list[TensorProto]:
        """Inserts the computation from the given FQIR graph inside of the current working graph.
        The provided set of inputs replace the original inputs from the given graph.

        Arguments:
            graph (GraphProto): FQIR graph to inline, "MAIN" or "ARITH" level.
            inputs (list[TensorProto]): list of inputs to pass into the graph. They must match
                the signature of `graph` with identical number of inputs, shapes, dtypes, and quanta. An
                error is raised otherwise.
            enable_quanta_matching (bool, optional): if True, enables insertion of rescaling nodes if quantas
                do not match. Otherwise, an error is raised if quantas mismatch.

        Returns:
            list[TensorProto]: list of outputs from the inlined graph
        """

        arith = graph.subgraphs.get("ARITH", graph)
        init = graph.subgraphs.get("INIT", None)

        # map tensors in the input graph to tensors in the current graph
        varmap: dict[TensorProto, TensorProto] = {}

        # initialize the varmap with inputs
        if len(inputs) != len(arith.inputs):
            raise ValueError(
                f"Recieved an incorrect number of inputs. Graph has {len(arith.inputs)} inputs, recieved {len(inputs)}"
            )

        for i, (x_orig, x_new) in enumerate(zip(arith.inputs, inputs)):
            if x_orig.shape != x_new.shape:
                raise ValueError(
                    f"Shape mismatch in input {i}. graph has a shape {x_orig.shape}, input tensor has shape {x_new.shape}"
                )
            if x_orig.dtype != x_new.dtype:
                raise ValueError(
                    f"dtype mismatch in input {i}. graph has a dtype {x_orig.dtype}, input tensor has dtype {x_new.dtype}"
                )

            if x_orig.quanta != x_new.quanta:
                if enable_quanta_matching:
                    x_rescaled = self.multiply(
                        x_new, 1.0, round=True, quanta=x_orig.quanta
                    )
                    x_new = x_rescaled
                else:
                    raise ValueError(
                        f"Quanta mismatch in input {i}. graph has a quanta {x_orig.quanta}, input tensor has quanta {x_new.quanta}"
                    )

            varmap[x_orig] = x_new

        # copy param tensors
        for p in arith.parameters:
            new_p = self.add_parameter(
                p.value,
                name=autogen_name(p.name),
                precision=p.dtype,
                quanta=p.quanta if p.quanta is not None else 0,
            )
            varmap[p] = new_p

        if init is not None:
            # copy init buffers
            for x in init.all_tensors():
                x_init = self.add_zeros_buffer(
                    channels=x.shape[0],
                    quanta=x.quanta,
                    name=autogen_name(x.name),
                    precision=x.dtype.split("fq")[1],
                )
                varmap[x] = x_init

        # copy arith nodes
        for node in arith.nodes:
            # this updates the varmap in-place
            self.copy_fqir_node(node, varmap)

        # return outputs
        outputs = [varmap[x] for x in arith.outputs]
        return outputs

    @contextmanager
    def for_loop_writer(
        self,
        n_iter: int,
        x_to_slice: list[TensorProto],
        x_recurse_init: list[TensorProto],
    ):
        loop_body = GraphProto(name=autogen_name("loop_body"))

        inputs = {}
        for i, x_slice in enumerate(x_to_slice):
            inputs[f"x_sliced_{i}"] = x_slice

        for i, x_recurse in enumerate(x_recurse_init):
            inputs[f"x_recurse_{i}"] = x_recurse

        loop_node = NodeProto(
            name=autogen_name("loop"),
            optype=registry_v1["loop"],
            inputs=inputs,
            outputs=[],
            constants={
                "n_iter": n_iter,
                "n_recurse": len(x_recurse_init),
                "n_sliced": len(x_to_slice),
                "n_scope": 0,
                "n_concat": 0,
                "n_final": 0,
                "block_size_sliced": [x.shape[0] // n_iter for x in x_to_slice],
                "reverse_sliced": [False] * len(x_to_slice),
                "reverse_concat": [],
            },
            subgraph=loop_body,
        )

        curr_recurses = [
            TensorProto(
                autogen_name(f"x_recurse_curr.{i}"), x.dtype, x.shape, quanta=x.quanta
            )
            for x in x_recurse_init
        ]
        curr_slices = [
            TensorProto(
                autogen_name(f"x_slice_curr.{i}"),
                x.dtype,
                [x.shape[0] // n_iter],
                quanta=x.quanta,
            )
            for x in x_to_slice
        ]

        loop_body.inputs = curr_recurses + curr_slices

        self.arith.add_node(loop_node)

        writer = LoopWriter(
            n_iter=n_iter,
            parent_node=loop_node,
            recursed_inputs=curr_recurses,
            sliced_inputs=curr_slices,
            arith=loop_body,
            init=self.init,
            act_precision=self.act_precision,
        )
        writer.disable_gt0_decomp = self.disable_gt0_decomp

        try:
            yield writer
        finally:
            writer.close()

    @contextmanager
    def with_precision(self, precision: str):
        writer = FQIRWriter(
            arith=self.arith,
            init=self.init,
            act_precision=precision,
        )
        writer.disable_gt0_decomp = self.disable_gt0_decomp
        try:
            yield writer
        finally:
            pass


class LoopWriter(FQIRWriter):
    #: number of iterations for the for-loop
    n_iter: int

    #: list of recursed inputs
    recursed_inputs: list[TensorProto]

    #: list of sliced inputs
    sliced_inputs: list[TensorProto]

    def __init__(
        self,
        n_iter: int,
        parent_node: NodeProto,
        recursed_inputs: list[TensorProto],
        sliced_inputs: list[TensorProto],
        arith: GraphProto,
        init: Optional[GraphProto],
        act_precision: str,
    ):
        super().__init__(arith, init, act_precision)
        self.n_iter = n_iter
        self.parent_node = parent_node
        self.recursed_inputs = recursed_inputs
        self.sliced_inputs = sliced_inputs

        self._cat_outs = {}
        self._final_outs = {}
        self._recurse_updates = {}

    def return_concatenated(self, x: TensorProto) -> TensorProto:
        x_concatenated = TensorProto(
            name=autogen_name("loop_concat_output"),
            dtype=x.dtype,
            shape=[x.shape[0] * self.n_iter],
            quanta=x.quanta,
        )

        self._cat_outs[x] = x_concatenated
        return x_concatenated

    def return_final(self, x: TensorProto) -> TensorProto:
        x_final = TensorProto(
            name=autogen_name("loop_final_output"),
            dtype=x.dtype,
            shape=x.shape,
            quanta=x.quanta,
        )
        self._final_outs[x] = x_final
        return x_final

    def update_recursed_state(self, x_prev: TensorProto, x_new: TensorProto):
        if x_prev not in self.recursed_inputs:
            raise ValueError(
                f"{x_prev=} not contained inside of the loop's x_recurse_init variable list."
            )
        self._recurse_updates[x_prev] = x_new

    def close(self):
        subgraph_outs = []
        loop_node_outs = []

        expected_recurse_keys = set(self.recursed_inputs)
        recurse_keys = set(list(self._recurse_updates.keys()))

        if recurse_keys != expected_recurse_keys:
            raise ValueError(
                f"Recurse keys {recurse_keys} do not match {expected_recurse_keys}. You must have a recursed variable that isn't being updated."
            )

        for x_orig in self.recursed_inputs:
            subgraph_outs.append(self._recurse_updates[x_orig])

        for x_cat_in, x_cat_out in self._cat_outs.items():
            subgraph_outs.append(x_cat_in)
            loop_node_outs.append(x_cat_out)

        for x_final_in, x_final_out in self._final_outs.items():
            subgraph_outs.append(x_final_in)
            loop_node_outs.append(x_final_out)

        self.arith.outputs = subgraph_outs
        self.parent_node.outputs = loop_node_outs

        consts = self.parent_node.constants
        consts["n_concat"] = len(self._cat_outs)
        consts["n_final"] = len(self._final_outs)
        consts["reverse_concat"] = [False] * len(self._cat_outs)
