"""This module defines functions for tracing torch graphs and writing out fqir"""
from .utils import (
    combine_iterators,
    getargnames,
    store_hierarchical_names,
    get_hierarchical_name,
    allhaveprotos,
    autogen_name,
    reset_autogen_count,
)
import warnings
import copy
import logging
import torch
from torch import nn, Tensor

from fmot.fqir import TensorProto, NodeProto, GraphProto, registry_v1, passes
import fmot
import fmot.qat as Q
from fmot.qat.annotated_tensors import copy_annotations
from fmot.tracing.tracing_blacklist import TRACING_BLACKLIST
from fmot.tracing.oplinks_v1 import oplinks_v1
from fmot.nn.sequencer import unbind as seq_unbind
from fmot.nn.sequencer import stack as seq_stack
from fmot.qat.nn import GMACv2
from fmot.nn import Loop
from itertools import zip_longest
from typing import *

logger = logging.getLogger(__name__)


def dimension_index(dim, dims):
    """Extract the index of dim in dims list

    Raises:
        ValueError: if dim is not found in dims
    """
    try:
        return dims.index(dim)
    except ValueError as err:
        logger.error("Dimension %d not in dimension list", dim)
        raise err


def trace(model, *inputs, batch_dim=None, seq_dim=None, **kwarg_inputs):
    """Trace a model and generate FQIR

    Args:
        model (QAT Model): Model to be traced
        inputs: inputs to use to trace the model; as many non-keyword arguments as is necessary
        batch_dim (int): input batch dimension. Default is None
        seq_dim (int): input sequential dimension. If not None, the model will be traced as a
            sequential model
    Returns:
        :class:`fqir.GraphProto`: An FQIR graph representation of the model
    """
    if seq_dim is not None:
        if batch_dim is None:
            batch_dim = 0
        logger.info("Tracing sequential model")
        graph, tsrc_dict = trace_sequential_model(
            model, *inputs, batch_dim=batch_dim, seq_dim=seq_dim, **kwarg_inputs
        )
    else:
        logger.info("Tracing feedforward model")
        graph, tsrc_dict = trace_feedforward_model(
            model, *inputs, batch_dim=batch_dim, **kwarg_inputs
        )
    return graph, tsrc_dict


###############################################################
# > GRAPH_MOD_RULES
# >   graph modification rules, a set of forward hook functions.
# >   Do something to the graph whenever a submodule is called.


def register_inputs_immediately(module, graph):
    """Register inputs with the graph immediately (cf. when the node is done executing)

    This needs to be done with the model's top-level module. Tensors without
    protos will be given protos.
    """

    def hook_fn(module, xin):
        for x in combine_iterators(xin, types=torch.Tensor):
            if not hasattr(x, "proto"):
                x.proto = TensorProto.from_tensor(x, autogen_name("i"))
            graph.add_input(x.proto)

    return module.register_forward_pre_hook(hook_fn)


def register_inputs(module, graph):
    """When this module is called, the inputs will be registered to the graph"""

    def hook_fn(module, xin, xout):
        for x in combine_iterators(xin, types=torch.Tensor):
            if not hasattr(x, "proto"):
                x.proto = TensorProto.from_tensor(x, autogen_name("i"))
            graph.add_input(x.proto)

    return module.register_forward_hook(hook_fn)


def register_param(module, graph):
    """
    Should only be applied to ParameterQuantizer modules.
    When called, will register parameters with the graph.
    """
    assert isinstance(
        module, (Q.nn.ParameterQuantizer, fmot.nn.ParameterQuantizer)
    ), "register_param can only take ParameterQuantizer nodes"

    def hook_fn(module, xin, xout):
        (xin,) = xin
        if not hasattr(xin, "proto"):
            xin.proto = TensorProto.from_tensor(
                xout, autogen_name("p"), store_value=True
            )
            graph.add_parameter(xin.proto)
            logger.debug(f"Registering parameter {xin.proto}")
        xout.proto = xin.proto

    return module.register_forward_hook(hook_fn)


