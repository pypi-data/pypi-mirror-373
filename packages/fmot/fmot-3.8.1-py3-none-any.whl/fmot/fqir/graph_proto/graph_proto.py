"""An FQIR Graph consists of :obj:`GraphProto`, :obj:`NodeProto`, and :obj:`TensorProto`"""
import numpy as np
from .graph_runtime import run_graph, run_sequential_graph
from collections import defaultdict, OrderedDict
from ..nodes import OpCount, NodeProto
from ..variables import TensorProto
from typing import *

DEF_IND = "   "


class GraphProto:
    """Defines an fqir graph or subgraph

    The same GraphProto class is used for main graphs and subgraphs.
    Certain subgraphs have a special importance:

    * :obj:`MAIN`: This is the main graph containing all subgraphs
    * :obj:`INIT`: This subgraph defines how to initialize state variables
    * :obj:`QUANT`: This subgraph defines how to cast floating point inputs to integer types
    * :obj:`ARITH`: This subgraph defines all of the arithmetic operations for one time-step
    * :obj:`DEQUANT`: This subgraph defines how to cast integer outputs to floating-point

    Args:
        name (str, optional): graph's name
        unbind_dim (int, optional): Which dimension of the input tensor(s) is the time-dimension
        stack_dim (int, optional): Which dimension of the output tensor(s) is the time-dimension.
            Defaults to match :attr:`unbind_dim`

    Attributes:
        nodes (list[:class:`NodeProto`]): The graph's operations
        inputs (list[:class:`TensorProto`]): The inputs to the graph
        outputs (list[:class:`TensorProto`]): The graph's outputs
        parameters (list[:class:`TensorProto`]): The graph's parameters
        subgraphs (dict[:class:`GraphProto`]): Maps names to subgraphs
        reshaper (callable, optional): Reshapes input sequences
            (e.g. for when there is a strided frontend conv1d layer
    """

    def __init__(self, name="", unbind_dim=None, stack_dim=None):
        self.name = name
        self.nodes: List[NodeProto] = []
        self.inputs: List[TensorProto] = []
        self.outputs: List[TensorProto] = []
        self.parameters: List[TensorProto] = []
        self.subgraphs: Dict[str, GraphProto] = {}
        self.reshaper = None
        self.unbind_dim = unbind_dim
        if stack_dim is None:
            stack_dim = unbind_dim
        self.stack_dim = stack_dim

    def add_input(self, tensor):
        """Register a new input tensor to :attr:`self.inputs`

        Args:
            tensor (:class:`TensorProto`): A new input tensor
        """
        self.inputs.append(tensor)

    def add_parameter(self, tensor):
        """Register a new parameter tensor to :attr:`self.parameters`

        Args:
            tensor (:class:`TensorProto`): A new parameter tensor
        """
        self.parameters.append(tensor)

    def add_output(self, tensor):
        """Register a new output tensor to :attr:`self.outputs`

        Args:
            tensor (:class:`TensorProto`): A new output tensor
        """
        self.outputs.append(tensor)

    def add_node(self, node):
        """Register a new node to :attr:`self.nodes`

        Args:
            node (:class:`NodeProto`): New node to add to the graph

        .. note::

            The order in which :class:`NodeProto` are added to the graph is the execution order
        """
        self.nodes.append(node)

    def add_subgraph(self, name, subgraph):
        """Registers a subgraph to the graph with a given name.

        .. note::

            The graph should also be attached to a :class:`NodeProto`
            so that its execution is clear in the graph's execution
            order

        Args:
            name (str): Name to register subgraph under
            subgraph (:class:`GraphProto`): Subgraph to register
        """
        self.subgraphs[name] = subgraph

    def register_reshaper(self, reshaper_module):
        """
        Registers a reshaper to the graph.

        Args:
            reshaper_module (callable): a callable reshaper module
        """
        self.reshaper = reshaper_module

    def printout(self, constants=True, subgraphs=True, indent=None, energy=False):
        """Generate a string representation of the graph"""
        if indent is None:
            indent = DEF_IND
        rep = ""
        if self.reshaper is not None:
            rep += str(self.reshaper)
            rep += "\n" + "-" * 50 + "\n\n"
        if len(self.inputs) > 0:
            rep += "inputs:\n" + indent
            rep += f"\n{indent}".join([str(i) for i in self.inputs])
            rep += "\n"
        if len(self.parameters) > 0:
            rep += "parameters:\n" + indent
            rep += f"\n{indent}".join([str(p) for p in self.parameters])
            rep += "\n"
        rep += "nodes:\n" + indent
        rep += f"\n{indent}".join(
            [
                n.printout(
                    constants=constants,
                    subgraph=subgraphs,
                    indent=indent,
                    energy=energy,
                )
                for n in self.nodes
            ]
        )
        if len(self.outputs) > 0:
            rep += "\noutputs:\n" + indent
            rep += f"\n{indent}".join([str(o) for o in self.outputs])
        return rep

    def __repr__(self):
        return self.printout(constants=False)

    def run(
        self,
        *inputs,
        return_objs=False,
        dequant=False,
        state=None,
        return_dict=False,
        reshape=True,
    ):
        """Run the graph on a set of inputs.

        Nodes are run in the order added by :attr:`add_node`.

        Args:
            *inputs (:class:`numpy.ndarray`): Input tensors to the runtime.
                Their order must match the runtime function signature.
            return_objs (bool, optional): Return all of the runtime's hidden
                variables along with the runtime's output.
            dequant (bool, optional): If True, casts integer outputs to floating point
                by running them through the :attr:`DEQUANT` subgraph.
            state (dict of :obj:`{str:numpy.ndarray}`, optional): Initial runtime state.
                Maps TensorProto and NodeProto names to values.
                If no initial state is provided to a sequential model, the :attr:`INIT`
                subgraph will be run to generate the initial state.
            return_dict (bool, optional): Return the output as a dictionary
            reshape (bool): Pass inputs through the graph's reshaper, if one exists.

        .. note::

            :attr:`return_dict` should not be confused with :attr:`return_objs`.
            The first returns only the model's outputs as a dictionary.
            With :attr:`return_objs=True`, the model will return
            :attr:`(output, internal_vars)`
        """
        if reshape and self.reshaper is not None:
            inputs = [self.reshaper(x) for x in inputs]
        if "INIT" in self.subgraphs:
            return run_sequential_graph(
                self,
                *inputs,
                return_objs=return_objs,
                dequant=dequant,
                objs=state,
                return_dict=return_dict,
            )
        else:
            return run_graph(
                self,
                *inputs,
                return_objs=return_objs,
                dequant=dequant,
                objs=state,
                return_dict=return_dict,
            )

    def iterate_inputs(self, *args, return_dict=False, quant=True, reshape=True):
        """Iterate through inputs along the sequential dimension.

        Args:
            *args: inputs to the model
            return_dict (bool): whether to return processed inputs as a dictionary,
                default is False
            quant (bool): whether to run floating point inputs through quantizers,
                default is True
            reshape (bool): whether to reshape the input sequence (for models with
                frontend strided conv1d layers). Default is True

        Returns:
            - An iterator that yields model inputs at each timestep
        """
        shapes = np.array([a.shape for a in args])
        ndims = np.array([a.ndim for a in args])

        if "INIT" in self.subgraphs:
            assert (
                np.max(ndims) == 2
            ), f"Please remove the batch dimension from your inputs. dims: {ndims}"
        else:
            assert (
                np.max(ndims) == 1
            ), f"Please remove the batch dimension from your inputs. dims: {ndims}"
        if np.max(ndims) == 2:
            unbind_dim = self.unbind_dim
            if unbind_dim is None:
                unbind_dim = 0
            T = shapes[ndims == 2][0][unbind_dim]
        else:
            T = 1
        if reshape and self.reshaper is not None:
            args = [self.reshaper(x) for x in args]
        if quant and "QUANT" in self.subgraphs:
            args = run_graph(self.subgraphs["QUANT"], *args, return_dict=return_dict)
        for t in range(T):
            if isinstance(args, tuple):
                a_t = []
                for a in args:
                    if a.ndim == 2:
                        a_t.append(a.take(t, self.unbind_dim))
                    else:
                        a_t.append(a)
                a_t = tuple(a_t)
            elif isinstance(args, dict):
                a_t = {}
                for k, a in args.items():
                    if a.ndim == 2:
                        a_t[k] = a.take(t, self.unbind_dim)
                    else:
                        a_t[k] = a
            else:
                if args.ndim == 2:
                    a_t = args.take(t, self.unbind_dim)
                else:
                    a_t = args
            yield a_t

    def dequantize(self, *args):
        """Casts arguments to floating point, according to the graph's DEQUANT subgraph"""
        assert (
            "DEQUANT" in self.subgraphs
        ), "This graph doesn't have a dequant subgraph, try the main graph"
        if len(args) == 1:
            args = args[0]
        if isinstance(args, dict):
            tuple_in = tuple(
                [args[tproto.name] for tproto in self.subgraphs["DEQUANT"].inputs]
            )
            output = self.subgraphs["DEQUANT"].run(*tuple_in, return_dict=True)
        elif isinstance(args, (tuple, list)):
            output = self.subgraphs["DEQUANT"].run(*args)
        else:
            output = self.subgraphs["DEQUANT"].run(args)
        return output

    def stack_outputs(self, *args):
        """Stacks lists of outputs along the correct dimension"""
        if self.stack_dim is not None:
            stack_dim = self.stack_dim
        else:
            stack_dim = self.unbind_dim
        if len(args) == 1:
            args = args[0]
        if stack_dim is not None:
            if isinstance(args, dict):
                output = {k: np.stack(vlist, stack_dim) for k, vlist in args.items()}
            elif isinstance(args, tuple):
                output = tuple([np.stack(vlist, stack_dim) for vlist in args])
            else:
                output = np.stack(args, stack_dim)
        else:
            if isinstance(args, dict):
                output = {k: vlist[0] for k, vlist in args.items()}
            elif isinstance(args, tuple):
                output = tuple([vlist[0] for vlist in args])
            else:
                output = args[0]
        return output

    def node_iter(self):
        for node in self.nodes:
            if node.is_subgraph:
                for subnode in node.subgraph.node_iter():
                    yield subnode
            else:
                yield node

    def opcount(self, st_ld_pessimism=None):
        """
        Returns an OpCount object, estimating the number of data memory, table memory,
        and accumulator operations
        """

        all_opcounts = []
        for node in self.node_iter():
            all_opcounts.append(node.opcount(st_ld_pessimism))
        return sum(all_opcounts, start=OpCount())

    def weight(self, st_ld_pessimism=None):
        return self.opcount(st_ld_pessimism).weight()

    def energy(self, st_ld_pessimism=None, config=None):
        raise NotImplementedError(
            "Energy estimation not enabled -- please use the behavioral simulator instead."
        )

    def sorted_opcounts(self, group_by="op", st_ld_pessimism=None):
        if group_by is None or group_by == "node":
            grouped_opcounts = self._opcounts_per_node(st_ld_pessimism)
        elif group_by == "op":
            grouped_opcounts = self._opcounts_per_op(st_ld_pessimism)
        else:
            raise ValueError(f"Cannot group opcounts by {group_by}")

        groups = []
        energies = []
        for group, opcount in grouped_opcounts.items():
            groups.append(group)
            energies.append(opcount.energy())
        sort = np.argsort(energies)[::-1]
        opcounts_out = {}
        for idx in sort:
            if energies[idx] != 0:
                group = groups[idx]
                opcounts_out[group] = grouped_opcounts[group]
        return opcounts_out

    def sorted_energies(self, group_by="op", st_ld_pessimism=None):
        opcounts = self.sorted_opcounts(
            group_by=group_by, st_ld_pessimism=st_ld_pessimism
        )
        energies = OrderedDict()
        for k, v in opcounts.items():
            energies[k] = v.energy()
        return energies

    def _opcounts_per_op(self, st_ld_pessimism=None):
        opcounts = defaultdict(OpCount)
        for node in self.node_iter():
            opcounts[node.optype.name] += node.opcount(st_ld_pessimism)
        return opcounts

    def _opcounts_per_node(self, st_ld_pessimism=None):
        opcounts = OrderedDict()
        for node in self.node_iter():
            opcounts[node] = node.opcount(st_ld_pessimism)
        return opcounts

    def all_nodes(self):
        for node in self.nodes:
            if node.subgraph is not None:
                for n in node.subgraph.all_nodes():
                    yield n
            yield node

    def all_tensors(self):
        tensors = set()
        for x in self.inputs:
            tensors.add(x)
        for x in self.outputs:
            tensors.add(x)
        for node in self.all_nodes():
            for x in node.inputs.values():
                tensors.add(x)
            for x in node.outputs:
                tensors.add(x)

            if node.subgraph is not None:
                tensors = tensors.union(node.subgraph.all_tensors())
        for x in tensors:
            yield x

    def _all_parameters(self):
        params = set(self.parameters)
        for node in self.nodes:
            if node.subgraph is not None:
                params = params.union(node.subgraph._all_parameters())

        for p in params:
            yield p

    def footprint_bytes(self):
        """Reports footprint of the graph, in bytes.

        Returns:
            dictionary with keys "total", "parameters", and "activations"
        """
        param_size = sum([p.nbytes(nonzero_only=True) for p in self._all_parameters()])

        total_size = sum([x.nbytes(nonzero_only=True) for x in self.all_tensors()])

        act_size = total_size - param_size

        return {"total": total_size, "parameters": param_size, "activations": act_size}
