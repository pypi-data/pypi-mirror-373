import dataclasses


@dataclasses.dataclass(init=True, repr=False, eq=True)
class TensorSignature:
    """
    Dataclass object, storing dtype and shape for a given variable.
    """

    dtype: str
    shape: tuple
    extra_rep: str = dataclasses.field(default_factory=lambda: "")

    __annotations__ = {"dtype": str, "shape": tuple, "extra_rep": str}

    def __repr__(self):
        return (
            f'{self.dtype}<{"x".join([str(s) for s in self.shape])}>' + self.extra_rep
        )


class VariableBase:
    """A variable in an fqir graph. Subclassed by TensorProto

    Args:
        name (str): variable name (should be unique within a given graph)
        dtype (str): datatype
        shape (tuple or list): list/tuple of the variable's shape
        extra_rep (str): additional string to add to the end of the string representation
    """

    def __init__(self, name: str, dtype: str, shape: list, extra_rep: str = None):
        self.name = name
        self.dtype = dtype
        assert isinstance(shape, (tuple, list))
        self.shape = list(shape)
        self.extra_rep = extra_rep if extra_rep is not None else ""
        self.runtime_value = None

    def __repr__(self):
        """
        name: dtype<shape>{extra_rep}
        """
        shp = ""
        if len(self.shape) > 0:
            shp = "<" + "x".join([str(s) for s in self.shape]) + ">"
        rep = f"{self.name}: {self.dtype}{shp}"
        if self.extra_rep is not None:
            rep += self.extra_rep
        return rep

    def signature(self):
        return TensorSignature(self.dtype, self.shape, self.extra_rep)

    @property
    def is_scalar(self):
        return self.shape == [1]

    def get_value(self):
        """
        Returns current runtime value
        """
        return self.runtime_value

    def set_value(self, x):
        """
        Sets current runtime value
        """
        self.runtime_value = x

    def reset_value(self):
        """
        Sets runtime value to None.
        """
        self.runtime_value = None