class FakeHook:
    def remove(self):
        pass


def register_node(
    module, graph, tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = None
):
    """Register a forward hook to add a node to the computational graph if the node is a leaf"""
    hname = get_hierarchical_name(module)
    module.traced = False

    if isinstance(module, (Q.nn.DictQuantCollection, Q.nn.ListQuantCollection)):
        return FakeHook()

    def hook_fn(module, xin, xout):
        # Get flat list of inputs and outputs

        xin_c = combine_iterators(xin, types=torch.Tensor)
        xout_c = combine_iterators(xout, types=torch.Tensor)

        if isinstance(module, GMACv2):
            logger.debug(f"GMACv2 tracing inputs {xin} \n{len(xin_c)=}")
        if not allhaveprotos(xin_c):
            msgs = []
            for i, x in enumerate(xin_c):
                msgs.append(
                    f" input{i} -- type: {type(x)} -- hasproto: {hasattr(x, 'proto')}"
                )
            raise ValueError(
                f"Inputs to self.{hname} were not annotated with a proto. Module: {module}.\n"
                + "\n".join(msgs)
            )

        # propagate varnames
        for x in xin_c + xout_c:
            if hasattr(x, "varname") and hasattr(x, "proto"):
                x.proto.name = x.varname

        # Add a node to the graph if any of the outputs are not annotated with
        # a proto (this indicates that we've reached a leaf module)
        if not allhaveprotos(xout_c):
            module.traced = True

            # Get constants for the node
            try:
                if hasattr(module, "_get_constants"):
                    constants = module._get_constants(*xin)
                else:
                    constants = {}
            except Exception as e:
                raise RuntimeError(
                    f"tracing failed on module {module}\n"
                    f"inputs: {[x.proto for x in xin_c]}\n"
                    f"input parents: {[x.proto.parents for x in xin_c]}\n"
                    f"input parents-nodes: {[x.proto.parent_nodes for x in xin_c]}\n"
                    f"graph so far: {graph}\n{e}"
                )

            # Create TensorProtos for all of the outputs
            for idx, x in enumerate(xout_c):
                if not hasattr(x, "proto"):
                    x.proto = TensorProto.from_tensor(x, autogen_name("x"))
                    if tsrc_dict is not None:
                        tsrc_dict[x.proto.name] = (module, idx)

            # Get source code reference
            sourceref = ""
            if hasattr(module, "_sourceref"):
                sourceref = module._sourceref

            # Construct an input operand dictionary
            argnames = getargnames(module)
            inputs = {k: x.proto for k, x in zip(argnames, xin_c)}
            if len(inputs) != len(xin_c):
                raise ValueError("argnames has different length than xin_c.")

            # Get operator name and link
            if type(module) in oplinks_v1:
                optype = oplinks_v1[type(module)]
            else:
                warnings.warn(
                    f"Oplink not found for leaf module of type {type(module)}"
                )
                optype = None

            # Construct node and add to graph:
            node = NodeProto(
                name=hname,
                optype=optype,
                inputs=inputs,
                outputs=[x.proto for x in xout_c],
                constants=constants,
                sourceref=sourceref,
            )
            graph.add_node(node)

    return module.register_forward_hook(hook_fn)


def register_outputs(module, graph, dequant_graph=None):
    """Register forward hook function to add the outputs to the graph

    This hook should be applied *after* nodes have been registered
    """
    hname = get_hierarchical_name(module)

    def hook_fn(module, xin, xout):
        for x in combine_iterators(xout, types=torch.Tensor):
            assert hasattr(
                x, "proto"
            ), f"{type(module)} has an output without a proto, hname: {hname}"
            graph.add_output(x.proto)
            if dequant_graph is not None and hasattr(x, "quanta"):
                proto = TensorProto.from_tensor(x, autogen_name("x"))
                proto.dtype = "float"
                optype = registry_v1["dequantize"]
                constants = {"quanta": int(x.quanta)}
                node = NodeProto(
                    name=hname,
                    optype=optype,
                    inputs={"x": x.proto},
                    outputs=[proto],
                    constants=constants,
                )
                dequant_graph.add_node(node)
                dequant_graph.add_input(x.proto)
                dequant_graph.add_output(proto)
                x.proto = proto

    return module.register_forward_hook(hook_fn)


