import numpy as np
from fmot.fqir import GraphProto, TensorProto, NodeProto, registry_v1
from fmot.qat.nn.atomics import Table
from fmot.configure import CONFIG
import logging

logger = logging.getLogger(__name__)


def get_pwlin_nodes(
    name: str,
    c0: np.ndarray,
    c1: np.ndarray,
    q_c0: int,
    q_c1: int,
    q_addr: int,
    x: TensorProto,
    y: TensorProto,
):
    order = 2

    # convert copt into tables
    tables = []
    for i, copt_i in enumerate([c0, c1]):
        tables.append(Table(np.arange(-128, 128), copt_i, f"{name}_c{i}"))

    nodes = []

    shamt = -8

    # is this overkill? We may be throwing away precision here in some cases...
    if x.quanta != q_addr - 8:
        new_x = TensorProto(f"{x.name}_shifted", x.dtype, x.shape, quanta=q_addr - 8)
        shift_in = NodeProto(
            name=f"{name}_shift_input_dynrange",
            optype=registry_v1["shift"],
            inputs={"x": x},
            outputs=[new_x],
            constants={"shamt": x.quanta - q_addr + 8, "bw": 16},
        )
        nodes.append(shift_in)
        x = new_x

    # compute addr
    addr = TensorProto(f"{x.name}_addr", "fqint8", x.shape, quanta=q_addr)
    shift_addr = NodeProto(
        name=f"{name}_shift_addr",
        optype=registry_v1["shift"],
        inputs={"x": x},
        outputs=[addr],
        constants={"shamt": shamt, "bw": 8},
    )
    nodes.append(shift_addr)

    if order > 1:
        # compute remainder
        rem = TensorProto(f"{x.name}_rem", "fqint16", x.shape, quanta=x.quanta)
        rem_sub = NodeProto(
            name=f"{name}_rem_sub",
            optype=registry_v1["vvsub"],
            inputs={"x": x, "y": addr},
            outputs=[rem],
            constants={
                "shamt_x": 0,
                "shamt_y": 8,
                "shamt_bwred": 0,
                "bw": 16,
                "bw_x": 16,
                "bw_y": 8,
            },
        )
        nodes.append(rem_sub)
    else:
        rem = None

    # Evaluate LUTs
    coeffs = []
    for i, (table, quanta) in enumerate(zip(tables, [q_c0, q_c1])):
        c = TensorProto(
            f"{x.name}_coeff{i}", dtype="fqint16", shape=x.shape, quanta=quanta
        )
        node = NodeProto(
            name=f"{name}_lut_coeff{i}",
            optype=registry_v1["lut"],
            inputs={"x": addr},
            outputs=[c],
            constants={
                "shamt_address": 0,
                "bw_address": 8,
                "table": table,
                "function": table.name,
            },
        )
        nodes.append(node)
        coeffs.append(c)

    # End if there is only one coefficient in the expansion
    if len(coeffs) == 1:
        # TODO: check that the quanta is what we want it to be
        nodes[-1].outputs = [y]
        return y, nodes

    # Otherwise, compute the polynomial expansion
    res = None
    for i, coeff in enumerate(coeffs[::-1]):
        if res is not None:
            HEADROOM = 0
            q = max(res.quanta, coeff.quanta)
            new_res = TensorProto(
                f"{x.name}_sum_{i}", "fqint16", x.shape, quanta=q + HEADROOM
            )
            node = NodeProto(
                name=f"{name}_partial_sum_{i}",
                optype=registry_v1["vvadd"],
                inputs={"x": res, "y": coeff},
                outputs=[new_res],
                constants={
                    "rounded": False,
                    "shamt_x": res.quanta - q,
                    "shamt_y": coeff.quanta - q,
                    "shamt_bwred": -HEADROOM,
                    "bw": 16,
                    "bw_x": 16,
                    "bw_y": 16,
                },
            )
            nodes.append(node)
            res = new_res
        else:
            res = coeff
        if i != len(coeffs) - 1:
            q = res.quanta + rem.quanta + 8
            new_res = TensorProto(
                f"{x.name}_partial_prod_{i}", dtype="fqint16", shape=x.shape, quanta=q
            )
            node = NodeProto(
                name=f"{name}_partial_prod_{i}",
                optype=registry_v1["vvmul"],
                inputs={"x": res, "y": rem},
                outputs=[new_res],
                constants={"rounded": False, "shamt_bwred": -8, "bw": 16},
            )
            nodes.append(node)
            res = new_res

    nodes[-1].outputs = [y]
    if new_res.quanta != y.quanta:
        logger.debug("Changing output shamt to match!!")
        nodes[-1].constants["shamt_bwred"] += new_res.quanta - y.quanta
        new_res.quanta = y.quanta

    return y, nodes


def _kernelize_pwlin(graph: GraphProto):
    """Locates PWLIN nodes within the working graph and kernelizes them.

    Also recurses through any nodes with subgraphs"""

    while any(node.opname == "pwlin" for node in graph.nodes):
        for i, node in enumerate(graph.nodes):
            if node.opname == "pwlin":
                x = node.inputs["x"]
                y = node.outputs[0]
                cnst = node.constants
                c0 = cnst["c0"]
                c1 = cnst["c1"]
                name = cnst["name"]
                q_c0 = cnst["q_c0"]
                q_c1 = cnst["q_c1"]
                q_addr = cnst["q_addr"]

                y, nodes = get_pwlin_nodes(name, c0, c1, q_c0, q_c1, q_addr, x, y)
                graph.nodes = graph.nodes[:i] + nodes + graph.nodes[i + 1 :]

                break

    for node in graph.nodes:
        if node.subgraph is not None:
            _kernelize_pwlin(node.subgraph)


def kernelize_pwlin(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    _kernelize_pwlin(arith)

    return graph
