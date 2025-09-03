"""This FQIR pass will convert high-precision variables (e.g. int24) into int16,
and modify any GMAC operators accordingly. Will also raise errors if an int24 variable
is passed into a non-supporting operator."""
from fmot.fqir import GraphProto, TensorProto, NodeProto, registry_v1
from fmot.fqir.nodes.optypes import lshift
import logging
from typing import Union, Literal, Optional
from collections import defaultdict
from enum import Enum
from ordered_set import OrderedSet
from fmot.fqir.nodes.optypes import split_to_subprecisions
import numpy as np
from fmot.fqir.writer.utils import successors, predecessors

logger = logging.getLogger(__name__)

# helpers:


def predecessors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_pred in graph.nodes:
            if node in maybe_pred.outputs:
                yield maybe_pred

    elif isinstance(node, NodeProto):
        for x in node.inputs.values():
            yield x


def successors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_succ in graph.nodes:
            if node in maybe_succ.inputs.values():
                yield maybe_succ

    elif isinstance(node, NodeProto):
        for x in node.outputs:
            yield x


def create_lo_hi_from_i24(x: TensorProto):
    """Create low/high-bit subvectors from an initial int24 vector.

    The low vector stores the bottom 12 bits (with an unused sign bit, hence i13)
    The high vector stores the top 12 bits (including sign)

    Quantas are derived from the original tensor's quanta
    """
    if x.value is not None:
        v_lo, v_hi = split_to_subprecisions(x.value, [13, 12])
    else:
        v_lo, v_hi = None, None

    if x.quanta is not None:
        hi_q = x.quanta + 12
        lo_q = x.quanta
    else:
        hi_q = None
        lo_q = None

    hi = TensorProto(
        name=f"{x.name}_hi",
        dtype="fqint16",
        shape=x.shape,
        quanta=hi_q,  ### TODO: double check quanta values
        value=v_hi,
    )
    lo = TensorProto(
        name=f"{x.name}_lo",
        dtype="fqint16",
        shape=x.shape,
        quanta=lo_q,  ### TODO: double check quanta values
        value=v_lo,
    )
    return lo, hi


def get_offset_gmacv2(
    name: str,
    x_vv: list[TensorProto],
    y_vv: list[TensorProto],
    x_vi: list[TensorProto],
    outputs: list[TensorProto],
    bits_out: list[int],
    shamts_vv: list[int],
    shamts_vi: list[int],
    immediates_vi: list[int],
    offset: int,
    shamt_offset: int,
    arith: GraphProto,
):
    inputs = {}
    assert len(x_vv) == len(y_vv)
    assert len(x_vv) == len(shamts_vv)
    assert len(x_vi) == len(shamts_vi)
    assert len(x_vi) == len(immediates_vi)
    assert len(outputs) == len(bits_out)

    for i, x in enumerate(x_vv):
        inputs[f"x_vv_{i}"] = x
    for i, x in enumerate(y_vv):
        inputs[f"y_vv_{i}"] = x
    for i, x in enumerate(x_vi):
        inputs[f"x_vi_{i}"] = x

    if offset != 0:
        n_channels = next(iter(inputs.values())).shape[0]
        ones = TensorProto(
            name=f"{name}.ones",
            dtype="fqint16",
            shape=[n_channels],
            quanta=None,
            value=np.ones((n_channels,), dtype=np.int32),
        )
        arith.add_parameter(ones)

        inputs[f"x_vi_{len(x_vi)}"] = ones
        shamts_vi.append(shamt_offset)
        immediates_vi.append(offset)

    node = NodeProto(
        name=name,
        optype=registry_v1["gmac_v2"],
        inputs=inputs,
        outputs=outputs,
        constants={
            "shamts_vv": shamts_vv,
            "shamts_vi": shamts_vi,
            "immediates_vi": immediates_vi,
            "bits_out": bits_out,
        },
    )
    return node


RuleType = Enum(
    "RuleType",
    [
        # A PRODUCE RuleType annotates that a PropagatorRule should be applied to a node if it produces an
        #   int24 output
        # PRODUCE rules are applied when we detect that a node has an int24 output, and
        #   are independent of input precisions.
        # Example: if a GMACv2 produces an int24, we can precision-split its output into two i16 outputs
        #   without any consideration of the input precisions.
        "PRODUCE",
        # A CONSUME_ANY RuleType annotates that a PropagatorRule should be applied to a node if any of its inputs
        #   are int24 AND we have a mapping from the original int24 input to two int16 subvectors
        # We wait to apply a CONSUME_ANY rule until the mapping from int24 to (int16, int16) has been added
        #   to the bank
        # Example: if a GMACv2 consumes an int24 operand, and we have mapped this int24 operand to x_lo, x_hi,
        #   then we can replace the int24 operand with the x_lo and x_hi precision-split versions.
        "CONSUME_ANY",
        # A CONSUME_ALL RuleType annotates that a PropagatorRule should be applied to a node if ALL of its
        #   int24 inputs have been mapped to int16 subvectors
        # We wait to apply a CONSUME_ALL rule until the mapping from int24 to (int16, int16) has been added
        #   to the bank for EVERY one of the int24 inputs. Note that it is legal in some cases for the node to
        #   have a mix of int16 and int24 inputs -- we may just do nothing to the int16 inputs.
        # Example: z = CAT([x, y]) where x and y are int24. We will wait until we have mappings x -> (x_lo, x_hi)
        #   and y -> (y_lo, y_hi). Once these mappings exist, we will replace the original CAT node with two CAT nodes:
        #        z_hi = CAT([x_hi, y_hi])
        #        z_lo = CAT([x_lo, y_lo])
        #   note that we could not have performed this re-write intil ALL of the inputs had mappings to i16x2.
        "CONSUME_ALL",
    ],
)


# Propagator Rules:


class PropagatorRule:
    """Base Class for an int24 Propagator.

    Arguments:
        opname (str): the FQIR optype name (e.g. "gmac_v2", "cat", "vvadd", ...)
        rule_type (RuleType): configures the conditions that need to be satisifed when we will call this rule.
            See above comments to see how the different RuleTypes configure this behavior
    """

    opname: str
    rule_type: RuleType

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        input_origs: Optional[dict[str, TensorProto]] = None,
    ):
        """
        Arguments:
            node (NodeProto): the node to be modified / replaced in the graph
            arith (GraphProto): the arithmetic graph to be edited
            bank (dict[Tensor, [Tensor, Tensor]]): a dictionary containing all of the active mapping from
                int24 tensors to pairs of int16 vectors (x_orig: i24 -> (x_hi: i16, x_lo: i16))
            subgraph_bank (dict[Tensor, [Tensor, Tensor]]): a dictionary containing all of the active mapping from
                int24 tensors to pairs of int16 vectors *for direct subgraphs* (x_orig: i24 -> (x_hi: i16, x_lo: i16))
            input_origs (optional): a dictionary containing the original int24 input tensors to the node, keyed by the
                argument-names. For example, for a node that takes in "x" and "y" arguements,
                this could be {"x": <original_int24_input>, "y": <original_int24_input>}. This is only used in CONSUME rules
                (CONSUME_ANY, CONSUME_ALL)
        """
        raise NotImplementedError()


class GMACv2ProduceRule(PropagatorRule):
    """Split the int24 output into two int16 subvectors, using GMACv2's "bits_out" field."""

    opname = "gmac_v2"
    rule_type = RuleType.PRODUCE

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        assert node.opname == "gmac_v2"

        bws_out = node.constants["bits_out"]

        if len(bws_out) == 1 and sum(bws_out) == 24:
            # modify the node in-place and create new hi/lo output tensors

            node.constants["bits_out"] = [13, 12]
            out24 = node.outputs[0]
            assert out24.dtype == "fqint24"

            out_lo, out_hi = create_lo_hi_from_i24(out24)

            node.outputs = [out_lo, out_hi]

            logger.debug(f"gmac_v2 int24 output has been split {node}")

            # add to the bank
            bank[out24] = (out_lo, out_hi)


class GMACv2ConsumeRule(PropagatorRule):
    """
    Replace reference to original int24 input with the split int16 subvectors.

    Examples:
        1) Propagating split precisions into vector-vector terms:
                gmac_v2(x_vv_0=XORIG, y_vv_0=y, ..., shifts_vv=[S, ...])
            Where XORIG is int24 and has been split to (XLO, XHI) int16 subvectors.
            We break this into two terms, both multiplying the same y, and use new shift-amounts:
                gmac_v2(
                    x_vv_0=XLO, y_vv_0=y,
                    x_vv_1=XHI, y_vv_1=y,
                    ...
                    shifts_vv=[S, S+12, ...])
        2) Propagating split precisions into vector-immediate terms:
                gmac_v2(..., x_vi_0=XORIG, ..., immediates_vi=[I, ...], shamts_vi=[S, ...])
            Where XORIG is int24 and has been split to (XLO, XHI) int16 subvectors.
            We break this into two terms, both multiplying the same immediate, and use new shift-amounts:
                gmac_v2(
                    ...
                    x_vi_0=XLO,
                    x_vi_1=XHI,
                    ...,
                    immediate_vi=[I, I, ...]
                    shifts_vi=[S, S+12, ...])
    """

    opname = "gmac_v2"
    rule_type = RuleType.CONSUME_ANY

    def __init__(self):
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.num_vv = 0
        self.num_vi = 0
        self.node: NodeProto = None

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Modifies a gmac_v2 consumer of an int24 tensor based on upstream splitting"""
        assert node.opname == "gmac_v2"
        if node.name.startswith(r"mul.%muli.1.%add.69"):
            print("BEFORE:")
            print(node)
            print(node.constants)

        self.num_vv = 0
        self.num_vi = 0
        self.bank = bank
        self.node = node

        for key in node.inputs.keys():
            if key.startswith("x_vv_"):
                self.num_vv += 1
            elif key.startswith("x_vi_"):
                self.num_vi += 1

        for key, input_orig in inputs_orig.items():
            if key.startswith("x_vv"):
                self.prop_vv(key, input_orig)
            elif key.startswith("y_vv"):
                self.prop_vv(key, input_orig)
            elif key.startswith("x_vi"):
                self.prop_vi(key, input_orig)

        if node.name.startswith(r"mul.%muli.1.%add.69"):
            print("AFTER:")
            print(node)
            print(node.constants)
            print()

    def prop_vv(self, key: str, input_orig: TensorProto):
        id = key.split("_vv_")[0]  # "x" or "y"
        other_id = {"x": "y", "y": "x"}[id]
        idx = int(key.split("_vv_")[1])  # integer index

        shamt = self.node.constants["shamts_vv"][idx]

        lo, hi = self.bank[input_orig]

        # we had a single term:
        #  (x24 * other) << shamt
        # we will transform it to:
        #  (x_lo * other) << shamt_lo + (x_hi * other) << shamt_hi
        # where x24 = x_lo + 2**12 * x_hi
        # therefore, shamt_lo = shamt, shamt_hi = shamt + 12

        # update current product to use x_lo (no change to shamt)
        self.node.inputs[key] = lo

        # create new partial product for x_hi * other >> shamt + 12
        self.node.inputs[f"{id}_vv_{self.num_vv}"] = hi
        self.node.inputs[f"{other_id}_vv_{self.num_vv}"] = self.node.inputs[
            f"{other_id}_vv_{idx}"
        ]
        self.node.constants["shamts_vv"].append(shamt + 12)

        self.num_vv += 1

        logger.debug(
            f" propagated int24 input splitting {input_orig} into gmac_v2 through key {key}"
        )

    def prop_vi(self, key: str, input_orig: TensorProto):
        idx = int(key.split("x_vi_")[1])
        imm = self.node.constants["immediates_vi"][idx]
        shamt = self.node.constants["shamts_vi"][idx]

        # we had a single term:
        #  (x24 * imm) << shamt
        # we will transform it to:
        #  (x_lo * im) << shamt_lo + (x_hi * imm) << shamt_hi
        # where x24 = x_lo + 2**12 * x_hi
        # therefore, shamt_lo = shamt, shamt_hi = shamt + 12

        if shamt + 12 <= 0:
            self.node.constants["immediates_vi"].append(imm)
            self.node.constants["shamts_vi"].append(shamt + 12)
        else:
            new_imm = imm << (shamt + 12)
            if new_imm >= -(2**23) and new_imm < 2**23:
                self.node.constants["immediates_vi"].append(new_imm)
                self.node.constants["shamts_vi"].append(0)
            else:
                # raise ValueError(
                #     f"Infeasible shift-amount and immediate combination: shamt: {shamt+12} imm: {new_imm} in node {self.node}\n{self.node.constants}"
                # )
                self.node.constants["immediates_vi"].append(imm)
                self.node.constants["shamts_vi"].append(shamt + 12)

        lo, hi = self.bank[input_orig]

        self.node.inputs[key] = lo
        self.node.inputs[f"x_vi_{self.num_vi}"] = hi

        self.num_vi += 1

        logger.debug(
            f" propagated int24 input splitting {input_orig} into gmac_v2 through key {key}"
        )


class CatConsumeRule(PropagatorRule):
    """Break a CAT node into two parallel CAT nodes, for the _lo and _hi subvectors.

    CONSUME_ALL --> all int24 inputs must be mapped before we can apply this rule."""

    opname = "cat"
    rule_type = RuleType.CONSUME_ALL

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Create two parallel concatenation nodes, each focused on the lo and hi parts of the
        vector."""

        assert node.opname == "cat"

        logger.debug(f"Arith before:\n{arith}")

        output_orig = node.outputs[0]
        new_lo, new_hi = create_lo_hi_from_i24(output_orig)

        inputs_lo = {}
        inputs_hi = {}
        for key, input_orig in inputs_orig.items():
            lo, hi = bank[input_orig]
            inputs_lo[key] = lo
            inputs_hi[key] = hi

        cat_lo = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1["cat"],
            inputs=inputs_lo,
            outputs=[new_lo],
            constants=node.constants.copy(),
        )

        cat_hi = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1["cat"],
            inputs=inputs_hi,
            outputs=[new_hi],
            constants=node.constants.copy(),
        )

        # insert these new cat nodes before the original cat node
        # and then remove it
        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, cat_lo)
        arith.nodes.insert(idx, cat_hi)
        arith.nodes.remove(node)

        # add new lo/hi tensors to the bank
        bank[output_orig] = (new_lo, new_hi)

        logger.debug(f"Arith after:\n{arith}")