def attach_subgraph(
    module, graph, subgraph, subgraph_name, register_inputs=True, register_outputs=True
):
    """Register forward hook function to add a subgraph to the graph

    Subgraph is also registered as a node for execution purposes
    """
    hname = get_hierarchical_name(module)

    def hook_fn(module, xin, xout):
        xin_c = combine_iterators(xin, types=torch.Tensor)
        xout_c = combine_iterators(xout, types=torch.Tensor)

        if register_inputs:
            for x in xin_c:
                subgraph.add_input(x.proto)
        if register_outputs:
            for x in xout_c:
                if not hasattr(x, "proto"):
                    raise ValueError(
                        f"Output from {module} does not have a proto. \n{subgraph}\n{x}"
                    )
                subgraph.add_output(x.proto)

        sig_dict = {f"x{i+1}": x.proto for i, x in enumerate(combine_iterators(xin_c))}

        node = NodeProto(
            name=hname,
            optype=None,
            inputs=sig_dict if register_inputs else {},
            outputs=[x.proto for x in xout_c] if register_outputs else [],
            subgraph=subgraph,
        )
        graph.add_node(node)
        graph.add_subgraph(subgraph_name, subgraph)

    return module.register_forward_hook(hook_fn)


def register_zeros_init(module, graph):
    hname = get_hierarchical_name(module)

    def hook_fn(module, xin, xout):
        xout_c = combine_iterators(xout, types=torch.Tensor)
        for x in xout_c:
            x.proto = TensorProto.from_tensor(x, autogen_name("x"))
            node = NodeProto(
                name=hname,
                optype=registry_v1["zeros"],
                inputs={},
                outputs=[x.proto],
                constants={"shape": tuple(x.shape)},
            )
            graph.add_node(node)

    return module.register_forward_hook(hook_fn)


def _siso_sequencer_state_assign(
    module: fmot.nn.Sequencer,
    xin: torch.Tensor,
    output: Tuple[torch.Tensor, List[torch.Tensor]],
    graph: GraphProto,
    hname: str,
):
    assert isinstance(module, fmot.nn.Sequencer)
    assert not module.is_mimo

    state_in = module.prev_state
    state_out = module.state

    if isinstance(output, (list, tuple)):
        try:
            out_proto = output[0].proto
        except:
            raise ValueError(f"output: {output}, output[0] doesn't have a proto")
    else:
        out_proto = output.proto
    copied_output = None

    for s_in, s_out in zip(state_in, state_out):
        if s_in.proto == out_proto:
            new_out_proto = TensorProto.from_tensor(output[0], autogen_name("x"))
            copy_node = NodeProto(
                name=hname,
                optype=registry_v1["copy"],
                inputs={"x": out_proto},
                outputs=[new_out_proto],
                constants=None,
            )
            copied_output = copy.deepcopy(output[0])
            copied_output = copy_annotations(output[0], copied_output)
            copied_output.proto = new_out_proto
            out_proto = new_out_proto
            graph.add_node(copy_node)
        node = NodeProto(
            name=hname,
            optype=registry_v1["assign"],
            inputs={"y": s_in.proto, "x": s_out.proto},
            outputs=[],
            constants=None,
        )
        graph.add_node(node)

    # cleanup (this is essential if the Sequencer layer is reused!!)
    module.state = None
    module.prev_state = None

    if copied_output is not None:
        ret = (copied_output, output[1])
    else:
        ret = None
    return ret


