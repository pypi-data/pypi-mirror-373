from fmot.fqir import TensorProto, GraphProto, NodeProto, registry_v1
from fmot.configure import CONFIG
import numpy as np
from typing import *

REARRANGE_GATES = True
VERBOSE = False


def kernelize_lstm(graph: GraphProto):
    """
    Replace lstm node w/ multiple kernelized nodes
    """
    arith = graph.subgraphs["ARITH"]
    if "INIT" in graph.subgraphs:
        no_init = False
        init = graph.subgraphs["INIT"]
    else:
        no_init = True
        init = GraphProto(name="INIT")
    any_kerned = False

    lstm_count = 0
    lstm_in_graph = True
    while lstm_in_graph:
        lstm_in_graph = False
        for node_i, node in enumerate(arith.nodes):
            if node.opname == "lstm":
                lstm_kernelization(arith, init, node, node_i)
                any_kerned = True
                lstm_count += 1
                lstm_in_graph = True
                break

    if no_init and any_kerned:
        init_node = NodeProto(
            name="INIT", optype=None, inputs={}, outputs=[], subgraph=init
        )
        graph.add_node(init_node)
        graph.add_subgraph("INIT", init)


def get_weights(
    arith: GraphProto, node: NodeProto, layer_idx: int, rearrange_gates=False
):
    layer_consts = node.constants["layers"][layer_idx]
    weights: Dict[str, TensorProto] = {}
    for name in ["weight_ih", "weight_hh", "bias_ih", "bias_hh"]:
        weight = layer_consts[name]
        w_int = layer_consts[f"{name}_int"]
        if weight is not None:
            if not isinstance(w_int, np.ndarray):
                w_int = w_int.numpy()

            if rearrange_gates:
                H = w_int.shape[0] // 4
                w_int = np.concatenate(
                    [w_int[: 2 * H], w_int[3 * H :], w_int[2 * H : 3 * H]], axis=0
                )

            if weight.ndim >= 2:
                dtype = "fqint8"
            else:
                dtype = "fqint16"
            proto = TensorProto(
                f"%{name}_l{layer_idx}",
                dtype,
                w_int.shape,
                value=w_int,
                quanta=int(layer_consts[f"{name}_quanta"]),
            )
            arith.add_parameter(proto)
        else:
            proto = None
        weights[name] = proto
    return weights


def get_bw(tensor: TensorProto) -> int:
    return int(tensor.dtype.split("fqint")[1])


def get_matmul(
    name: str,
    dtype: str,
    input_size: int,
    quanta_out: int,
    output_size: int,
    x: TensorProto,
    weight: TensorProto,
    bias: TensorProto = None,
    factor: Any = None,
    output: TensorProto = None,
) -> Tuple[TensorProto, NodeProto]:
    if output is None:
        y = TensorProto(f"%{name}_output", dtype, [output_size], quanta=quanta_out)
    else:
        y = output
    outputs = [y]

    constants = {}
    quanta_weight = weight.quanta
    quanta_x = x.quanta

    quanta_buff = quanta_weight + quanta_x
    shamt_bwred = quanta_buff - quanta_out
    constants["shamt_bwred"] = shamt_bwred
    constants["rounded"] = False
    bw_out = int(dtype.split("fqint")[1])
    constants["bw_out"] = bw_out

    inputs = {}
    if weight.shape[-1] == input_size:
        inputs["x"] = weight
        inputs["y"] = x
    else:
        inputs["y"] = weight
        inputs["x"] = x

    optype = registry_v1["matmul"]
    if bias is not None:
        shamt_bias = bias.quanta - quanta_buff
        constants["shamt_bias"] = shamt_bias
        inputs["bias"] = bias
        optype = registry_v1["addmm"]

    mm_node = NodeProto(name, optype, inputs, outputs, constants)

    return y, mm_node


