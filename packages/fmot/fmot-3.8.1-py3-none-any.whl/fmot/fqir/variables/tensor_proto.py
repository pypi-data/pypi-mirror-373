from . import VariableBase
from fmot.fqir.utils import asint
import numpy as np
import torch

BYTES_PER_ELEMENT = dict(
    fqint4=0.5, fqint8=1, fqint16=2, fqint4_fp=0.5, fqint8_fp=1, fqint16_fp=2
)


class TensorProto(VariableBase):
    """Represents a tensor in an fqir graph

    Used to represent parameters (i.e., weights and biases) or activations

    Args:
        name (str): name
        dtype (str): datatype
        shape (list): shape
        avg_sparsity (float, optional): Average number of elements that are zero
        value (ndarray, optional): Value held by the tensor--only for parameters,
            not for activations
        default_value (ndarray, optional): Default value for configuration inputs,
            e.g. those that are optional in the input signature
        quanta (int, optional): Quantization quanta for the tensor

    Attributes:
        children (set[:class:`TensorProto`]): Children :class:`TensorProto`.
            Each child has a dependency on this :class:`TensorProto`
            through a node in the graph (i.e., as a result of an operation)
        parents (set[:class:`TensorProto`]): Parent :class:`TensorProto`
            upon which this :class:`TensorProto` is dependent on via a node
            (i.e., as a result of an operation)
    """

    def __init__(
        self,
        name,
        dtype,
        shape,
        avg_sparsity=None,
        value=None,
        quanta=None,
        density_per_element=None,
        named_dims=None,
    ):
        super().__init__(name, dtype, shape)
        self.value = value
        self.avg_sparsity = avg_sparsity
        self.density_per_element = density_per_element
        self.quanta = quanta
        self.named_dims = named_dims
        self.children = set()
        self.parents = set()
        self.parent_nodes = set()
        self.seq_length = None

    def _value(self):
        if self.value is not None:
            return self.value
        parent = self._get_parent_through_optypes("transpose")
        if parent is not None:
            value = parent._value()
            if value is not None:
                return value.T
        return None

    def _get_parent_through_optypes(self, *optypes):
        if len(self.parent_nodes) == 1:
            parent = next(iter(self.parent_nodes))
            if parent.optype.name in optypes:
                return parent.inputs["x"]
        else:
            return None

    def numel(self, nonzero_only=False):
        """
        Number of elements in the TensorProto.
        Args:
            nonzero_only (bool): If True, returns the (average) number of nonzero
                elements in the tensor. Default is False.
        """
        parent = self._get_parent_through_optypes("transpose", "reshape")
        if parent is not None:
            return parent.numel(nonzero_only=nonzero_only)

        N = np.prod(self.shape)
        if not nonzero_only:
            return N
        elif self.value is None:
            if self.avg_sparsity is None:
                return N
            else:
                return N * (1 - self.avg_sparsity)
        else:
            return np.sum(self.value != 0)

    def nbytes(self, nonzero_only=False):
        """
        Number of bytes required to store this TensorProto.
        Args:
            nonzero_only (bool): If True, returns the (average) number of bytes to store
                nonzero elements in the tensor. Default is False.
        """
        if self.dtype not in BYTES_PER_ELEMENT:
            raise ValueError(f"Cannot assess memory for datatype {self.dtype}")
        return int(
            self.numel(nonzero_only=nonzero_only) * BYTES_PER_ELEMENT[self.dtype]
        )

    def store_value(self, value):
        """Stores the given array as the value attribute

        Args:
            value (ndarray): numpy array
        """
        assert isinstance(value, np.ndarray)
        self.value = value

    def get_value(self):
        """
        Returns current runtime-value.
        """
        if self.value is not None:
            return self.value
        else:
            return self.runtime_value

    @property
    def stype_candidate(self):
        return self.density_per_element is not None

    @classmethod
    def from_tensor(cls, x, name, store_value=False):
        """Factory method to create a TensorProto from a pytorch tensor during tracing.

        The :attr:`dtype`, :attr:`shape`, :attr:`avg_sparsity`, and :attr:`value`
        attributes are chosen from the tensor and its fmot annotations
        (see :obj:`fmot.qat.annotated_tensors`).

        Args:
            x (:class:`torch.Tensor`): Pytorch tensor, preferably with annotations
                (see :obj:`fmot.qat.annotated_tensors`)
            name (str): Name for the tensor
            store_value (bool): Whether to store the tensor's value as :attr:`self.value`.
                E.g. if :attr:`x` is a quantized and annotated tensor, :attr:`self.value` will
                be the integer tensor from :attr:`x.asint()`

        Returns:
            - :class:`TensorProto` generated from the pytorch tensor :attr:`x`
        """

        # override name with `varname` attribute if it is provided
        if hasattr(x, "varname"):
            name = x.varname

        val = None
        avg_sparsity = None
        quanta = None
        density_per_element = None
        named_dims = None
        assert isinstance(x, torch.Tensor)
        if hasattr(x, "annotated"):
            if store_value:
                if x.quantized:
                    val = asint(x).cpu().numpy()
                else:
                    val = x.detach().cpu().numpy()
            dtype = str(x.bitwidth)
            if not x.quantized:
                dtype += "_fp"
            avg_sparsity = x.avg_sparsity
            if isinstance(avg_sparsity, torch.Tensor):
                avg_sparsity = avg_sparsity.cpu().item()
            if hasattr(x, "density_per_element"):
                if x.density_per_element is not None:
                    density_per_element = x.density_per_element.cpu().numpy()
            quanta = x.quanta
            if isinstance(quanta, torch.Tensor):
                quanta = quanta.cpu().int().item()
        else:
            dtype = "float"
            if store_value:
                val = x.detach().cpu().numpy()
            avg_sparsity = None
        if hasattr(x, "dimensions"):
            named_dims = x.dimensions

        proto = cls(
            name=name,
            dtype=dtype,
            shape=list(x.shape),
            avg_sparsity=avg_sparsity,
            value=val,
            quanta=quanta,
            density_per_element=density_per_element,
            named_dims=named_dims,
        )
        return proto