class AssignConsumeRule(PropagatorRule):
    """Break an ASSIGN node into two parallel ASSIGN nodes, for the _lo and _hi subvectors

    CONSUME_ALL --> all int24 inputs must be mapped before we can apply this rule."""

    opname = "assign"
    rule_type = RuleType.CONSUME_ALL

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        x_orig = node.inputs["x"]
        y_orig = node.inputs["y"]

        x_lo, x_hi = bank[x_orig]
        y_lo, y_hi = bank[y_orig]

        assign_lo = NodeProto(
            name=f"{node.name}_lo",
            optype=registry_v1["assign"],
            inputs={"x": x_lo, "y": y_lo},
            outputs=[],
            constants={},
        )

        assign_hi = NodeProto(
            name=f"{node.name}_hi",
            optype=registry_v1["assign"],
            inputs={"x": x_hi, "y": y_hi},
            outputs=[],
            constants={},
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, assign_lo)
        arith.nodes.insert(idx, assign_hi)
        arith.nodes.remove(node)

        logger.debug(f"Virtualized assign {node} to i24")


class ConvertShiftToGMACv2(PropagatorRule):
    """If a SHIFT consumes int24, we will convert it to an equivalent GMACv2.
    The GMACv2 rules will be applied on the next step of propagation.
    """

    opname = "shift"
    rule_type = RuleType.CONSUME_ANY

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        assert node.opname == "shift"

        # convert shift to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt = node.constants["shamt"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]

        if shamt <= 0:
            new_shamt = shamt
            imm = 1
        else:
            new_shamt = 0
            imm = 2**shamt
            if shamt > 24:
                raise ValueError("Extreme shamt of > 24 cannot be converted to gmac_v2")

        if rounded:
            round_offset = int(2 ** (-shamt - 1))
            round_shamt = shamt
        else:
            round_offset = 0
            round_shamt = 0

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[],
            y_vv=[],
            x_vi=[node.inputs["x"]],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[],
            shamts_vi=[new_shamt],
            immediates_vi=[imm],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        arith.nodes.remove(node)

        logger.debug(f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}")


