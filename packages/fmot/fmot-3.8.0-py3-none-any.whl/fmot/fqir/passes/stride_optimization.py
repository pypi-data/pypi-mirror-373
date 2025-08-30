from ... import fqir
from .helpers import create_replica_tensor, create_replica_node
from typing import *


def get_seq_length_multiplier(node: fqir.NodeProto):
    """Returns how much the node will multiply sequence length.

    Examples: temporal_unfold(stride=2) --> 1/2
              temporal_transpose_fold(stride=2) --> 2
    """
    if node.opname == "temporal_unfold_unkernelized":
        return 1 / node.constants["stride"]
    elif node.opname == "temporal_transpose_fold_unkernelized":
        return node.constants["stride"]
    else:
        return 1


class SpecialNodeRepeatFunction:
    """This base class is used to define a rule for how a node is repeated.

    Must implement "kernelize", which returns two lists of nodes.
        The first is used to the arith graph to replace the node,
        the second list is added to init"""

    @staticmethod
    def kernelize(
        parent: fqir.NodeProto, get_tensor: Callable, num_repeats: int
    ) -> Tuple[List[fqir.NodeProto], List[fqir.NodeProto]]:
        raise NotImplementedError


class TemporalUnfoldRepeatFunction(SpecialNodeRepeatFunction):
    """Implementation of repeated (MIMO) temporal unfold"""

    def __init__(self):
        self.conv_count = 0  # use this to create uniquely named variables

    def kernelize(
        self, parent: fqir.NodeProto, get_tensor: Callable, num_repeats: int
    ) -> Tuple[List[fqir.NodeProto], List[fqir.NodeProto]]:
        nodes = []
        add_to_init = []
        constants = parent.constants
        kernel_size = constants["kernel_size"]
        stride = constants["stride"]
        dilation = constants["dilation"]

        x = parent.inputs["x"]
        y = parent.outputs[0]
        in_features = x.shape[0]

        if num_repeats == 1 and stride == 1:
            return (
                [
                    create_replica_node(
                        parent,
                        inputs={"x": get_tensor(x, 0)},
                        outputs=[get_tensor(parent.outputs[0], 0)],
                    )
                ],
                [],
            )

        if dilation != 1:
            raise ValueError(
                "Dilated TCN not supported at this moment when strides != 1 are used."
            )

        buffer_size = max((kernel_size - stride) * dilation, 0)
        buffer = []
        for i in range(buffer_size):
            _buff = fqir.TensorProto(
                name=f"tcn{self.conv_count}.buffer.{i}",
                dtype=x.dtype,
                shape=(in_features,),
                quanta=x.quanta,
            )
            buffer.append(_buff)

            init_node = fqir.NodeProto(
                name=f"tcn{self.conv_count}.buffer_init.{i}",
                optype=fqir.registry_v1["zeros"],
                inputs={},
                outputs=[_buff],
                constants={"shape": _buff.shape},
                sourceref=parent.sourceref,
            )
            add_to_init.append(init_node)

        inputs = [get_tensor(x, i) for i in range(num_repeats * stride)]
        outputs = [get_tensor(y, i) for i in range(num_repeats)]

        # the relevant part of the input sequence to the node (receptive field)
        recept = buffer + inputs

        for rpt in range(num_repeats):
            patch = []
            start = rpt * stride
            for idx in range(kernel_size):
                pidx = start + dilation * idx
                patch.append(recept[pidx])

            cat_node = fqir.NodeProto(
                name=f"{parent.name}.cat.{rpt}",
                optype=fqir.registry_v1["cat"],
                constants={"dim": 0},
                inputs={f"x{i}": patch[i] for i in range(kernel_size)},
                outputs=[outputs[rpt]],
                sourceref=parent.sourceref,
            )
            nodes.append(cat_node)

        # manually rotate the buffer
        if buffer_size > 0:
            new_buffer = recept[-buffer_size:]
            for idx, (borig, bnew) in enumerate(zip(buffer, new_buffer)):
                assign = fqir.NodeProto(
                    name=f"{parent.name}.buffer_rotation.{idx}",
                    optype=fqir.registry_v1["assign"],
                    inputs={"y": borig, "x": bnew},
                    outputs=[],
                    constants={},
                    sourceref=parent.sourceref,
                )
                nodes.append(assign)

        self.conv_count += 1
        return nodes, add_to_init


