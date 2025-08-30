import fmot
from torch import nn
from .. import torchscript_utils as utils
import math
import logging

logger = logging.getLogger(__name__)


class PatchRule:
    def __init__(self, rule, options):
        self._from_node = rule
        self.options = options


def add_sub_rule(vv=fmot.nn.VVAdd, vi=fmot.nn.VIAdd):
    def rule(node, module):
        inputs = list(node.inputs())
        if len(inputs) < 3:
            raise ValueError(
                f"module {module} only had {len(inputs)} inputs in node {node}, < 3"
            )
        if not utils.get_value(inputs[2], module) == 1:
            raise ValueError(
                f"Unexpected value: {utils.get_value(inputs[2], module)} != 1 in module {module}"
            )
        assert utils.istensor(inputs[0])
        if utils.istensor(inputs[1]):
            return vv()
        else:
            imm = utils.get_value(inputs[1], module)
            return vi(imm)

    return rule


def mul_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[0])
    if utils.istensor(inputs[1]):
        return fmot.nn.VVMul()
    else:
        imm = utils.get_value(inputs[1], module)
        return fmot.nn.VIMul(imm)


def chunk_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[0])
    chunks = utils.get_value(inputs[1], module)
    dim = utils.get_value(inputs[2], module)
    return fmot.nn.Chunk(chunks, dim)


def split_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[0])
    split_sizes = utils.get_list(inputs[1], module=module)
    if any([xx is None for xx in split_sizes]):
        raise ValueError(f"Found split_size of None in {node=}, {module.sizes=}")
    dim = utils.get_value(inputs[2], module)
    return fmot.nn.Split(split_sizes, dim)


def cat_rule(node, module):
    inputs = list(node.inputs())
    dim = utils.get_value(inputs[1], module)
    return fmot.nn.Cat(dim)


def stack_rule(node, module):
    inputs = list(node.inputs())
    dim = utils.get_value(inputs[1], module)
    return fmot.nn.Stack(dim)


def reshape_rule(node, module):
    inputs = list(node.inputs())
    shape = utils.get_list(inputs[1])
    return fmot.nn.Reshape(shape)


def div_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[0])
    if utils.istensor(inputs[1]):
        return fmot.nn.Div()
    else:
        imm = utils.get_value(inputs[1], module)
        return fmot.nn.VIMul(1.0 / imm)


def sum_mean_rule(opname="torch.sum", map_to=fmot.nn.Sum):
    def rule(node, module):
        inputs = list(node.inputs())
        assert utils.istensor(inputs[0])
        if len(inputs) == 4:
            dim = utils.get_list(inputs[1])
            keepdim = utils.get_value(inputs[2], module)
        else:
            raise RuntimeError(
                f"Cannot compile {opname} without a dim argument\n{node.sourceRange()}"
            )
        return map_to(dim=dim, keepdim=keepdim)

    return rule


def std_var_rule(opname="torch.std", map_to=fmot.nn.Std):
    def rule(node, module):
        inputs = list(node.inputs())
        assert utils.istensor(inputs[0])
        if len(inputs) == 4:
            dim = utils.get_list(inputs[1])
            unbiased = utils.get_value(inputs[2], module)
            keepdim = utils.get_value(inputs[3], module)
        else:
            raise RuntimeError(
                f"Cannot compile {opname} without a dim argument\n{node.sourceRange()}"
            )
        return map_to(dim=dim, keepdim=keepdim, unbiased=unbiased)

    return rule


def linear_rule(node, module):
    inputs = list(node.inputs())
    if utils.istensor(inputs[-1]):
        logger.debug("linear with bias")
        return fmot.nn.F_Linear()
    else:
        logger.debug("no bias linear")
        return fmot.nn.F_Linear_nb()


def layernorm_rule(node, module):
    inputs = list(node.inputs())
    normalized_shape = utils.get_list(inputs[2])
    eps = utils.get_value(inputs[5], module)
    assert utils.istensor(inputs[1])
    weight = utils.istensor(inputs[3])
    bias = utils.istensor(inputs[4])
    if not all([weight, bias]):
        issues = []
        if not weight:
            issues.append("weight = None")
        if not bias:
            issues.append("bias = None")
        raise RuntimeError(
            f'Cannot compile LayerNorm with {", ".join(issues)}\n{node.sourceRange()}'
        )
    return fmot.nn.F_LayerNorm(normalized_shape=normalized_shape, eps=eps)