class ChunkConsumeRule(PropagatorRule):
    """Break an CHUNK node into two parallel CHUNK nodes, for the _lo and _hi subvectors

    Same logic is reused for SplitConsumeRule (identical signature/approach)"""

    opname = "chunk"
    rule_type = RuleType.CONSUME_ANY

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Create two parallel concatenation nodes, each focused on the lo and hi parts of the
        vector."""

        assert node.opname == self.opname

        outs_hi = []
        outs_lo = []

        if "x" not in inputs_orig:
            raise ValueError(f"{inputs_orig=}")

        lo, hi = bank[inputs_orig["x"]]

        for output in node.outputs:
            new_lo, new_hi = create_lo_hi_from_i24(output)
            outs_hi.append(new_hi)
            outs_lo.append(new_lo)

            bank[output] = (new_lo, new_hi)

        chunk_lo = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1[self.opname],
            inputs={"x": lo},
            outputs=outs_lo,
            constants=node.constants.copy(),
        )
        chunk_hi = NodeProto(
            name=node.name + "_hi",
            optype=registry_v1[self.opname],
            inputs={"x": hi},
            outputs=outs_hi,
            constants=node.constants.copy(),
        )

        # insert these new chunk nodes before the original cat node
        # and then remove it
        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, chunk_lo)
        arith.nodes.insert(idx, chunk_hi)
        arith.nodes.remove(node)

        logger.debug(f"Replaced chunk {node} with\n{chunk_lo}\n{chunk_hi}")


class SplitConsumeRule(ChunkConsumeRule):
    """Very simple subclass of ChunkConsumeRule, just need to change opname to 'split'"""

    opname = "split"


class LoopConsumeRule(PropagatorRule):
    opname = "loop"
    rule_type = RuleType.CONSUME_ANY

    def __init__(self):
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.node: NodeProto = None
        self.subgraph: GraphProto = None

    @property
    def n_recurse(self):
        return self.node.constants["n_recurse"]

    @n_recurse.setter
    def n_recurse(self, value):
        self.node.constants["n_recurse"] = value

    @property
    def n_sliced(self):
        return self.node.constants["n_sliced"]

    @n_sliced.setter
    def n_sliced(self, value):
        self.node.constants["n_sliced"] = value

    @property
    def n_scope(self):
        return self.node.constants["n_scope"]

    @n_scope.setter
    def n_scope(self, value):
        self.node.constants["n_scope"] = value

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        self.bank = bank
        self.subgraph_bank = subgraph_bank
        self.node = node
        self.subgraph = node.subgraph

        logger.debug(f"\n{self.subgraph_bank=}\n")
        logger.debug(f"{self.subgraph.inputs=}\n")
        logger.debug(f"{self.subgraph.outputs=}\n")

        for name, x_orig in inputs_orig.items():
            if x_orig.dtype == "fqint24":
                logger.debug(f"{name=}")
                logger.debug(f"{self.subgraph.inputs=}\n")
                if name.startswith("x_sliced"):
                    self.prop_slice(name, x_orig)
                elif name.startswith("x_recurse"):
                    self.prop_recurse(name, x_orig)
                elif name.startswith("x_scope"):
                    self.prop_scope(name, x_orig)
                else:
                    raise NotImplementedError(f"port {name = } not implemented")

    def prop_slice(self, name: str, x_orig: TensorProto):
        logger.debug(f"{self.subgraph.inputs=}")
        idx = int(name.split("x_sliced_")[1])
        lo, hi = self.bank[x_orig]

        self.node.inputs[name] = lo
        self.node.inputs[f"x_sliced_{self.n_sliced}"] = hi

        logger.debug(f"{self.subgraph.inputs=}")

        sub_idx_lo = self.n_recurse + idx
        sub_x = self.subgraph.inputs[sub_idx_lo]

        sub_x_lo, sub_x_hi = self.subgraph_bank[sub_x]

        self.subgraph.inputs[sub_idx_lo] = sub_x_lo
        self.subgraph.inputs.insert(self.n_recurse + self.n_sliced, sub_x_hi)

        self.n_sliced += 1

        # update block_size_sliced and reverse_sliced constants
        self.node.constants["block_size_sliced"].append(
            self.node.constants["block_size_sliced"][idx]
        )
        self.node.constants["reverse_sliced"].append(
            self.node.constants["reverse_sliced"][idx]
        )

        logger.debug(
            f" propagated int24 input splitting {x_orig} into loop through key {name}"
        )

    def prop_recurse(self, name: str, x_orig: TensorProto):
        idx = int(name.split("x_recurse_")[1])
        lo, hi = self.bank[x_orig]

        self.node.inputs[name] = lo
        self.node.inputs[f"x_recurse_{self.n_recurse}"] = hi

        sub_idx_lo = idx
        sub_x = self.subgraph.inputs[sub_idx_lo]

        sub_x_lo, sub_x_hi = self.subgraph_bank[sub_x]

        self.subgraph.inputs[sub_idx_lo] = sub_x_lo
        self.subgraph.inputs.insert(self.n_recurse, sub_x_hi)

        # also need to handle recursed outputs!
        subgraph_output_orig = self.subgraph.outputs[idx]
        sub_x_lo, sub_x_hi = self.subgraph_bank[subgraph_output_orig]
        self.subgraph.outputs[idx] = sub_x_lo
        self.subgraph.outputs.insert(self.n_recurse, sub_x_hi)

        self.n_recurse += 1

        logger.debug(
            f" propagated int24 input splitting {x_orig} into loop through key {name}"
        )

    def prop_scope(self, name: str, x_orig: TensorProto):
        idx = int(name.split("x_scope_")[1])
        lo, hi = self.bank[x_orig]

        self.node.inputs[name] = lo
        self.node.inputs[f"x_scope_{self.n_scope}"] = hi

        sub_idx_lo = self.n_recurse + self.n_sliced + idx
        sub_x = self.subgraph.inputs[sub_idx_lo]

        sub_x_lo, sub_x_hi = self.subgraph_bank[sub_x]

        self.subgraph.inputs[sub_idx_lo] = sub_x_lo
        self.subgraph.inputs.insert(
            self.n_recurse + self.n_sliced + self.n_scope, sub_x_hi
        )

        self.n_scope += 1

        logger.debug(
            f" propagated int24 input splitting {x_orig} into loop through key {name}"
        )


class LoopProduceRule(PropagatorRule):
    opname = "loop"
    rule_type = RuleType.PRODUCE

    def __init__(self):
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.node: NodeProto = None
        self.subgraph: GraphProto = None

    @property
    def n_recurse(self):
        return self.node.constants["n_recurse"]

    @property
    def n_concat(self):
        return self.node.constants["n_concat"]

    @n_concat.setter
    def n_concat(self, value):
        self.node.constants["n_concat"] = value

    @property
    def n_final(self):
        return self.node.constants["n_final"]

    @n_final.setter
    def n_final(self, value):
        self.node.constants["n_final"] = value

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        self.bank = bank
        self.subgraph_bank = subgraph_bank
        self.node = node
        self.subgraph = node.subgraph

        logger.debug(
            f"calling loop produce rule!\n{self.node.outputs=}\n{self.subgraph.outputs=}"
        )

        # indices will be changed as we modify in-place.
        # only do one modification at a time; continue until there's nothing left to do
        while any(x.dtype == "fqint24" for x in self.node.outputs):
            for i, x_orig in enumerate(node.outputs):
                if x_orig.dtype == "fqint24":
                    if i < self.n_concat:
                        self.prop_concat(i, x_orig)
                    else:
                        self.prop_final(i - self.n_concat, x_orig)
                    break

    def prop_concat(self, idx: int, x_orig: TensorProto):
        """
        1. create new lo/hi split-precision subvectors, add these to the bank
        2. replace the original output with these new lo/hi subvectors
        3. replace the subgraph's output with the new lo/hi subvectors (already in the subgraph bank)
        4. update node constants: increment n_concat and append to reverse_concat
        """
        logger.debug("calling prop_concat")
        # 1.
        lo, hi = create_lo_hi_from_i24(x_orig)
        self.bank[x_orig] = (lo, hi)

        # 2.
        output_idx = idx
        self.node.outputs[output_idx] = lo
        self.node.outputs.insert(self.n_concat, hi)

        # 3.
        sub_out_idx = self.n_recurse + output_idx
        sub_x = self.subgraph.outputs[sub_out_idx]
        sub_lo, sub_hi = self.subgraph_bank[sub_x]
        self.subgraph.outputs[sub_out_idx] = sub_lo
        self.subgraph.outputs.insert(self.n_recurse + self.n_concat, sub_hi)

        # 4.
        self.n_concat += 1
        self.node.constants["reverse_concat"].append(
            self.node.constants["reverse_concat"][idx]
        )

        logger.debug(f"{x_orig=} {sub_x=} {self.subgraph.outputs=}")

    def prop_final(self, idx: int, x_orig: TensorProto):
        """
        1. create new lo/hi split-precision subvectors, add these to the bank
        2. replace the original output with these new lo/hi subvectors
        3. replace the subgraph's output with the new lo/hi subvectors (already in the subgraph bank)
        4. update node constants: increment n_final
        """
        logger.debug("calling prop_final")
        # 1.
        lo, hi = create_lo_hi_from_i24(x_orig)
        self.bank[x_orig] = (lo, hi)

        # 2.
        output_idx = self.n_concat + idx
        self.node.outputs[output_idx] = lo
        self.node.outputs.insert(self.n_concat + self.n_final, hi)

        # 3.
        sub_out_idx = self.n_recurse + output_idx
        sub_x = self.subgraph.outputs[sub_out_idx]
        sub_lo, sub_hi = self.subgraph_bank[sub_x]
        self.subgraph.outputs[sub_out_idx] = sub_lo
        self.subgraph.outputs.insert(
            self.n_recurse + self.n_concat + self.n_final, sub_hi
        )

        # 4.
        self.n_final += 1

        logger.debug(f"{x_orig=} {sub_x=} {self.subgraph.outputs=}")


class LegalizationRule:
    """Base class for a node legalization rule. This will not change add nodes to the graph, only
    change the internal constants within a node. May also add new input connections to the node (but these
    will be repeated connections to inputs that already exist.)

    An example is for GMACv2, if an immediate is int24, this should be broken into two int16 immediates.
    """

    opname: str

    @staticmethod
    def apply(node: NodeProto):
        raise NotImplementedError()


class GMACv2Legalizer(LegalizationRule):
    """Fixes any crazy shamts..."""

    opname = "gmac_v2"

    @staticmethod
    def apply(node: NodeProto):
        imms = node.constants["immediates_vi"]
        shamts = node.constants["shamts_vi"]

        vmin, vmax = -(2**15), 2**15 - 1

        for i, (imm, shamt) in enumerate(zip(imms, shamts)):
            # check if the immediate is int16 or not
            if imm < vmin or imm > vmax:
                logger.debug(f"GMAC immediate needs splitting! {imm=}")

                b_lo = min(1 - shamt, 13)
                b_lo = max(b_lo, 9)
                b_hi = 25 - b_lo

                assert b_hi <= 16, f"{b_hi=}, needs to be <= 16"

                imm_lo, imm_hi = split_to_subprecisions(np.array([imm]), [b_lo, b_hi])
                imm_lo = imm_lo[0].item()
                imm_hi = imm_hi[0].item()

                logger.debug(f"{imm_lo=} {imm_hi=}")

                reconst = 2 ** (b_lo - 1) * imm_hi + imm_lo
                logger.debug(f"{reconst=} {imm=} {(reconst - imm)=}")

                shamt_lo = shamt
                shamt_hi = shamt + b_lo - 1

                x = node.inputs[f"x_vi_{i}"]

                if imm_lo != 0:
                    node.constants["shamts_vi"][i] = shamt_lo
                    node.constants["immediates_vi"][i] = imm_lo

                    # add an additional connection to multiply with "imm_hi"
                    n_vi = len(node.constants["shamts_vi"])
                    node.inputs[f"x_vi_{n_vi}"] = x
                    node.constants["shamts_vi"].append(shamt_hi)
                    node.constants["immediates_vi"].append(imm_hi)

                    logger.debug(
                        f"splitting gmac_v2 vi partial:\n original:\t{x} * {imm} >> {-shamt} "
                        f"\n new:\t{x} * {imm_lo} >> {-shamt_lo} + {x} * {imm_hi} >> {-shamt_hi}"
                    )

                else:
                    node.constants["shamts_vi"][i] = shamt_hi
                    node.constants["immediates_vi"][i] = imm_hi

                    logger.debug(
                        f"converting gmac_v2 vi partial:\n original:\t{x} * {imm} >> {-shamt} "
                        f"\n new:\t{x} * {imm_hi} >> {-shamt_hi}"
                    )

        for key in ["shamts_vi", "shamts_vv", "immediates_vi"]:
            node.constants[key] = [int(x) for x in node.constants[key]]


class LoweringRule:
    """Base class for a node lowering rule. This will in-place replace a given node with a new node, without
    modifying any of the input and output operands. Unlike a Legalization rule, this will change the node-type.

    An example is for VVADD, if any input or output is i24, it should be converted to an equivalent GMAC.
    """

    opname: str

    @staticmethod
    def has_i24_args(node: NodeProto):
        return any(
            x.dtype == "fqint24" for x in node.outputs + list(node.inputs.values())
        )

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        raise NotImplementedError()


def get_add_shamt_and_imm(shamt):
    if shamt <= 0:
        new_shamt = shamt
        imm = 1
    else:
        new_shamt = 0
        imm = 2**shamt
        if shamt > 24:
            raise ValueError("Extreme shamt of > 24 cannot be converted to gmac_v2")
    return new_shamt, imm


class VVADDLoweringRule(LoweringRule):
    opname = "vvadd"

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        """Replace vvadd with GMACv2 if any input or output is i24"""

        # only convert if there are any fqint24 input / outputs
        if not LoweringRule.has_i24_args(node):
            return

        # convert vvadd to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt_x = node.constants["shamt_x"]
        shamt_y = node.constants["shamt_y"]
        shamt_z = node.constants["shamt_bwred"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]
        x = node.inputs["x"]
        y = node.inputs["y"]

        if shamt_x < 0:
            x_new = TensorProto(name=f"{x.name}_shift", dtype=x.dtype, shape=x.shape)
            x_op = get_offset_gmacv2(
                name=f"{x.name}_shift_op",
                x_vv=[],
                y_vv=[],
                x_vi=[x],
                outputs=[x_new],
                bits_out=[node.constants["bw_x"]],
                shamts_vv=[],
                shamts_vi=[shamt_x],
                immediates_vi=[1],
                offset=0,
                shamt_offset=0,
                arith=arith,
            )
            x = x_new
            shamt_x = 0
        else:
            x_op = None

        if shamt_y < 0:
            y_new = TensorProto(name=f"{y.name}_shift", dtype=y.dtype, shape=y.shape)
            y_op = get_offset_gmacv2(
                name=f"{y.name}_shift_op",
                x_vv=[],
                y_vv=[],
                x_vi=[y],
                outputs=[y_new],
                bits_out=[node.constants["bw_y"]],
                shamts_vv=[],
                shamts_vi=[shamt_y],
                immediates_vi=[1],
                offset=0,
                shamt_offset=0,
                arith=arith,
            )
            y = y_new
            shamt_y = 0
        else:
            y_op = None

        shamt_x, imm_x = get_add_shamt_and_imm(shamt_x + shamt_z)
        shamt_y, imm_y = get_add_shamt_and_imm(shamt_y + shamt_z)

        if rounded:
            round_offset = int(2 ** (-shamt_z - 1))
            round_shamt = shamt_z
        else:
            round_offset, round_shamt = (0, 0)

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[],
            y_vv=[],
            x_vi=[x, y],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[],
            shamts_vi=[shamt_x, shamt_y],
            immediates_vi=[imm_x, imm_y],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        if x_op is not None:
            arith.nodes.insert(idx, x_op)
        if y_op is not None:
            arith.nodes.insert(idx, y_op)
        arith.nodes.remove(node)

        logger.debug(
            f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}, preceded by {x_op}, {y_op}"
        )


class VVSUBLoweringRule(LoweringRule):
    opname = "vvsub"

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        """Replace vvsub with GMACv2 if any input or output is i24"""

        # only convert if there are any fqint24 input / outputs
        if not LoweringRule.has_i24_args(node):
            return

        # convert vvadd to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt_x = node.constants["shamt_x"]
        shamt_y = node.constants["shamt_y"]
        shamt_z = node.constants["shamt_bwred"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]
        x = node.inputs["x"]
        y = node.inputs["y"]

        if shamt_x < 0:
            x_new = TensorProto(name=f"{x.name}_shift", dtype=x.dtype, shape=x.shape)
            x_op = get_offset_gmacv2(
                name=f"{x.name}_shift_op",
                x_vv=[],
                y_vv=[],
                x_vi=[x],
                outputs=[x_new],
                bits_out=[node.constants["bw_x"]],
                shamts_vv=[],
                shamts_vi=[shamt_x],
                immediates_vi=[1],
                offset=0,
                shamt_offset=0,
                arith=arith,
            )
            x = x_new
            shamt_x = 0
        else:
            x_op = None

        if shamt_y < 0:
            y_new = TensorProto(name=f"{y.name}_shift", dtype=y.dtype, shape=y.shape)
            y_op = get_offset_gmacv2(
                name=f"{y.name}_shift_op",
                x_vv=[],
                y_vv=[],
                x_vi=[y],
                outputs=[y_new],
                bits_out=[node.constants["bw_y"]],
                shamts_vv=[],
                shamts_vi=[shamt_y],
                immediates_vi=[1],
                offset=0,
                shamt_offset=0,
                arith=arith,
            )
            y = y_new
            shamt_y = 0
        else:
            y_op = None

        shamt_x, imm_x = get_add_shamt_and_imm(shamt_x + shamt_z)
        shamt_y, imm_y = get_add_shamt_and_imm(shamt_y + shamt_z)
        imm_y *= -1

        if rounded:
            round_offset = int(2 ** (-shamt_z - 1))
            round_shamt = shamt_z
        else:
            round_offset, round_shamt = (0, 0)

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[],
            y_vv=[],
            x_vi=[x, y],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[],
            shamts_vi=[shamt_x, shamt_y],
            immediates_vi=[imm_x, imm_y],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        if x_op is not None:
            arith.nodes.insert(idx, x_op)
        if y_op is not None:
            arith.nodes.insert(idx, y_op)
        arith.nodes.remove(node)

        logger.debug(
            f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}, preceded by {x_op}, {y_op}"
        )


class VVMULLoweringRule(LoweringRule):
    opname = "vvmul"

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        """Replace vvmul with GMACv2 if any input or output is i24"""

        # only convert if there are any fqint24 input / outputs
        if not LoweringRule.has_i24_args(node):
            return

        # convert vvadd to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt = node.constants["shamt_bwred"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]

        if rounded:
            round_offset = int(2 ** (-shamt - 1))
            round_shamt = shamt
        else:
            round_offset, round_shamt = (0, 0)

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[node.inputs["x"]],
            y_vv=[node.inputs["y"]],
            x_vi=[],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[shamt],
            shamts_vi=[],
            immediates_vi=[],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        arith.nodes.remove(node)

        logger.debug(f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}")


class VIMULLoweringRule(LoweringRule):
    opname = "vimul"

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        """Replace vimul with GMACv2 if any input or output is i24"""

        # only convert if there are any fqint24 input / outputs
        if not LoweringRule.has_i24_args(node):
            return

        # convert vvadd to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt = node.constants["shamt_bwred"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]
        imm = node.constants["y"]

        if rounded:
            round_offset = int(2 ** (-shamt - 1))
            round_shamt = shamt
        else:
            round_offset, round_shamt = (0, 0)

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[],
            y_vv=[],
            x_vi=[node.inputs["x"]],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[],
            shamts_vi=[shamt],
            immediates_vi=[imm],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        arith.nodes.remove(node)

        logger.debug(f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}")


class VIADDLoweringRule(LoweringRule):
    opname = "viadd"

    @staticmethod
    def apply(arith: GraphProto, node: NodeProto):
        """Replace viadd with GMACv2 if any input or output is i24"""

        # only convert if there are any fqint24 input / outputs
        if not LoweringRule.has_i24_args(node):
            return

        # convert vvadd to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt_x = node.constants["shamt_x"]
        shamt_y = node.constants["shamt_y"]
        shamt_z = node.constants["shamt_bwred"]
        imm_y = node.constants["y"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]

        # statically shift the immediate
        imm_y = lshift(imm_y, shamt_y)
        shamt_y = 0

        x = node.inputs["x"]

        y = TensorProto(
            name=f"{node.name}-dummy-ones",
            dtype="fqint16",
            shape=node.outputs[0].shape,
            quanta=0,
            value=np.ones(node.outputs[0].shape, dtype=np.int32),
        )
        arith.add_parameter(y)

        shamt_x, imm_x = get_add_shamt_and_imm(shamt_x + shamt_z)
        shamt_y = shamt_y + shamt_z

        if rounded:
            round_offset = int(2 ** (-shamt_z - 1))
            round_shamt = shamt_z
        else:
            round_offset, round_shamt = (0, 0)

        gmac_equiv = get_offset_gmacv2(
            name=node.name + "_as_gmac_v2",
            x_vv=[],
            y_vv=[],
            x_vi=[x, y],
            outputs=node.outputs,
            bits_out=[bw],
            shamts_vv=[],
            shamts_vi=[shamt_x, shamt_y],
            immediates_vi=[imm_x, imm_y],
            offset=round_offset,
            shamt_offset=round_shamt,
            arith=arith,
        )

        logger.debug(gmac_equiv)
        logger.debug(gmac_equiv.constants)

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        arith.nodes.remove(node)

        logger.debug(f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}")
        logger.debug(f"{node.constants=}")
        logger.debug(f"{gmac_equiv.constants=}")


class VirtualI24Propagator:
    """Converts int24 tensors into two int16 tensors, based on an i13/i12 split.

    Iteratively converts int24 tensors to int13/int12 and propagates these changes
    through the rest of the graph.

    The algorithm to propagate precision-splitting maintains a *bank*, a dictionary mapping from the
    original int24 variable to the (lo, hi) precision-split variables. At each iteration of the algo we:
        1. Split any gmac_v2 int24 outputs and add these to the bank
        2. Visit all children of tensors in the bank. For each of these:
            - Raise an exception if there is no known method of propagating int24 precision
            given the node's optype
            - If the node is satisfied by the bank's contents, call the appropriate propagation
                function on this node, which may add new split vectors to the bank.
                A node is satisfied if we have enough of its inputs in the bank that we can propagate
                int24 precision-splitting through it. Concatenation is an important example, where we
                will want to wait until all of the cat node's inputs have been split before attempting to
                split the cat.
        3. Clear out any tensors from the bank which no longer are being consumed in the graph

    We repeat this process until the bank is empty (or we hit an error). To avoid infinite-spinning,
    if the bank has not changed between two iterations, we will also throw an error.
    """

    def __init__(self, arith: GraphProto, init: Optional[GraphProto] = None):
        self.arith = arith
        self.init = init
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = {}
        self.subgraph_bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = {}
        # stores mappings from original outputs to precision-split outputs
        self.output_bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = {}

        # maintain these lists as we define new rules

        self.lowerings: list[type[LoweringRule]] = [
            VVADDLoweringRule,
            VVSUBLoweringRule,
            VVMULLoweringRule,
            VIMULLoweringRule,
            VIADDLoweringRule,
        ]

        self.rules: list[type[PropagatorRule]] = [
            GMACv2ConsumeRule,
            GMACv2ProduceRule,
            CatConsumeRule,
            ChunkConsumeRule,
            SplitConsumeRule,
            ConvertShiftToGMACv2,
            AssignConsumeRule,
            LoopConsumeRule,
            LoopProduceRule,
        ]

        self.legalizers: list[type[LegalizationRule]] = [GMACv2Legalizer]

        # automatically create a mapping of opnames to rules
        self.opname_to_rules = defaultdict(list[type[PropagatorRule]])
        for rule in self.rules:
            self.opname_to_rules[rule.opname].append(rule)

        # raise an error if there is more than one rule of a given type for a given operator
        for opname, rules in self.opname_to_rules.items():
            ruletypes = set()
            for rule in rules:
                if rule.rule_type in ruletypes:
                    raise ValueError(
                        f"More than one rule of type {rule.rule_type} has been defined for {opname}"
                    )
                ruletypes.add(rule.rule_type)

        # automatically create a mapping of opnames to legalizers
        self.opname_to_legalizers = defaultdict(list[type[LegalizationRule]])
        for legalizer in self.legalizers:
            self.opname_to_legalizers[legalizer.opname].append(legalizer)

        # automatically create a mapping of opnames to lowerings
        self.opname_to_lowerings = defaultdict(list[type[LoweringRule]])
        for lowering in self.lowerings:
            self.opname_to_lowerings[lowering.opname].append(lowering)

    def get_rule_of_type_for_opname(self, opname: str, rule_type: RuleType):
        for rule in self.opname_to_rules[opname]:
            if rule.rule_type == rule_type:
                return rule
        return None

    def step(self):
        any_change = False
        for node in self.arith.nodes:
            # PRODUCE
            if any(x.dtype == "fqint24" for x in node.outputs):
                logger.debug(
                    f"checking for produce rule for node of type {node.opname}"
                )
                maybe_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.PRODUCE
                )
                if maybe_rule is not None:
                    maybe_rule().apply(node, self.arith, self.bank, self.subgraph_bank)
                    any_change = True

            # CONSUME
            if len(node.inputs) != 0:
                banked_inputs = {}
                missing_keys = set()
                num_banked_24_inputs = 0
                for key, value in node.inputs.items():
                    if value.dtype == "fqint24":
                        if value in self.bank:
                            banked_inputs[key] = value
                            num_banked_24_inputs += 1
                        else:
                            missing_keys.add(key)

                consume_all_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.CONSUME_ALL
                )
                consume_any_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.CONSUME_ANY
                )

                if num_banked_24_inputs > 0:
                    if (consume_all_rule is None) and (consume_any_rule is None):
                        raise RuntimeError(
                            f"No propagation rule for node {node} to consume an int24 variable."
                        )
                    if len(missing_keys) == 0 and consume_all_rule is not None:
                        consume_all_rule().apply(
                            node,
                            self.arith,
                            self.bank,
                            self.subgraph_bank,
                            banked_inputs,
                        )
                        any_change = True
                    elif consume_any_rule is not None:
                        consume_any_rule().apply(
                            node,
                            self.arith,
                            self.bank,
                            self.subgraph_bank,
                            banked_inputs,
                        )
                        any_change = True
                    elif consume_all_rule is None:
                        raise RuntimeError(
                            f"No propagation rule for node {node} to consume an int24 variable."
                        )

        # cleanup
        to_remove = set()
        for tensor in self.bank.keys():
            if len(list(successors(self.arith, tensor))) == 0:
                to_remove.add(tensor)
                if tensor in self.arith.outputs:
                    self.output_bank[tensor] = self.bank[tensor]
        for x in to_remove:
            self.bank.pop(x)

        return any_change

    def fragment_i24_params(self):
        i24_params = OrderedSet()
        for p in self.arith.parameters:
            if p.dtype == "fqint24":
                assert (
                    len(p.shape) == 1
                ), f"Found illegal multidimensional int24 parameter {p}"
                i24_params.add(p)

        for p_orig in i24_params:
            p_lo, p_hi = create_lo_hi_from_i24(p_orig)
            self.arith.add_parameter(p_lo)
            self.arith.add_parameter(p_hi)
            logger.debug(f"Replacing int24 parameter {p_orig} with {p_lo} and {p_hi}")
            self.arith.parameters.remove(p_orig)

            self.bank[p_orig] = (p_lo, p_hi)

    def fragment_i24_zeros_init(self):
        if self.init is None:
            return
        for node in self.init.nodes.copy():
            if node.opname == "zeros" and node.outputs[0].dtype == "fqint24":
                y_orig = node.outputs[0]
                y_lo, y_hi = create_lo_hi_from_i24(y_orig)
                self.bank[y_orig] = (y_lo, y_hi)

                node_lo = NodeProto(
                    name=f"{node.name}_lo",
                    optype=registry_v1["zeros"],
                    inputs={},
                    outputs=[y_lo],
                    constants=node.constants.copy(),
                )
                node_hi = NodeProto(
                    name=f"{node.name}_hi",
                    optype=registry_v1["zeros"],
                    inputs={},
                    outputs=[y_hi],
                    constants=node.constants.copy(),
                )
                self.init.add_node(node_lo)
                self.init.add_node(node_hi)
                self.init.nodes.remove(node)

                logger.debug(f"replacing {node} with {node_lo}, {node_hi} in INIT")

    def legalize_subgraph(self, node: NodeProto):
        subgraph: GraphProto = node.subgraph
        assert subgraph is not None

        sub_bank = {}

        for x in subgraph.inputs:
            if x.dtype == "fqint24":
                sub_bank[x] = create_lo_hi_from_i24(x)

        prop = VirtualI24Propagator(subgraph)
        prop.bank = sub_bank.copy()
        prop.do()

        self.subgraph_bank.update(sub_bank)
        self.subgraph_bank.update(prop.output_bank)

        logger.debug(self.subgraph_bank)

    def legalize_subgraphs(self):
        for node in self.arith.nodes:
            if node.opname in ["loop"]:
                self.legalize_subgraph(node)

    def legalize(self):
        for node in self.arith.nodes:
            for legalizer in self.opname_to_legalizers[node.opname]:
                legalizer.apply(node)

    def lower(self):
        for node in self.arith.nodes:
            lowerings = self.opname_to_lowerings[node.opname]
            if len(lowerings) == 1:
                lowerings[0].apply(self.arith, node)
            elif len(lowerings) > 1:
                raise ValueError(
                    f"{len(lowerings)} lowerings have been registered for optype {node.opname}"
                )

    def repr_graph_full(self):
        repr = []
        for node in self.arith.nodes:
            repr.append(str(node))
            repr.append(f"\t{node.constants}")
        return "\n".join(repr)

    def do(self):
        # recurse down to all subgraphs before doing anything

        logger.debug(f"Graph before: {self.repr_graph_full()}")

        self.legalize_subgraphs()

        # before: fragment any int24 parameters and zeros-init
        self.fragment_i24_params()
        self.fragment_i24_zeros_init()

        self.lower()

        if True:
            logger.debug(f"Graph after lowering {self.repr_graph_full()}")

            logger.debug("Step 0")
            any_change = self.step()

            i = 1
            while len(self.bank) != 0 and any_change:
                logger.debug(f"Step {i}, bank: {self.bank}, graph: {self.arith}")
                any_change = self.step()
                logger.debug(f"{any_change=} at step {i}")
                i += 1
                if i == 10:
                    assert False, f"{self.arith=}\n{self.init=}"

            if len(self.bank) != 0:
                msg = [f"Virtual int24 propagation failed. {self.bank=}"]
                for x in self.bank:
                    succs = list(successors(self.arith, x))
                    preds = list(predecessors(self.arith, x))

                    succ_types = set(s.opname for s in succs)
                    pred_types = set(s.opname for s in preds)
                    msg += [f"{x}: {succ_types=} {pred_types=}"]
                    for suc in succs:
                        msg += [f"\t{suc.inputs=}"]

                raise RuntimeError("\n".join(msg))

            for node in self.arith.nodes:
                if any(x.dtype == "fqint24" for x in node.outputs):
                    raise ValueError(
                        f"Found int24 intermediate from node of type {node.opname}\n{self.get_rule_of_type_for_opname(node.opname, RuleType.PRODUCE)}"
                    )

            logger.debug(f"Graph after virtualization {self.repr_graph_full()}")

            if True:
                # after: run legalizers
                self.legalize()

                logger.debug(f"Graph after final legalization {self.repr_graph_full()}")


def virtualize_high_precisions(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    init = graph.subgraphs.get("INIT", None)

    propagator = VirtualI24Propagator(arith, init=init)
    propagator.do()