def _mimo_sequencer_state_assign(
    module: fmot.nn.Sequencer,
    xin: List[torch.Tensor],
    output: Tuple[List[torch.Tensor], List[torch.Tensor]],
    graph: GraphProto,
    hname: str,
):
    assert isinstance(module, fmot.nn.Sequencer)
    assert module.is_mimo

    state_in = module.prev_state
    state_out = module.state

    for s_in, s_out in zip(state_in, state_out):
        node = NodeProto(
            name=hname,
            optype=registry_v1["assign"],
            inputs={"y": s_in.proto, "x": s_out.proto},
            outputs=[],
            constants=None,
        )
        graph.add_node(node)


def register_state_assign(module, graph):
    hname = get_hierarchical_name(module)

    def hook_fn(module, xin, output):
        assert isinstance(module, fmot.nn.Sequencer)
        if module.is_mimo:
            return _mimo_sequencer_state_assign(module, xin, output, graph, hname)
        else:
            return _siso_sequencer_state_assign(module, xin, output, graph, hname)

    return module.register_forward_hook(hook_fn)


def clean_params(model):
    for p in model.parameters():
        if hasattr(p, "proto"):
            delattr(p, "proto")


def register_output_replacement(module, graph: GraphProto):
    def hook_fn(module, xin, output):
        if isinstance(xin, (list, tuple)):
            assert len(xin) == 1
            xin = xin[0]
        assert isinstance(
            xin, torch.Tensor
        ), f"{xin=} is not a tensor (input to {module})"
        assert isinstance(output, torch.Tensor)

        assert hasattr(xin, "proto")
        assert hasattr(output, "proto")
        if xin.proto in graph.outputs:
            idx = graph.outputs.index(xin.proto)
            graph.outputs[idx] = output.proto
            logger.debug(f"Output {output.proto} will replace {xin.proto}")
            logger.debug(f"{output.proto.parents=}")
            logger.debug(graph.nodes[-10:])
        elif output.proto in graph.outputs:
            logger.debug(
                f"Output {output.proto} was already the graph output -- doing nothing"
            )
        else:
            raise RuntimeError(
                f"xin proto {xin.proto} was not an output for graph \n{graph}"
            )

    return module.register_forward_hook(hook_fn)


