from .batchdim_removal import remove_batchdim
from .dimtag_removal import remove_named_dims
from .kernelize_lstm import kernelize_lstm
from .kernelize_temporal_unfold import kernelize_temporal_unfold, add_conv2d_buffer
from .cleanup import (
    uniquify_names,
    limit_biases,
    remove_unused_params,
    remove_null_shifts,
    correct_subgraph_outputs,
)
from .kernelize_red_broad import kernelize_sum, kernelize_broadcast
from .kernelize_lut import kernelize_pwlin
from .fold_reused_params import fold_reused_params
from .stride_optimization import perform_stride_optimization
from .repeat_assign import dereference_repeated_assigns
from .statically_transpose import static_transposes
from ..graph_proto import GraphProto
from .virtualize_high_precisions import virtualize_high_precisions
from .conv1d_weight_pass import conv1d_weights_pass
from .output_naming import rename_outputs
import logging

logger = logging.getLogger("FQIR PASSES")


PASS_ORDER = [
    # remove_batchdim,
    kernelize_pwlin,  # recurses into subgraphs :)
    # correct_subgraph_outputs,
    # kernelize_lstm,
    remove_null_shifts,  # recurses into subgraphs :)
    virtualize_high_precisions,  # recurses into subgraphs :)
    # perform_stride_optimization,  # not necessary to recurse
    dereference_repeated_assigns,  # assigns should only be in the top-level graph (TODO: enforce this)
    kernelize_temporal_unfold,  # TODO: what happens if conv1d used in a subgraph?
    conv1d_weights_pass,  # recurses into subgraphs
    add_conv2d_buffer,  # TODO: what happens if conv2d used in a subgraph?
    kernelize_sum,  # recurses into subgraphs
    kernelize_broadcast,  # recurses into subgraphs
    uniquify_names,
    limit_biases,  # recurses into subgraphs
    static_transposes,  # recurses into subgraphs
    remove_unused_params,  # recurses into subgraphs
    fold_reused_params,  # recurses into subgraphs
    rename_outputs,
    uniquify_names,
]


def run_passes(graph):
    objs = {"graph": graph, "io_spec": None}
    logger.debug("Running FQIR optimization passes")
    for p in PASS_ORDER:
        logger.debug(f"{p}:")
        ret = p(objs["graph"])
        if isinstance(ret, GraphProto):
            objs["graph"] = ret
        elif isinstance(ret, dict):
            objs.update(ret)
        logger.debug(objs["graph"])

    graph = objs["graph"]
    return graph, objs