def get_simple_vvadd(
    name: str,
    dtype: str,
    length: int,
    quanta: int,
    x: TensorProto,
    y: TensorProto,
    output: TensorProto = None,
) -> Tuple[TensorProto, NodeProto]:
    if output is None:
        z = TensorProto(name=name, dtype=dtype, shape=[length], quanta=quanta)
    else:
        z = output

    q_x = x.quanta
    q_y = y.quanta

    s_x = q_x - quanta
    s_y = q_y - quanta

    node = NodeProto(
        name,
        registry_v1["vvadd"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={
            "rounded": False,
            "shamt_x": s_x,
            "shamt_y": s_y,
            "shamt_bwred": 0,
            "bw": get_bw(z),
            "bw_x": get_bw(x),
            "bw_y": get_bw(y),
        },
    )
    return z, node


def get_chunk(
    name: str, chunks: int, x: TensorProto
) -> Tuple[List[TensorProto], NodeProto]:
    length_in = x.shape[-1]
    l_per = length_in // chunks
    outputs = [
        TensorProto(name=f"{name}_{i}", dtype=x.dtype, shape=[l_per], quanta=x.quanta)
        for i in range(chunks)
    ]
    node = NodeProto(
        name,
        registry_v1["chunk"],
        inputs={"x": x},
        outputs=outputs,
        constants={"chunks": chunks, "dim": -1},
    )
    return outputs, node


def get_nonlin(
    name: str,
    b_addr: int,
    b_act: int,
    act_dtype: str,
    lut_dtype: str,
    q_addr: int,
    q_lut: int,
    table,
    x: TensorProto,
    output: TensorProto = None,
    interpolate=False,
) -> Tuple[TensorProto, List[NodeProto]]:
    if not interpolate:
        return _get_nonlin(
            name, b_addr, act_dtype, lut_dtype, q_addr, q_lut, table, x, output
        )
    else:
        return _get_nonlin_interpolate(
            name, b_addr, b_act, act_dtype, lut_dtype, q_addr, q_lut, table, x, output
        )


def _get_nonlin(
    name: str,
    b_addr: int,
    act_dtype: str,
    lut_dtype: str,
    q_addr: int,
    q_lut: int,
    table,
    x: TensorProto,
    output: TensorProto = None,
) -> Tuple[TensorProto, List[NodeProto]]:
    shape = x.shape
    shamt = x.quanta - q_addr

    if output is None:
        lut_output = TensorProto(
            f"{name}_out", dtype=act_dtype, quanta=q_lut, shape=shape
        )
    else:
        lut_output = output

    addr = TensorProto(f"{name}_addr", lut_dtype, shape=x.shape, quanta=q_addr)
    addr_shift = NodeProto(
        f"{name}_addr_shift",
        registry_v1["shift"],
        inputs={"x": x},
        outputs=[addr],
        constants={"shamt": shamt, "bw": b_addr},
    )

    lut = NodeProto(
        f"{name}_lut",
        optype=registry_v1["lut"],
        inputs={"x": addr},
        outputs=[lut_output],
        constants={
            "shamt_address": 0,
            "bw_address": b_addr,
            "table": table,
            "function": table.name,
        },
    )
    return lut_output, [addr_shift, lut]


def _get_nonlin_interpolate(
    name: str,
    b_addr: int,
    b_act: int,
    act_dtype: str,
    lut_dtype: str,
    q_addr: int,
    q_lut: int,
    table,
    x: TensorProto,
    output: TensorProto = None,
) -> Tuple[TensorProto, List[NodeProto]]:
    shape = x.shape
    shamt = x.quanta - q_addr
    shape2 = [2 * x.shape[0]]

    nodes = []

    def add_shape_print(x, msg: str):
        nodes.append(
            NodeProto(
                "print",
                registry_v1["print"],
                inputs={"x": x},
                outputs=[],
                constants={"func": lambda x: msg + str(x.shape)},
            )
        )

    def add_value_print(x, msg: str):
        nodes.append(
            NodeProto(
                "print",
                registry_v1["print"],
                inputs={"x": x},
                outputs=[],
                constants={"func": lambda x: msg + str(x)},
            )
        )

    # COMPUTE FLOOR AND CEIL ADDRESSES
    floor = TensorProto(f"{name}_floor", lut_dtype, shape=shape, quanta=q_addr)
    nodes += [
        NodeProto(
            f"{name}_floor_shift",
            registry_v1["shift"],
            inputs={"x": x},
            outputs=[floor],
            constants={"shamt": shamt, "bw": b_addr},
        )
    ]

    ceil = TensorProto(f"{name}_ceil", lut_dtype, shape=shape, quanta=q_addr)
    nodes += [
        NodeProto(
            f"{name}_ceil_viadd",
            registry_v1["viadd"],
            inputs={"x": floor},
            outputs=[ceil],
            constants={
                "y": 1,
                "shamt_x": 0,
                "shamt_y": 0,
                "shamt_bwred": 0,
                "bw": b_addr,
                "bw_x": b_addr,
                "bw_y": b_addr,
            },
        )
    ]

    # CONCATENATE THEM (TO AVOID CALLING MULTIPLE LUTS)
    cat_out = TensorProto(f"{name}_addrs", lut_dtype, shape=shape2, quanta=q_lut)
    nodes += [
        NodeProto(
            f"{name}_addr_cat",
            registry_v1["cat"],
            inputs={"x0": floor, "x1": ceil},
            outputs=[cat_out],
            constants={"dim": -1},
        )
    ]

    # APPLY LUT TO FLOOR/CEIL CONCATENATION
    lut_out = TensorProto(f"{name}_y", dtype=act_dtype, quanta=q_lut, shape=shape2)
    nodes += [
        NodeProto(
            f"{name}_lut",
            optype=registry_v1["lut"],
            inputs={"x": cat_out},
            outputs=[lut_out],
            constants={
                "shamt_address": 0,
                "bw_address": b_addr,
                "table": table,
                "function": table.name,
            },
        )
    ]

    # CHUNK THE RESULT
    (y_floor, y_ceil), chunk = get_chunk(f"{name}_ychunk", 2, lut_out)
    nodes.append(chunk)

    # COMPUTE MUXING SIGNAL
    #  (1): shift up the floor
    floor_up = TensorProto(
        f"{name}_floor_up", dtype=act_dtype, shape=shape, quanta=x.quanta
    )
    nodes += [
        NodeProto(
            f"{name}_floor_upshift",
            registry_v1["shift"],
            inputs={"x": floor},
            outputs=[floor_up],
            constants={"shamt": -shamt, "bw": b_act},
        )
    ]
    # (2): compute remainder mux = x - floor(x)
    mux = TensorProto(f"{name}_mux", dtype=act_dtype, shape=shape, quanta=x.quanta)
    nodes += [
        NodeProto(
            f"{name}_rem_sub",
            registry_v1["vvsub"],
            inputs={"x": x, "y": floor_up},
            outputs=[mux],
            constants={
                "shamt_x": 0,
                "shamt_y": 0,
                "shamt_bwred": 0,
                "bw": b_act,
                "bw_x": b_act,
                "bw_y": b_act,
            },
        )
    ]

    # MULTIPLY THE TWO EVALUATIONS BY THE MUX
    mix_floor = TensorProto(
        f"{name}_mixfloor", dtype=act_dtype, shape=shape, quanta=q_lut
    )
    nodes += [
        NodeProto(
            f"{name}_mixmul_floor",
            registry_v1["vvmul"],
            inputs={"x": y_floor, "y": mux},
            outputs=[mix_floor],
            constants={"rounded": False, "shamt_bwred": shamt, "bw": b_act},
        )
    ]

    mix_ceil = TensorProto(
        f"{name}_mixceil", dtype=act_dtype, shape=shape, quanta=q_lut
    )
    nodes += [
        NodeProto(
            f"{name}_mixmul_ceil",
            registry_v1["vvmul"],
            inputs={"x": y_ceil, "y": mux},
            outputs=[mix_ceil],
            constants={"rounded": False, "shamt_bwred": shamt, "bw": b_act},
        )
    ]

    # FINAL RESULT: mix_ceil - mix_floor + y_floor
    res_a = TensorProto(f"{name}_result_a", dtype=act_dtype, shape=shape, quanta=q_lut)
    nodes += [
        NodeProto(
            f"{name}_subout",
            registry_v1["vvsub"],
            inputs={"x": mix_ceil, "y": mix_floor},
            outputs=[res_a],
            constants={
                "shamt_x": 0,
                "shamt_y": 0,
                "shamt_bwred": 0,
                "bw": b_act,
                "bw_x": b_act,
                "bw_y": b_act,
            },
        )
    ]

    if output is None:
        output = TensorProto(
            f"{name}_output", dtype=act_dtype, shape=shape, quanta=q_lut
        )
    nodes += [
        NodeProto(
            f"{name}_add_out",
            registry_v1["vvadd"],
            inputs={"x": res_a, "y": y_floor},
            outputs=[output],
            constants={
                "rounded": False,
                "shamt_x": 0,
                "shamt_y": 0,
                "shamt_bwred": 0,
                "bw": b_act,
                "bw_x": b_act,
                "bw_y": b_act,
            },
        )
    ]

    return output, nodes


def get_mul(
    name: str,
    quanta: int,
    dtype: str,
    x: TensorProto,
    y: TensorProto,
    output: TensorProto = None,
    debug=False,
) -> Tuple[TensorProto, NodeProto]:
    log = f"Kernelizing vvmul for {name} : z = x * y"

    quanta_buff = x.quanta + y.quanta
    log += f"\n\tx.quanta={x.quanta}"
    log += f"\n\ty.quanta={y.quanta}"
    log += f"\n\tquanta_buff={quanta_buff}"

    if output is None:
        z = TensorProto(name, dtype=dtype, shape=x.shape, quanta=quanta)
    else:
        z = output

    shamt = quanta_buff - z.quanta
    log += f"\n\tz.quanta={z.quanta}"
    log += f"\n\tshamt={shamt}"

    node = NodeProto(
        name,
        optype=registry_v1["vvmul"],
        inputs={"x": x, "y": y},
        outputs=[z],
        constants={"rounded": False, "shamt_bwred": shamt, "bw": get_bw(z)},
    )
    if debug:
        print(log)
    return z, node


def lstm_kernelization(
    arith: GraphProto, init: GraphProto, node: NodeProto, node_i: int
):
    if VERBOSE:
        print(f"   Kernelizing LSTM node {node}")

    kern_nodes = []

    act_bw = node.constants["layers"][0]["b_act"]
    lut_bw = node.constants["layers"][0]["b_addr"]

    act_dtype = f"fqint{act_bw}"
    lut_dtype = f"fqint{lut_bw}"
    hidden_size = node.constants["hidden_size"]
    input_size = node.constants["input_size"]

    x = node.inputs["x"]
    output, h_final, c_final = node.outputs

    num_layers = node.constants["num_layers"]

    for idx in range(num_layers):
        weights = get_weights(arith, node, idx, rearrange_gates=REARRANGE_GATES)
        layer_conf = node.constants["layers"][idx]
        interpolate = layer_conf.get("interpolate", False)
        if interpolate and VERBOSE:
            print("Generating LSTM with interpolation")

        q_matmul = max(layer_conf["q_mm_hh"], layer_conf["q_mm_ih"])

        # INIT HIDDEN STATE
        h_0 = TensorProto(
            f"lstm_h0_l{idx}", act_dtype, [hidden_size], quanta=layer_conf["q_unity"]
        )
        c_0 = TensorProto(
            f"lstm_c0_l{idx}", act_dtype, [hidden_size], quanta=layer_conf["q_c"]
        )

        h_initializer = NodeProto(
            f"h_init_l{idx}",
            optype=registry_v1["zeros"],
            inputs={},
            outputs=[h_0],
            constants={"shape": [hidden_size]},
        )
        init.add_node(h_initializer)
        c_initializer = NodeProto(
            f"c_init_l{idx}",
            optype=registry_v1["zeros"],
            inputs={},
            outputs=[c_0],
            constants={"shape": [hidden_size]},
        )
        init.add_node(c_initializer)

        # MATMULS
        try:
            y_ih, mm_ih = get_matmul(
                name=f"mm_ih_l{idx}",
                dtype=act_dtype,
                input_size=input_size if idx == 0 else hidden_size,
                output_size=4 * hidden_size,
                x=x,
                weight=weights["weight_ih"],
                bias=weights["bias_ih"],
                quanta_out=layer_conf["q_mm_ih"],
            )
        except:
            print(f"Failed on x: {x}\n" f"{arith}")
            raise
        kern_nodes.append(mm_ih)
        try:
            y_hh, mm_hh = get_matmul(
                name=f"mm_hh_l{idx}",
                dtype=act_dtype,
                input_size=hidden_size,
                output_size=4 * hidden_size,
                x=h_0,
                weight=weights["weight_hh"],
                bias=weights["bias_hh"],
                quanta_out=layer_conf["q_mm_hh"],
            )
        except:
            print("failed on h_0")
            raise
        kern_nodes.append(mm_hh)
        y_mm, add_mms = get_simple_vvadd(
            f"mm_add_l{idx}",
            dtype=act_dtype,
            length=4 * hidden_size,
            quanta=q_matmul,
            x=y_hh,
            y=y_ih,
        )
        kern_nodes.append(add_mms)

        if not REARRANGE_GATES:
            # CHUNK
            (i_x, f_x, g_x, o_x), chunk = get_chunk(
                f"chunk_iofg_l{idx}", x=y_mm, chunks=4
            )
            kern_nodes.append(chunk)

            # SIGSIGTANHSIG
            i, nodes = get_nonlin(
                name=f"i_sigmoid_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_sig_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["sigmoid"],
                x=i_x,
                interpolate=interpolate,
            )
            kern_nodes += nodes
            f, nodes = get_nonlin(
                name=f"f_sigmoid_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_sig_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["sigmoid"],
                x=f_x,
                interpolate=interpolate,
            )
            kern_nodes += nodes
            g, nodes = get_nonlin(
                name=f"g_tanh_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_tanh_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["tanh"],
                x=g_x,
                interpolate=interpolate,
            )
            kern_nodes += nodes
            o, nodes = get_nonlin(
                name=f"o_sigmoid_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_sig_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["sigmoid"],
                x=o_x,
                interpolate=interpolate,
            )
            kern_nodes += nodes

        else:
            x_sigmoid = TensorProto(
                f"x_sigmoid_l{idx}",
                dtype=act_dtype,
                shape=[3 * hidden_size],
                quanta=q_matmul,
            )
            x_tanh = TensorProto(
                f"x_tanh_l{idx}", dtype=act_dtype, shape=[hidden_size], quanta=q_matmul
            )
            split = NodeProto(
                f"gate_split_l{idx}",
                registry_v1["split"],
                inputs={"x": y_mm},
                outputs=[x_sigmoid, x_tanh],
                constants={"lengths": [3 * hidden_size, hidden_size], "dim": -1},
            )
            kern_nodes.append(split)

            ifo, nodes = get_nonlin(
                name=f"ifo_sigmoid_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_sig_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["sigmoid"],
                x=x_sigmoid,
                interpolate=interpolate,
            )
            kern_nodes += nodes

            (i, f, o), chunk = get_chunk(f"chunk_ifo_l{idx}", x=ifo, chunks=3)
            kern_nodes.append(chunk)

            g, nodes = get_nonlin(
                name=f"g_tanh_l{idx}",
                b_addr=lut_bw,
                b_act=act_bw,
                act_dtype=act_dtype,
                lut_dtype=lut_dtype,
                q_addr=layer_conf["q_tanh_addr"],
                q_lut=layer_conf["q_unity"],
                table=node.constants["tanh"],
                x=x_tanh,
                interpolate=interpolate,
            )
            kern_nodes += nodes

        # c_next = i*g + f*c_prev
        ig, ig_prod = get_mul(
            f"ig_prod_l{idx}", quanta=layer_conf["q_c"], dtype=act_dtype, x=i, y=g
        )
        kern_nodes.append(ig_prod)

        fc, fc_prod = get_mul(
            f"fc_prod_l{idx}", quanta=layer_conf["q_c"], dtype=act_dtype, x=f, y=c_0
        )
        kern_nodes.append(fc_prod)

        if idx == num_layers - 1:
            z = c_final
            c_final.shape = [hidden_size]
        else:
            z = None
        c_next, c_sum = get_simple_vvadd(
            f"c_sum_l{idx}",
            dtype=act_dtype,
            length=hidden_size,
            quanta=layer_conf["q_c"],
            x=fc,
            y=ig,
            output=z,
        )
        kern_nodes.append(c_sum)

        # h_next = o * tanh(c_next)
        h_next, nodes = get_nonlin(
            name=f"c_tanh_l{idx}",
            b_addr=lut_bw,
            b_act=act_bw,
            act_dtype=act_dtype,
            lut_dtype=lut_dtype,
            q_addr=layer_conf["q_tanh_addr"],
            q_lut=layer_conf["q_unity"],
            table=node.constants["tanh"],
            x=c_next,
            interpolate=interpolate,
        )
        kern_nodes += nodes
        if idx == num_layers - 1:
            z = output
        else:
            z = None
        h_next, h_gate = get_mul(
            name=f"h_gated_l{idx}",
            quanta=layer_conf["q_unity"],
            dtype=act_dtype,
            x=h_next,
            y=o,
            output=z,
        )
        kern_nodes.append(h_gate)

        # ASSIGN: h->h_next, c->c_next
        kern_nodes.append(
            NodeProto(
                f"assign_h_l{idx}",
                registry_v1["assign"],
                inputs={"y": h_0, "x": h_next},
                outputs=[],
                constants={},
            )
        )
        kern_nodes.append(
            NodeProto(
                f"assign_c_l{idx}",
                registry_v1["assign"],
                inputs={"y": c_0, "x": c_next},
                outputs=[],
                constants={},
            )
        )

        x = h_next

    kern_nodes.append(
        NodeProto(
            f"copy_l{idx}", registry_v1["copy"], inputs={"x": h_next}, outputs=[h_final]
        )
    )
    h_final.shape = h_next.shape

    arith_before = arith.nodes[:node_i]
    if len(arith.nodes) >= node_i:
        arith_after = arith.nodes[node_i + 1 :]
    else:
        arith_after = []

    arith.nodes = arith_before + kern_nodes + arith_after