def register_loop(module: Loop, curr_graph: GraphProto, tsrc_dict: dict):
    """Register a forward hook to add a node to the computational graph if the node is a leaf"""
    hname = get_hierarchical_name(module)
    module.traced = False

    def hook_fn(
        module: Loop,
        args: tuple[list[Tensor], list[Tensor], list[Tensor]],
        kwargs: dict,
        orig_outputs: list[Tensor],
    ):
        # construct a loop node by tracing the submodules into a new loop GraphProto
        if len(args) == 3:
            x_to_slice, x_recursed_init, x_scope = args
        elif len(args) == 0:
            x_to_slice = kwargs["x_to_slice"]
            x_recursed_init = kwargs["x_recursed_init"]
            x_scope = kwargs["x_scope"]
        else:
            raise ValueError(f"Expected 3 or 0 args, got {len(args)}")

        assert allhaveprotos(x_to_slice + x_recursed_init + x_scope)

        loop_graph = GraphProto(name=f"loop_{hname}")

        # Approach:
        # 1) trace _initialize_recursive_state to curr_graph
        # 2) trace _forward_trace to loop_graph

        #### Tracing _initialize_recursive_state

        handles = []
        for child in module.children():
            get_tracing_handles(handles, child, curr_graph, tsrc_dict)

        x_recursed = module._initialize_recursive_state(x_recursed_init)

        for handle in handles:
            handle.remove()

        #### Tracing _forward_trace to loop_graph

        handles = []
        for child in module.children():
            get_tracing_handles(handles, child, loop_graph, tsrc_dict)

        sliced_protos = []
        blocksizes = []
        for x, blocksize in zip_longest(x_to_slice, module.slice_blocksizes):
            proto = TensorProto.from_tensor(
                x, autogen_name("x.slice"), store_value=False
            )
            proto.shape[module.dim] = blocksize
            sliced_protos.append(proto)
            blocksizes.append(blocksize)

        x_recursed_orig_protos = []
        for x in x_recursed:
            x_recursed_orig_protos.append(x.proto)
            proto = TensorProto.from_tensor(
                x, autogen_name("x.recurse"), store_value=False
            )
            x.proto = proto

        x_scope_orig_protos = []
        for x in x_scope:
            x_scope_orig_protos.append(x.proto)
            proto = TensorProto.from_tensor(
                x, autogen_name("x.scope"), store_value=False
            )
            x.proto = proto

        y_recursed, y_concat, y_final = module._forward_trace(
            x_to_slice, x_recursed, x_scope, sliced_protos
        )

        for x in x_recursed:
            loop_graph.add_input(x.proto)
        for proto in sliced_protos:
            loop_graph.add_input(proto)
        for x in x_scope:
            loop_graph.add_input(x.proto)

        for y in y_recursed + y_concat + y_final:
            loop_graph.add_output(y.proto)

        for handle in handles:
            handle.remove()

        # construct the Loop node
        inputs = {}
        for i, proto in enumerate(x_recursed_orig_protos):
            inputs[f"x_recurse_{i}"] = proto
        for i, x in enumerate(x_to_slice):
            inputs[f"x_sliced_{i}"] = x.proto
        for i, proto in enumerate(x_scope_orig_protos):
            inputs[f"x_scope_{i}"] = proto

        # Create TensorProtos for all of the outputs
        output_protos = []
        for idx, x in enumerate(orig_outputs):
            x.proto = TensorProto.from_tensor(x, autogen_name("x"))
            if tsrc_dict is not None:
                tsrc_dict[x.proto.name] = (module, idx)
            output_protos.append(x.proto)

        rev_sliced = module.slice_reversed
        if len(rev_sliced) == 1 and len(x_to_slice) != 1:
            rev_sliced = [rev_sliced[0]] * len(x_to_slice)

        rev_cat = module.concat_reversed
        if len(rev_cat) == 1 and len(y_concat) != 1:
            rev_cat = [rev_cat[0]] * len(y_concat)

        node = NodeProto(
            name=hname,
            optype=registry_v1["loop"],
            inputs=inputs,
            outputs=output_protos,
            constants={
                "n_iter": module.n_iter,
                "n_recurse": len(y_recursed),
                "n_scope": len(x_scope),
                "n_concat": len(y_concat),
                "n_final": len(y_final),
                "n_sliced": len(x_to_slice),
                "block_size_sliced": blocksizes,
                "reverse_sliced": rev_sliced,
                "reverse_concat": rev_cat,
            },
            subgraph=loop_graph,
        )

        for x, orig_proto in zip(x_scope, x_scope_orig_protos):
            x.proto = orig_proto

        curr_graph.add_node(node)

        return orig_outputs

    return [module.register_forward_hook(hook_fn, with_kwargs=True)]


def get_tracing_handles(
    handles: list, module: nn.Module, arith: GraphProto, tsrc_dict: dict
):
    if isinstance(module, Loop):
        handles += register_loop(module, arith, tsrc_dict)
        return

    if not isinstance(module, tuple(TRACING_BLACKLIST)):
        handles += [register_node(module, arith, tsrc_dict)]
    if isinstance(module, fmot.nn.Sequencer):
        handles += [register_state_assign(module, arith)]
    if isinstance(module, Q.nn.ParameterQuantizer):
        handles += [register_param(module, arith)]

    # register modules recursively to arith; except for children of loop,
    # which need to be traced into a different subgraph (handled by register_loop)
    for child in module.children():
        get_tracing_handles(handles, child, arith, tsrc_dict)


