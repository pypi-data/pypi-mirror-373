import dataclasses
from ..variables import VariableBase, TensorSignature
from .opcounters import OpCounter, OpCount
from typing import List, Dict, Any


@dataclasses.dataclass
class NodeReprSettings:
    use_var_names: bool = True
    constants_to_rep: list = dataclasses.field(default_factory=list)
    operator_symbol: str = dataclasses.field(default_factory=lambda: "")

    __annotations__ = {
        "use_var_names": bool,
        "constants_to_rep": list,
        "operator_symbol": str,
    }

    def check(self, constants):
        for k in self.constants_to_rep:
            assert k in constants, f"Constant {k} not found in constants={constants}."

    def default_repr(self, opname, inputs, outputs, constants):
        self.check(constants)
        if len(outputs) == 0:
            rep = ""
        elif len(outputs) == 1:
            rep = f"{outputs[0]} = "
        else:
            rep = f'({", ".join(str(v) for v in outputs)}) = '
        rep += opname

        num_args = len(inputs) + len(self.constants_to_rep)
        use_var_names = self.use_var_names if num_args > 1 else False

        arg_strings = []

        def arg_append(k, v):
            if use_var_names:
                arg_strings.append(f"{k}={v}")
            else:
                arg_strings.append(str(v))

        for k, v in inputs.items():
            arg_append(k, v.name)
        for k in self.constants_to_rep:
            v = constants[k]
            arg_append(k, v)
        rep += "(" + ", ".join(arg_strings) + ")"
        return rep

    def operator_repr(self, opname, inputs, outputs, constants):
        self.check(constants)
        operands = [v.name for v in inputs.values()]
        operands += [constants[k] for k in self.constants_to_rep]
        assert len(outputs) == 1
        assert len(operands) == 2
        assert len(self.operator_symbol) > 0

        return f"{outputs[0]} = {operands[0]} {self.operator_symbol} {operands[1]}"

    def repr(self, opname, inputs, outputs, constants):
        if self.operator_symbol != "":
            return self.operator_repr(opname, inputs, outputs, constants)
        else:
            return self.default_repr(opname, inputs, outputs, constants)


class NodeBase:
    """Base class for a node. Subclassed by NodeProto, YieldNode, SetNode, etc.

    Args:
        inputs (dict[str: VariableBase]): dictionary of variables; input to the node
        outputs (list[VariableBase]): list of output variables from node
        opname (str): name of the operator (used in __repr__)
        constants (dict[str: any]): dictionary of non-variable inputs to the node; i.e. attributes
            of the node
        name (str, optional): node name (not the name of the operator)
        repr_settings (NodeReprSettings, optional): Settings to use when creating a string
            representation of the node.
        opcounter (OpCounter, optional): used to estimate opcount associated with this node.
            If no opcounter is provided, the opcount is assumed to be zero.
    """

    def __init__(
        self,
        inputs: Dict[str, VariableBase],
        outputs: List[VariableBase],
        opname: str,
        constants: Dict[str, Any] = None,
        name: str = None,
        repr_settings: NodeReprSettings = None,
        opcounter: OpCounter = None,
    ):
        assert isinstance(inputs, dict)
        for k, v in inputs.items():
            if not isinstance(v, VariableBase):
                raise ValueError(f"input {k}: {v} is not a VariableBase, got {type(v)}")
        self.inputs = inputs
        assert isinstance(outputs, (list, tuple))
        assert all(isinstance(v, VariableBase) for v in outputs)
        self.outputs = outputs
        self.opname = opname
        self.constants = constants if (constants is not None) else {}
        self.name = name
        if isinstance(repr_settings, NodeReprSettings):
            self.repr_settings = repr_settings
        else:
            self.repr_settings = NodeReprSettings()
        if opcounter is not None:
            assert isinstance(opcounter, OpCounter)
        self.opcounter = opcounter

    def __repr__(self):
        return self.repr_settings.repr(
            opname=self.opname,
            inputs=self.inputs,
            outputs=self.outputs,
            constants=self.constants,
        )

    def input_signature(self) -> Dict[str, TensorSignature]:
        return {k: v.signature() for k, v in self.inputs.items()}

    def output_signature(self) -> List[TensorSignature]:
        return [v.signature() for v in self.outputs]

    def exec(self):
        """
        Should set value of output tensors, given values of input vectors.

        Most exec methods should not return any values. However, YieldNode
        yields an output value.
        """
        raise NotImplementedError(self.opname)

    def opcount(self, st_ld_pessimism: float = None) -> OpCount:
        """
        Returns an OpCount for the node.

        Args:
            st_ld_pessimism (float, optional): Probability of a store-load *not* being
                removed. Float between zero and one. If none is provided, will use the
                default of 0.5.
            input_length (int, list[int], optional): Number of input time-steps, or shape
                of input sequence (excluding feature dimension). If none is provided, will
                assume an input length of 1 (thus evaluating opcount for a single frame)
            output_length (int, list[int], optional): Number of output time-steps, or shape
                of input sequence (excluding feature dimension). If none is provided, will
                assume an input length of 1 (thus evaluating opcount for a single frame)
        """
        if self.opcounter is None:
            return OpCount()
        else:
            return self.opcounter(
                self.inputs, self.outputs, self.constants, st_ld_pessimism
            )