def pow_rule(node, module):
    inputs = list(node.inputs())
    power = utils.get_value(inputs[1], module)
    if math.floor(power) == power:
        if power > 1:
            return fmot.nn.PowDecompPosInt(power)
        elif power == 1:
            return fmot.nn.Identity()
        elif power == 0:
            return fmot.nn.OnesLike()
        elif power == -1:
            return fmot.nn.Reciprocal()
        else:
            return fmot.nn.PowDecompNegInt(power)
    else:
        return fmot.nn.PowFrac(power)


def softmax_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[1])
    dim = utils.get_value(inputs[2], module)
    if dim is None:
        raise RuntimeError(
            f"Cannot compile softmax without a dim\n{node.sourcerange()}"
        )
    return fmot.nn.F_Softmax(dim)


def clamp_rule(node, module):
    inputs = list(node.inputs())
    assert utils.istensor(inputs[0])
    a = utils.get_value(inputs[1], module)
    b = utils.get_value(inputs[2], module)
    if a is not None:
        if b is not None:
            if b > a:
                return fmot.nn.ClampAB(a, b)
            else:
                return fmot.nn.ConstantLike(b)
        else:
            return fmot.nn.ClampA(a)
    else:
        if b is not None:
            return fmot.nn.ClampB(b)
        else:
            return fmot.nn.Identity()


def hardtanh_rule(node, module):
    inputs = list(node.inputs())
    min_val = utils.get_value(inputs[2], module)
    max_val = utils.get_value(inputs[3], module)
    return fmot.nn.HardTanh(min_val, max_val)


def leakyrelu_rule(node, module):
    inputs = list(node.inputs())
    negative_slope = utils.get_value(inputs[2], module)
    return fmot.nn.LeakyReLU(negative_slope)


def dropout_rule(node, module):
    inputs = list(node.inputs())
    p = utils.get_value(inputs[2], module)
    training = utils.get_value(inputs[3], module)
    inplace = utils.get_value(inputs[4], module)
    return fmot.nn.Dropout(p, training, inplace)


def transpose_rule(node, module):
    inputs = list(node.inputs())
    dim0 = utils.get_value(inputs[1], module)
    dim1 = utils.get_value(inputs[2], module)
    return fmot.nn.FTranspose(dim0, dim1)


def permute_rule(node, module):
    inputs = list(node.inputs())
    dims = [utils.get_list(inputs[i]) for i in len(inputs[0].shape)]
    return fmot.nn.Permute(dims)


def squeeze_rule(node, module):
    inputs = list(node.inputs())
    dim = utils.get_value(inputs[1], module)
    return fmot.nn.Squeeze(dim)


def fmot_tag_rule(node, module):
    inputs = list(node.inputs())
    varname = utils.get_value(inputs[2], module)
    assert varname is not None

    return fmot.nn.TagVarname(varname)