############################
# > TRACE FUNCTIONS
@torch.no_grad()
def trace_feedforward_model(
    model, *inputs, batch_dim=0, seq_dim=1, remove_batchdim=True, **kwarg_inputs
):
    """Trace a feedforward model (i.e. a model without any sequential operators)

    Args:
        model (:class:`torch.nn.Module`): The model to be traced (should be quantized beforehand)
        inputs (:class:`torch.Tensor`): Input(s) to use to trace the model
        batchdim (int, optional): Batch dimension to remove from computational graph
    """
    reset_autogen_count()
    store_hierarchical_names(model)

    #####################################
    # > SET RULES FOR GRAPH CONSTRUCTION
    graph = GraphProto(name="MAIN")
    # Register inputs and outputs
    dequant_graph = GraphProto(name="DEQUANT")
    handles = [
        register_inputs_immediately(model, graph),
        register_outputs(model, graph, dequant_graph=dequant_graph),
        attach_subgraph(
            model,
            graph,
            dequant_graph,
            "DEQUANT",
            register_inputs=False,
            register_outputs=False,
        ),
    ]

    # construct a tensor-source-dict for tracing
    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = {}

    arith = GraphProto(name="ARITH")

    # Create a quant/dequant subgraphs if the root node is a QuantWrapper
    if isinstance(model, Q.nn.QuantWrapper):
        # Create and attach a quant subgraph
        qgraph = GraphProto(name="QUANT")
        handles += [attach_subgraph(model.quantizers, graph, qgraph, "QUANT")]
        # Register quantizers as nodes
        handles += [
            register_node(m, qgraph, tsrc_dict)
            for m in model.quantizers.all_quantizers()
        ]

        # attach requantizers to arith
        for m in model.requantizers.modules():
            if isinstance(m, Q.nn.Requantize):
                logger.debug(f"Adding tracing for requantizer {m}")
                handles += [register_node(m, arith, tsrc_dict)]
                handles += [register_output_replacement(m, arith)]

        amodel = model.model
    else:
        amodel = model
    # Create and attach subgraph for arithmetic operations

    handles += [attach_subgraph(amodel, graph, arith, "ARITH")]
    # Register non-blacklisted arithmetic modules and parameters
    get_tracing_handles(handles, amodel, arith, tsrc_dict)

    ################################################
    # > CONSTRUCT GRAPH -- just call on test input
    if not (hasattr(inputs[0], "dimensions")):
        input_dimensions = ["F", "F", "F"]
        input_dimensions[batch_dim] = "B"
        input_dimensions[seq_dim] = "T"
    else:
        input_dimensions = inputs[0].dimensions

    tracing_inputs, tracing_kwargs = prepare_inputs(
        model, None, input_dimensions, inputs, kwarg_inputs
    )

    outputs = model(*tracing_inputs, **tracing_kwargs)

    # for input in inputs:
    #     input.dimensions = None
    # outputs = model(*inputs)
    ####################
    # > REMOVE HANDLES
    for handle in handles:
        handle.remove()
    reset_autogen_count()
    clean_params(model)

    if remove_batchdim:
        graph = passes.remove_batchdim(graph, dim=batch_dim)

    graph, objs = passes.run_passes(graph)
    return objs, tsrc_dict


def prep_model_for_streaming(model, xin):
    """Set model into streaming mode"""
    for module in [model] + list(model.modules()):
        if isinstance(module, fmot.nn.Sequencer):
            # module.state = module.get_init_state(xin)
            module._streaming = True
        if isinstance(module, Q.nn.Dropout):
            module.training = False
    return model


def clean_model_from_streaming(model):
    """Reset model from streaming mode"""
    for module in [model] + list(model.modules()):
        if isinstance(module, fmot.nn.Sequencer):
            module.state = None
            module.prev_state = None
            module._streaming = False
        if hasattr(module, "tracing_mode"):
            module.tracing_mode = False
    return model