class TransposedFoldRepeatFunction(SpecialNodeRepeatFunction):
    """Implementation of repeated (MIMO) transposed fold"""

    def __init__(self):
        self.conv_count = 0  # use this to create uniquely named variables

    def kernelize(
        self, parent: fqir.NodeProto, get_tensor: Callable, num_repeats: int
    ) -> Tuple[List[fqir.NodeProto], List[fqir.NodeProto]]:
        nodes = []
        add_to_init = []
        constants = parent.constants
        kernel_size = constants["kernel_size"]
        stride = constants["stride"]
        dilation = constants["dilation"]

        if dilation != 1:
            raise ValueError("Dilated Tranposed TCN not supported at this moment.")

        x = parent.inputs["x"]
        y = parent.outputs[0]
        in_features = x.shape[0]
        out_features = y.shape[0]

        if x.dtype.endswith("16"):
            bw = 16
        elif x.dtype.endswith("8"):
            bw = 8
        else:
            raise ValueError(f"Unknown precision {x.dtype}")

        buffer_size = max(kernel_size - stride, 0)
        buffer = []
        for i in range(buffer_size):
            _buff = fqir.TensorProto(
                name=f"tpose_tcn{self.conv_count}.buffer.{i}",
                dtype=x.dtype,
                shape=(out_features,),
                quanta=y.quanta,
            )
            buffer.append(_buff)

            init_node = fqir.NodeProto(
                name=f"tpose_tcn{self.conv_count}.buffer_init.{i}",
                optype=fqir.registry_v1["zeros"],
                inputs={},
                outputs=[_buff],
                constants={"shape": _buff.shape},
                sourceref=parent.sourceref,
            )
            add_to_init.append(init_node)

        curr_buffer = [b for b in buffer]
        for rpt in range(num_repeats // stride):
            x_in = get_tensor(x, rpt)
            z_chunks = [
                create_replica_tensor(y, tag=f".chunk.{rpt}.{idx}")
                for idx in range(kernel_size)
            ]
            n_partials = len(buffer)
            n_outputs = stride
            if n_outputs > n_partials:
                for i in range(n_partials, n_outputs):
                    z_chunks[i] = get_tensor(y, i + kernel_size * rpt)
            chunk = fqir.NodeProto(
                name=f"tpose_tcn{self.conv_count}.chunk.{rpt}",
                optype=fqir.registry_v1["chunk"],
                inputs={"x": x_in},
                outputs=[z for z in z_chunks],
                constants={"chunks": kernel_size, "dim": 0},
            )
            nodes.append(chunk)
            for bidx, buff in enumerate(curr_buffer):
                if bidx < stride:
                    partial = get_tensor(y, stride * rpt + bidx)
                else:
                    partial = create_replica_tensor(y, tag=f".partial.{rpt}.{bidx}")
                add = fqir.NodeProto(
                    name=f"tpose_tcn{self.conv_count}.partial_sum.{rpt}.{bidx}",
                    optype=fqir.registry_v1["vvadd"],
                    inputs={"x": z_chunks[bidx], "y": buff},
                    outputs=[partial],
                    constants={
                        "rounded": False,
                        "shamt_x": 0,
                        "shamt_y": 0,
                        "shamt_bwred": 0,
                        "bw": bw,
                        "bw_x": bw,
                        "bw_y": bw,
                    },
                )
                nodes.append(add)
                z_chunks[bidx] = partial

            # update curr_buffer
            if len(buffer) > 0:
                curr_buffer = z_chunks[-len(buffer) :]

        # manually rotate the buffer
        if buffer_size > 0:
            for idx, (borig, bnew) in enumerate(zip(buffer, curr_buffer)):
                assign = fqir.NodeProto(
                    name=f"{parent.name}.buffer_rotation.{idx}",
                    optype=fqir.registry_v1["assign"],
                    inputs={"y": borig, "x": bnew},
                    outputs=[],
                    constants={},
                    sourceref=parent.sourceref,
                )
                nodes.append(assign)

        self.conv_count += 1
        return nodes, add_to_init


REPEAT_FUNCTIONS: Dict[str, SpecialNodeRepeatFunction] = {
    "temporal_unfold_unkernelized": TemporalUnfoldRepeatFunction(),
    "temporal_transpose_fold_unkernelized": TransposedFoldRepeatFunction(),
}


def perform_stride_optimization(graph: fqir.GraphProto):
    """Performs an optimization to the graph that identifies the overall end-to-end stride of a model
    and transforms to a single-input-single output graph.

    See the "Strided Layer" page on the documentation website for introductory details
    """

    arith = graph.subgraphs["ARITH"]
    init = graph.subgraphs.get("INIT", None)
    node_multipliers = {}
    no_init = False
    needs_init = False
    if init is None:
        no_init = True
        init = fqir.GraphProto(name="INIT")

    # create outputs and iospec
    iospec = fqir.metadata.IOMetaData()
    unbind_dim = graph.unbind_dim
    if unbind_dim is None:
        feature_dim = 0
        sequence_dim = None
    elif unbind_dim == 0:
        feature_dim = 1
        sequence_dim = 0
    else:
        feature_dim = 0
        sequence_dim = 1

    for node in arith.nodes + init.nodes:
        node_multipliers[node] = get_seq_length_multiplier(node)

    tensor_multipliers = {}
    for x in arith.inputs:
        tensor_multipliers[x] = 1
    for x in arith.parameters:
        tensor_multipliers[x] = None

    for node in init.nodes + arith.nodes:
        input_multipliers = [tensor_multipliers[x] for x in node.inputs.values()]
        input_multipliers = [x for x in input_multipliers if x is not None]
        if len(input_multipliers) >= 1:
            multiplier = input_multipliers[0]
            is_compatible = all(m == multiplier for m in input_multipliers)
            assert (
                is_compatible
            ), f"Had incompatible multipliers on node: {node}\ninput multipliers: {input_multipliers}"
        else:
            multiplier = None

        if multiplier is not None:
            multiplier = multiplier * node_multipliers[node]

        for y in node.outputs:
            tensor_multipliers[y] = multiplier

        if node.opname == "assign":
            for x in node.inputs.values():
                tensor_multipliers[x] = multiplier

    min_multiplier = min(x for x in tensor_multipliers.values() if x is not None)

    tensor_repeats = {}
    for tensor, multiplier in tensor_multipliers.items():
        if multiplier is None:
            tensor_repeats[tensor] = None
        else:
            rpt = multiplier / min_multiplier
            assert rpt % 1 == 0
            tensor_repeats[tensor] = int(rpt)

    # set repeats = None for initialized tensors
    for node in init.nodes:
        for x in node.outputs:
            tensor_repeats[x] = 1

    # Create tensor_replicas, based on number of tensor_repeats
    tensor_replicas = {}
    for tensor, repeat in tensor_repeats.items():
        if repeat is None or repeat == 1:
            tensor_replicas[tensor] = tensor
        else:
            replicas = []
            for i in range(int(repeat)):
                replicas.append(create_replica_tensor(tensor, tag=f".{i}"))
            tensor_replicas[tensor] = replicas

    def get_new_tensor(parent_tensor, idx):
        replicas = tensor_replicas[parent_tensor]
        if isinstance(replicas, fqir.TensorProto):
            return replicas
        elif idx < len(replicas):
            return replicas[idx]
        else:
            raise ValueError(
                f"Tried to get the {idx}-th replica of {parent_tensor}, only have {len(replicas)}."
            )

    node_repeats = {}
    for node in arith.nodes:
        output_repeats = [tensor_repeats[t] for t in node.outputs]
        output_repeats = [r for r in output_repeats if r is not None]

        # confirm that repeat-factors are matching
        if len(output_repeats) > 0:
            repeat = output_repeats[0]
            is_compatible = all(rpt == repeat for rpt in output_repeats)
            if not is_compatible:
                raise ValueError(
                    f"Had incompatible input repeats on node: {node}\nrepeats: {output_repeats}"
                )
        else:
            repeat = None
        node_repeats[node] = repeat

    # break graph up into blocks (based on contiguous repeat factors)
    curr_repeat = None
    blocks = []
    none_block = []
    block_repeats = []

    for node in arith.nodes:
        repeat = node_repeats[node]
        if node.opname in REPEAT_FUNCTIONS:
            blocks.append([node])
            block_repeats.append(repeat)
            curr_repeat = None
        elif repeat is None:
            if len(blocks) > 0 and blocks[-1][0].opname not in REPEAT_FUNCTIONS:
                blocks[-1].append(node)
            else:
                none_block.append(node)
        elif curr_repeat is None or repeat != curr_repeat:
            blocks.append([node])
            block_repeats.append(repeat)
            curr_repeat = repeat
        else:
            blocks[-1].append(node)

    ######
    # construct new graph, repeating each operation as needed...
    ######
    new_arith = fqir.GraphProto(
        name=arith.name, unbind_dim=arith.unbind_dim, stack_dim=arith.stack_dim
    )
    for p in arith.parameters:
        new_arith.add_parameter(get_new_tensor(p, 0))

    ####
    # construct new inputs (if needed)
    ####
    for i, x_orig in enumerate(arith.inputs):
        repeats = tensor_repeats[x_orig]
        if repeats > 1:
            x_stacked = create_replica_tensor(
                x_orig, tag="_stack", shape=(x_orig.shape[0] * repeats,)
            )
            new_arith.add_input(x_stacked)
            chunk = fqir.NodeProto(
                name=f"{x_orig.name}.chunk",
                optype=fqir.registry_v1["chunk"],
                inputs={"x": x_stacked},
                outputs=[get_new_tensor(x_orig, i) for i in range(repeats)],
                constants={"chunks": repeats, "dim": 0},
            )
            new_arith.add_node(chunk)
        else:
            new_arith.add_input(get_new_tensor(x_orig, 0))

        spec = fqir.metadata.ReshapeSpec(
            feature_dim=feature_dim,
            sequence_dim=sequence_dim,
            base_features=x_orig.shape[0],
            repeat_factor=repeats,
            is_input=True,
        )
        iospec.add_input_spec(spec)

    def get_new_node(node_orig, idx):
        try:
            inputs = {
                name: get_new_tensor(parent, idx)
                for name, parent in node_orig.inputs.items()
            }
            outputs = [get_new_tensor(parent, idx) for parent in node_orig.outputs]
            new_node = create_replica_node(
                node_orig, tag=f".{idx}", inputs=inputs, outputs=outputs
            )
        except:
            print(f"Failed to get the {idx}-th replica of {node}")
            raise
        return new_node

    # repeat the "None" repeats once at the top of the graph
    for node in none_block:
        new_node = get_new_node(node, 0)
        new_arith.add_node(new_node)

    # repeat each block by its correct number of repeats
    for block, repeat in zip(blocks, block_repeats):
        if len(block) == 1 and block[0].opname in REPEAT_FUNCTIONS:
            parent = block[0]
            kern, add_to_init = REPEAT_FUNCTIONS[parent.opname].kernelize(
                parent, get_new_tensor, repeat
            )
            for node in kern:
                new_arith.add_node(node)
            for node in add_to_init:
                needs_init = True
                init.add_node(node)
        else:
            for i in range(int(repeat)):
                for node in block:
                    assert node.opname not in REPEAT_FUNCTIONS
                    new_arith.add_node(get_new_node(node, i))

    for i, y_orig in enumerate(arith.outputs):
        repeats = tensor_repeats[y_orig]
        if repeats is not None and repeats > 1:
            new_out = create_replica_tensor(
                y_orig, tag="", shape=(repeats * y_orig.shape[0],)
            )
            cat_node = fqir.NodeProto(
                name=f"cat_out.{y_orig.name}",
                optype=fqir.registry_v1["cat"],
                inputs={f"x{i}": get_new_tensor(y_orig, i) for i in range(repeats)},
                outputs=[new_out],
                constants={"dim": 0},
            )
            new_arith.add_node(cat_node)
            new_arith.add_output(new_out)
        else:
            new_arith.add_output(get_new_tensor(y_orig, 0))

        spec = fqir.metadata.ReshapeSpec(
            feature_dim=feature_dim,
            sequence_dim=sequence_dim,
            is_input=False,
            repeat_factor=repeats,
            base_features=y_orig.shape[0],
        )
        iospec.add_output_spec(spec)

    graph.subgraphs["ARITH"] = new_arith
    graph.nodes[1].subgraph = new_arith

    if no_init and needs_init:
        init_node = fqir.NodeProto(
            name="INIT", optype=None, inputs={}, outputs=[], subgraph=init
        )
        graph.add_node(init_node)
        graph.add_subgraph("INIT", init)

    for i, x_stacked in enumerate(new_arith.inputs):
        graph.inputs[i].shape = x_stacked.shape
        graph.subgraphs["QUANT"].inputs[i].shape = x_stacked.shape
        graph.subgraphs["QUANT"].outputs[i].shape = x_stacked.shape

    for i, y_stacked in enumerate(new_arith.outputs):
        graph.outputs[i].shape = y_stacked.shape
        graph.subgraphs["DEQUANT"].inputs[i].shape = y_stacked.shape
        graph.subgraphs["DEQUANT"].outputs[i].shape = y_stacked.shape

    return {"graph": graph, "iospec": iospec}
