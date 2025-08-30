"""Defines Operator base and registry"""
import inspect
from .opcounters import OpCounter
from fmot.fqir.variables import VariableBase
from typing import *


def get_defaults_names(function):
    """Returns a list of parameter names with default values."""
    argspec = inspect.getfullargspec(function)
    if argspec.defaults is None:
        return []
    res = []
    for i in range(len(argspec.defaults)):
        argname = argspec.args[-(i + 1)]
        res.append(argname)
    return res


def check_and_get_runtime_varkw(function, inputs, constants):
    argspec = inspect.getfullargspec(function)
    runtime_varkw = argspec.varkw
    runtime_args_varkw = argspec.args
    if runtime_varkw is not None:
        runtime_args_varkw.append(runtime_varkw)
    runtime_args_varkw_set = set(runtime_args_varkw)
    if "self" in runtime_args_varkw:
        runtime_args_varkw_set.remove("self")
    if "subgraph" in runtime_args_varkw:
        runtime_args_varkw_set.remove("subgraph")

    specified_args = inputs + constants
    specified_args = set(specified_args)

    # remove default args
    if argspec.defaults is not None:
        for i in range(len(argspec.defaults)):
            argname = runtime_args_varkw[-(i + 1)]
            runtime_args_varkw_set.remove(argname)
            if argname in specified_args:
                specified_args.remove(argname)

    runtime_args_varkw = set(runtime_args_varkw)

    # if set(runtime_args_varkw) == set(specified_args):
    #     set_diff = (runtime_args_varkw - specified_args).union(specified_args - runtime_args_varkw)
    #     if "subgraph" in set_diff:
    #         set_diff.remove("subgraph")
    #     if len(set_diff) != 0:
    #         raise ValueError(
    #             "For all runtime args, must specify which are "
    #             + "variable inputs and which are constant."
    #             + f"\nOffending function: {function}"
    #             + f"\nruntime_args_varkw={runtime_args_varkw}"
    #             + f"\nspecified_args={specified_args}"
    #         )
    assert not set(inputs).intersection(set(constants)), (
        "Cannot specify args as both inputs and constants"
        + f"\nOffending function: {function}"
    )
    return runtime_varkw


class OpType:
    """An FQIR operator

    Wraps a function with notes on which of its arguments are set at runtime vs constant

    Args:
        runtime (callable): A callable that implements the given operator
        runtime_inputs (list of [str]): Which of the runtime arguments can change during run time.
            If the runtime accepts a variable number of keyword arguments,
            indicate with the keyword dictionary name (e.g. 'kwargs' for :code:`foo(**kwargs)`)
        runtime_constants (list of [str]): Which runtime arguments are constant during run time.
            Can also accept a keyword dictionary name too like **runtime_inputs**.
        seq_len_fn (callable, optional): Function that computes sequence length (or H,W) as a function
            of input sequence length.
            Signature: (input_length: tuple[int], constants: dict) -> tuple[int]
    Attributes:
        runtime (callable or str): The runtime function
        seq_len_fn (callable): Function that computes sequence length (or H,W) as a function
            of input sequence length
    """

    def __init__(
        self,
        name,
        inputs,
        constants,
        runtime=None,
        opcounter=None,
        seq_length_fn=None,
        repr_settings=None,
        can_bcast_in: bool = True,
    ):
        self.name = name

        if runtime is not None:
            self._runtime = runtime
        else:
            runtime = self.runtime
            self._runtime = None

        self.docstring = runtime.__doc__

        self.runtime_varkw = check_and_get_runtime_varkw(runtime, inputs, constants)

        self.inputs = inputs
        self.constants = constants

        if opcounter is not None:
            assert isinstance(opcounter, OpCounter)
        self.opcounter = opcounter

        self._seq_length_fn = seq_length_fn
        self.repr_settings = repr_settings

        self._inputs: Dict[str, VariableBase] = None
        self._outputs: List[VariableBase] = None

        self.can_bcast_in = can_bcast_in

    def runtime(self, *args, **kwargs):
        return self._runtime(*args, **kwargs)

    def __repr__(self):
        return "OpType<{}>".format(self.name)

    def check_inputs_constants(self, inputs, constants):
        """Checks inputs and constants against the registered inputs and constants

        Args:
            inputs (dict): A dictionary with str keys indicating
                which input is connected to which object
            constants(dict): A dictionary with str keys indicating
                which constant is which value

        Raises:
            ValueError: When the inputs or constants keys do not match the runtime inputs and
                constants registered during __init__
        """
        input_names = list(inputs.keys())
        constant_names = list(constants.keys())

        if set(input_names).intersection(set(constant_names)):
            raise ValueError(
                "One or more names found in both inputs and constants list"
            )

        self_inputs = self.inputs.copy()
        self_constants = self.constants.copy()
        if self.runtime_varkw in self_inputs:
            self_inputs.remove(self.runtime_varkw)
            self_inputs += [name for name in input_names if name not in self_inputs]
        elif self.runtime_varkw in self_constants:
            self_constants.remove(self.runtime_varkw)
            self_constants += [
                name for name in constant_names if name not in self_constants
            ]

        default_names = get_defaults_names(self.runtime)

        for dn in default_names:
            if dn in input_names:
                input_names.remove(dn)
            if dn in constant_names:
                constant_names.remove(dn)
            if dn in self_constants:
                self_constants.remove(dn)
            if dn in self_inputs:
                self_inputs.remove(dn)

        if set(constant_names) != set(self_constants):
            raise ValueError(
                f"Mismatch between provided constants {sorted(constant_names)} "
                + f"and registered constants {sorted(self_constants)}. Defaults: {default_names}"
            )

    def seq_length_fn(self, input_length, constants):
        if self._seq_length_fn is None:
            return input_length
        else:
            return self._seq_length_fn(input_length, constants)


class OpRegistry:
    """A registry for FQIR operators

    Register ops with :attr:`register_op`, and access registered ops by their name.

    Args:
        version (str): Version string
    """

    def __init__(self, version):
        self.version = version
        self.ops = {}

    def register_op(self, op):  # pylint:disable=C0103
        """Add an operator to this registry

        Args:
            op (:obj:`OpType`): Operator to register

        Raises:
            ValueError: if an operator with the same name is already registered
        """
        assert isinstance(op, OpType)
        if op.name in self.ops:
            raise ValueError(f"An operator is already registered with name {op.name}")
        self.ops[op.name] = op

    def register_ops(self, ops):
        """Convenience function for adding multiple operators from a list"""
        for op in ops:  # pylint:disable=C0103
            self.register_op(op)

    @property
    def docstrings(self):
        """Docstrings for registered operators"""
        docstrings = []
        for name, op in self.ops.items():  # pylint:disable=C0103
            docstrings.append(f"{name}: {op.docstring}")
        return "\n".join(docstrings)

    def __getitem__(self, name):
        return self.ops[name]

    def docstring_for(self, name):
        """Retrieve the docstring for an operator

        Args:
            name (str): Operator name
        """
        return self[name].docstring

    def runtime_for(self, name):
        """Retrieve the runtime for an operator

        Args:
            name (str): Operator name
        """
        return self[name].runtime

    @property
    def optypes(self):
        """A list of registered operator names"""
        return list(self.ops.keys())

    def __repr__(self):
        rep = f"OpRegistry {self.version}:\n{self.docstrings}"
        return rep