def replace_with_mapping(inputs, tensor_fn):
    if inputs is None:
        return None
    if isinstance(inputs, torch.Tensor):
        return tensor_fn(inputs)
    elif isinstance(inputs, (list, tuple)):
        return [replace_with_mapping(x, tensor_fn) for x in inputs]
    elif isinstance(inputs, dict):
        return {k: replace_with_mapping(v, tensor_fn) for k, v in inputs.items()}


def prepare_inputs(model, graph, input_dimensions, inputs, kwargs):
    def prep_input(x):
        if x is not None:
            if graph is not None:
                x = prepare_for_tracing(model, x, graph)
            if x is not None and x.dim() == 3:
                if dimension_index("T", input_dimensions) == 2:
                    y = x[:, :, 0]
                    y.dimensions = input_dimensions[:-1]
                else:
                    if dimension_index("B", input_dimensions) == 0:
                        y = x[:, 0]
                        y.dimensions = ["B", "F"]
                    else:
                        y = x[0]
                        y.dimensions = ["F", "B"]
            else:
                y = x
        else:
            y = None
        return y

    inputs = replace_with_mapping(inputs, prep_input)
    kwargs = replace_with_mapping(kwargs, prep_input)
    return inputs, kwargs


@torch.no_grad()
def trace_sequential_model(model, *inputs, batch_dim=0, seq_dim=-1, **kwarg_inputs):
    """Trace a sequential model and generate fqir"""

    reset_autogen_count()
    store_hierarchical_names(model)

    #####################################
    # > SET RULES FOR GRAPH CONSTRUCTION
    main = GraphProto(name="MAIN")
    init = GraphProto(name="INIT")
    quant = GraphProto(name="QUANT")
    dequant = GraphProto(name="DEQUANT")
    arith = GraphProto(name="ARITH")

    ##########
    # > Construct a tensor-source dictionary for debugging
    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = {}

    ### MAIN LEVEL

    # Register inputs and outputs to MAIN
    handles = []
    handles += [register_inputs_immediately(model, main)]
    handles += [register_outputs(model, main, dequant_graph=dequant)]

    # Attach INIT to MAIN
    handles += [
        attach_subgraph(
            model, main, init, "INIT", register_inputs=False, register_outputs=False
        )
    ]

    # Attach dequant to MAIN
    handles += [
        attach_subgraph(
            model,
            main,
            dequant,
            "DEQUANT",
            register_inputs=False,
            register_outputs=False,
        )
    ]

    ### INIT LEVEL
    # register state init to INIT
    for m in model.modules():
        if isinstance(m, Q.nn.StateInitializer):
            handles += [register_zeros_init(m, init)]

    ### LOOP LEVEL
    # QUANT
    handles += [attach_subgraph(model.quantizers, main, quant, "QUANT")]
    handles += [
        register_node(m, quant, tsrc_dict) for m in model.quantizers.all_quantizers()
    ]

    if isinstance(model, Q.nn.QuantWrapper):
        amodel = model.model
    else:
        amodel = model

    # ARITH
    amodel = model.model
    handles += [attach_subgraph(amodel, main, arith, "ARITH")]

    get_tracing_handles(handles, amodel, arith, tsrc_dict)

    # requantizers
    if isinstance(model, Q.nn.QuantWrapper):
        for m in model.requantizers.modules():
            if isinstance(m, Q.nn.Requantize):
                handles += [register_node(m, arith, tsrc_dict)]
                handles += [register_output_replacement(m, arith)]

    ### IN and OUT dimensions
    input_dimensions = ["F", "F", "F"]
    input_dimensions[batch_dim] = "B"
    input_dimensions[seq_dim] = "T"

    ################################################
    # > CONSTRUCT GRAPH -- just call on test input
    tracing_inputs, tracing_kwargs = prepare_inputs(
        model, main, input_dimensions, inputs, kwarg_inputs
    )

    model = prep_model_for_streaming(model, inputs[0])

    model(*tracing_inputs, **tracing_kwargs)
    model = clean_model_from_streaming(model)

    ####################
    # > REMOVE HANDLES
    for handle in handles:
        handle.remove()

    reset_autogen_count()
    if 0 <= seq_dim < batch_dim:
        batch_dim -= 1

    if batch_dim == 0 and seq_dim == 1:
        main.unbind_dim = 0
    elif batch_dim == 1 and seq_dim == 0:
        main.unbind_dim = 0
    elif seq_dim in (2, -1):
        main.unbind_dim = -1

    main = passes.remove_batchdim(main, dim=batch_dim)

    logger.debug(f"ARITH before passes: \n{arith}\n--------")

    main, objs = passes.run_passes(main)

    logger.debug(f"ARITH after passes: \n{main.subgraphs['ARITH']}")

    clean_params(model)
    return objs, tsrc_dict