DEFAULT_PATCHINGS = {
    ########################################################################
    # >     ATEN FUNCTIONS
    "aten::relu": nn.ReLU,
    "aten::add": PatchRule(
        add_sub_rule(vv=fmot.nn.VVAdd, vi=fmot.nn.VIAdd), [fmot.nn.VVAdd, fmot.nn.VIAdd]
    ),
    "aten::add_": PatchRule(
        add_sub_rule(vv=fmot.nn.VVAdd, vi=fmot.nn.VIAdd), [fmot.nn.VVAdd, fmot.nn.VIAdd]
    ),
    "aten::sub": PatchRule(
        add_sub_rule(vv=fmot.nn.VVSub, vi=fmot.nn.VISub), [fmot.nn.VVSub, fmot.nn.VISub]
    ),
    "aten::neg": fmot.nn.Neg,
    "aten::mul": PatchRule(mul_rule, [fmot.nn.VVMul, fmot.nn.VIMul]),
    "aten::sigmoid": nn.Sigmoid,
    "aten::tanh": nn.Tanh,
    "aten::exp": fmot.nn.Exp,
    "aten::log": fmot.nn.Log,
    "aten::log1p": fmot.nn.Log1p,
    "aten::log10": fmot.nn.Log10,
    "aten::log2": fmot.nn.Log2,
    "aten::reciprocal": fmot.nn.Reciprocal,
    "aten::matmul": fmot.nn.Matmul,
    "aten::mm": fmot.nn.Matmul,
    "aten::abs": fmot.nn.Abs,
    "aten::sqrt": fmot.nn.Sqrt,
    "aten::rsqrt": fmot.nn.RSqrt,
    "aten::chunk": PatchRule(chunk_rule, [fmot.nn.Chunk]),
    "aten::split": PatchRule(split_rule, [fmot.nn.Split]),
    # "aten::prelu": fmot.nn.PReLU,
    "aten::clamp": PatchRule(
        clamp_rule,
        [
            fmot.nn.ClampAB,
            fmot.nn.ClampA,
            fmot.nn.ClampB,
            fmot.nn.Identity,
            fmot.nn.ConstantLike,
        ],
    ),
    "aten::cat": PatchRule(cat_rule, [fmot.nn.Cat]),
    "aten::stack": PatchRule(stack_rule, [fmot.nn.Stack]),
    "aten::pow": PatchRule(
        pow_rule,
        [
            fmot.nn.PowDecompPosInt,
            fmot.nn.PowDecompNegInt,
            fmot.nn.OnesLike,
            fmot.nn.PowFrac,
            fmot.nn.Identity,
            fmot.nn.Reciprocal,
        ],
    ),
    "aten::t": fmot.nn.Transpose,
    # "aten::reshape": PatchRule(reshape_rule, [fmot.nn.Reshape]),
    "aten::numpy_T": fmot.nn.Transpose,
    "aten::ones_like": fmot.nn.OnesLike,
    "aten::div": PatchRule(div_rule, [fmot.nn.Div, fmot.nn.VIMul]),
    "aten::sum": PatchRule(sum_mean_rule("torch.sum", fmot.nn.Sum), [fmot.nn.Sum]),
    "aten::mean": PatchRule(sum_mean_rule("torch.mean", fmot.nn.Mean), [fmot.nn.Mean]),
    "aten::std": PatchRule(std_var_rule("torch.std", fmot.nn.Std), [fmot.nn.Std]),
    "aten::var": PatchRule(std_var_rule("torch.var", fmot.nn.Var), [fmot.nn.Var]),
    "aten::var_mean": PatchRule(
        std_var_rule("torch.var_mean", fmot.nn.VarMean), [fmot.nn.VarMean]
    ),
    "aten::std_mean": PatchRule(
        std_var_rule("torch.std_mean", fmot.nn.StdMean), [fmot.nn.StdMean]
    ),
    "aten::transpose": PatchRule(transpose_rule, [fmot.nn.FTranspose]),
    "aten::permute": PatchRule(permute_rule, [fmot.nn.Permute]),
    "aten::squeeze": PatchRule(squeeze_rule, [fmot.nn.Squeeze]),
    "aten::linear": PatchRule(linear_rule, [fmot.nn.F_Linear, fmot.nn.F_Linear_nb]),
    ########################################################################
    # >     torch.nn.functional
    "F.relu": nn.ReLU,
    "F.sigmoid": nn.Sigmoid,
    "F.tanh": nn.Tanh,
    "F.linear": PatchRule(linear_rule, [fmot.nn.F_Linear, fmot.nn.F_Linear_nb]),
    "F.layer_norm": PatchRule(layernorm_rule, [fmot.nn.F_LayerNorm]),
    "F.softmax": PatchRule(softmax_rule, [fmot.nn.F_Softmax]),
    "F.hardsigmoid": fmot.nn.HardSigmoid,
    "F.hardswish": fmot.nn.Hardswish,
    "F.hardtanh": PatchRule(hardtanh_rule, [fmot.nn.HardTanh]),
    "F.leaky_relu": PatchRule(leakyrelu_rule, [fmot.nn.LeakyReLU]),
    "F.dropout": PatchRule(dropout_rule, [fmot.nn.Dropout]),
    ##########################################################################
    # >      fmot.functional
    "fmot.functional.tag": PatchRule(fmot_tag_rule, [fmot.nn.TagVarname]),
}
