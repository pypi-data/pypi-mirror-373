from .node_base import NodeBase
import textwrap
from deprecation import deprecated
import fmot
import numpy as np
from .optype_base import OpType
from ..variables import TensorProto
from typing import *

DEF_IND = "   "


class NodeProto(NodeBase):
    """Represents an operation or subgraph (but not both) in the fqir graph.

    Args:
        name (str): A name for the node. The hierarchical name of the pytorch module that generated
            this :class:`NodeProto` is reasonable,
            or :obj:`None` if there isn't a clear parent module
        optype (:class:`fqir.nodes.OpType`): An fqir operator
        inputs (dict): ``{str: TensorProto}`` Maps underlying OpType argnames to Tensors
        outputs (list[:class:`TensorProto`]): A list of output tensors from the node
        constants (dict, optional): An dictionary constant (non-tensor) arguments with keys
            matching the :class:`OpType` runtime constants
            (e.g. shift-amounts, immediates, LUT values, etc.)
        subgraph (:class:`GraphProto`, optional): A subgraph for the node to contain.
            Subgraphs are wrapped in NodeProtos for the purpose of runtime execution.
            When wrapping a subgraph, set ``optype`` to ``None``.
        sourceref (str, optional): A reference to the user's original code, or :attr:`None`
    """

    def __init__(
        self,
        name: str,
        optype: OpType,
        inputs: Dict[str, TensorProto],
        outputs: List[TensorProto],
        constants: Optional[Dict[str, Any]] = None,
        subgraph=None,
        sourceref=None,
    ):
        opname = optype.name if (optype is not None) else subgraph.name
        opcounter = optype.opcounter if (optype is not None) else None
        repr_settings = None
        if hasattr(optype, "repr_settings"):
            repr_settings = optype.repr_settings
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            opname=opname,
            constants=constants,
            name=name,
            repr_settings=repr_settings,
            opcounter=opcounter,
        )
        self.optype = optype
        self.subgraph = subgraph
        self.sourceref = sourceref
        self._tag_dependencies()

        if optype is not None:  # consistency checks
            self.optype.check_inputs_constants(self.inputs, self.constants)

    @property
    def is_subgraph(self):
        return self.optype is None

    def _tag_dependencies(self):
        # deprecated
        pass

    @property
    def docstring(self):
        """Return the docstring of the contained :class:`fqir.variables.OpType`

        Returns:
            - str: docstring of the contained :class:`fqir.variables.OpType`
            - None: if the Node does not contain an :class:`fqir.variables.OpType`
        """
        if self.optype is not None:
            return self.optype.docstring

    def runtime(self, *args, **kwargs):
        """Return the runtime of the contained :class:`fqir.variables.OpType`

        Returns:
            Runtime function (callable) or :attr:`None`
        """
        if self.optype is not None:
            self.optype._inputs = self.inputs
            self.optype._outputs = self.outputs
            if self.subgraph is not None:
                kwargs["subgraph"] = self.subgraph
            return self.optype.runtime(*args, **kwargs)

    def exec(self):
        """
        Executes the given node in the graph. Input values are pulled out of
        input variables, and output values are inserted into the output variables.
        """
        kwargs = {k: tensor.get_value() for k, tensor in self.inputs.items()}
        kwargs.update(self.constants)

        if self.subgraph is not None:
            kwargs["subgraph"] = self.subgraph

        outputs = self.runtime(**kwargs)
        if outputs is not None:
            if isinstance(outputs, np.ndarray):
                outputs = [outputs]
            for tensor, value in zip(self.outputs, outputs):
                tensor.set_value(value)

    def printout(self, constants=True, subgraph=True, indent=None, energy=False):
        """Generate a string representation of the node"""
        if self.subgraph is None:
            return super().__repr__()
        else:
            rep = super().__repr__()
            if indent is None:
                indent = "\t"
            if subgraph and (self.subgraph is not None):
                rep += "\n" + indent + "{"
                rep += textwrap.indent(
                    "\n" + self.subgraph.printout(constants, subgraph, indent, energy),
                    indent,
                )
                rep += "\n" + indent + "}"
            if energy:
                try:
                    rep += f" - {self.opcount().energy():.3E} J"
                except:
                    pass
            return rep

    def __repr__(self):
        return self.printout(constants=True)

    def seq_length_fn(self, input_length):
        return self.optype.seq_length_fn(input_length, self.constants)