def prepare_for_tracing(model, x, main_graph):
    for submodule in model.modules():
        if hasattr(submodule, "tracing_mode"):
            submodule.tracing_mode = True
    return x


def hook_mixed(model, graph, init_graph, tsrc_dict=None):
    handles = []
    _hook_ff(model, graph, init_graph, handles, tsrc_dict)
    return handles


def _hook_ff(
    module,
    graph,
    init_graph,
    handles,
    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = None,
):
    for m in module.children():
        if isinstance(m, fmot.nn.Sequencer):
            handles += _hook_seq(m, graph, init_graph, tsrc_dict)
        elif not isinstance(m, tuple(TRACING_BLACKLIST)):
            handles += [register_node(m, graph, tsrc_dict)]
            _hook_ff(m, graph, init_graph, handles)
        if isinstance(m, Q.nn.ParameterQuantizer):
            handles += [register_param(m, graph)]


def _hook_seq(
    module, graph, init_graph, tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = None
):
    assert isinstance(module, fmot.nn.Sequencer)

    internal_handles = []
    external_handles = []

    for name, m in module.named_modules():
        if m != module and type(m) not in TRACING_BLACKLIST:
            internal_handles += [
                register_node(m, register_node(m, graph, tsrc_dict), tsrc_dict)
            ]
        elif isinstance(m, Q.nn.StateInitializer):
            internal_handles += [register_zeros_init(m, init_graph)]
        elif isinstance(m, Q.nn.ParameterQuantizer):
            internal_handles += [register_param(m, graph)]
    internal_handles += [register_state_assign(module, graph)]

    def seq_prehook_fn(seq, xin):
        """
        - Enables streaming mode
        - Takes just first input from sequence
        - Sets SEQ_LEN to the sequence length
        """
        unbind_dim = seq.seq_dim
        seq.set_streaming(True)
        return_state = False
        if isinstance(xin, tuple):
            if len(xin) == 2:
                return_state = True
                x, state = xin
            else:
                (x,) = xin
        else:
            x = xin
        seq.SEQ_LEN = x.shape[unbind_dim]

        new_x = seq_unbind(x, unbind_dim)[0]
        new_x.proto = x.proto

        if return_state:
            return new_x, state
        else:
            return new_x

    def seq_posthook_fn(seq, xin, xout):
        """
        - Disables streaming mode
        - Removes internal hooks
        - Repeats output SEQ_LEN times;
        """
        unbind_dim = seq.seq_dim
        seq.set_streaming(False)
        output, final_state = xout
        new_output = seq_stack([output] * seq.SEQ_LEN, unbind_dim)
        new_output.proto = output.proto
        del seq.SEQ_LEN

        for handle in internal_handles:
            handle.remove()

        return new_output, final_state

    external_handles += [module.register_forward_pre_hook(seq_prehook_fn)]
    external_handles += [module.register_forward_hook(seq_posthook_fn)]
    return external_handles
