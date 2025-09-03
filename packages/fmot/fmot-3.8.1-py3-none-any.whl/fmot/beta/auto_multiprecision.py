import torch
import fmot
import numpy as np
from itertools import cycle
import tqdm
from collections import defaultdict
from fmot import fqir

from ..utils.quantizer_manager import get_quantizers, group_quantizers

"""
FQIR Rough Energy Model -- maybe put this inside of fqir instead of fmot
"""


def dtype_to_bytes(dtype):
    if dtype == "fqint4":
        return 0.5
    elif dtype == "fqint8":
        return 1
    elif dtype == "fqint16":
        return 2
    else:
        raise ValueError(f"Unrecognized datatype {dtype}")


def tproto_to_mem(tproto: fqir.TensorProto):
    return tproto.nbytes(nonzero_only=True)


def matmul_energy(node):
    avg_sparsity = 0
    x = node.inputs["x"]
    if hasattr(x, "avg_sparsity"):
        if x.avg_sparsity is not None:
            avg_sparsity = x.avg_sparsity

    x_density = 1 - avg_sparsity
    tot_mat_mem = tproto_to_mem(node.inputs["y"])
    mat_ops = tot_mat_mem * x_density
    if x.dtype == "fqint16" and node.inputs["y"].dtype == "fqint4":
        mat_ops *= 2  # because we would have to cast matrix to int8

    other_tensors = [node.inputs["x"], node.outputs[0]]
    if "bias" in node.inputs:
        other_tensors.append(node.inputs["bias"])
    other_ops = np.sum([tproto_to_mem(x) for x in other_tensors])
    return mat_ops + other_ops


def standard_energy(node):
    inputs = list(node.inputs.values())
    outputs = node.outputs

    return np.sum([tproto_to_mem(x) for x in inputs + outputs])


standard_optypes = [
    "vvadd",
    "viadd",
    "vvsub",
    "vneg",
    "vvmul",
    "vimul",
    "relu",
    "lut",
    "chunk",
    "cat",
    "stack",
    "sum",
    "copy",
    "shift",
    "gt0",
]
mm_optypes = ["matmul", "addmm"]


def rough_fqir_energy(graph):
    G = graph.subgraphs["ARITH"]
    tot_energy = 0
    for node in G.nodes:
        opname = node.optype.name
        if opname in standard_optypes:
            tot_energy += standard_energy(node)
        elif opname in mm_optypes:
            tot_energy += matmul_energy(node)
    return tot_energy


def fqir_energy(graph):
    """
    Returns an energy estimate (per input sample) for a given
    FQIR graph. If the graph has a :attr:`.energy()` method, will
    call this (versions of FQIR >= 0.5.0). Otherwise, will return
    rough_fqir_energy.

    Args:
        graph (fqir.GraphProto): traced computational graph
    Returns:
        - energy_estimate (float)
        - joules (bool): whether this returned estimate is in joules,
            or unitless
    """
    return rough_fqir_energy(graph), False


"""
Progress Bar
"""


def get_tqdm():
    return tqdm.tqdm


"""
Detection of LUT-variants
"""


def isinstance_among(x, *types):
    if len(types) == 0:
        raise ValueError("Need to supply at least one type")
    return any([isinstance(x, typ) for typ in types])


LUT_VARIANT_TYPES = [fmot.qat.nn.ILUT]


def get_lut_variants(module):
    """
    Returns:
        Dictionary, mapping lut layers to their (name, parent)
    """
    lut_dict = {}
    for name, mod in module.named_children():
        if isinstance_among(mod, *LUT_VARIANT_TYPES):
            lut_dict[mod] = (name, module)
        else:
            lut_dict.update(get_lut_variants(mod))
    return lut_dict


"""
OPTIMIZATION
"""

BWS = [fmot.qat.double, fmot.qat.standard]


def optimize_quantizer_config(quantizer, x, target, eval_fn, eta):
    """Find the optimal configuration for a single quantizer layer inside of model

    All other quantizers left alone. Optimal config is the one that minimizes
    cost, as defined by a given eval_fn.

    Args:
        quanitzer (fmot.qat.nn.Quantizer): Quantizer layer to be optimized
            at this step
        x (torch.Tensor or Tuple[Torch.Tensor]): Input to model
        target (torch.Tensor): target for loss-fn evaluation
        eval_fn (callable): Function used to score a given qconfig. Takes
            as inputs: (x, target, eta)
        eta (float): relative weighting between energy & objective function
    """
    best_score = float("inf")
    best_bw = None
    best_energy = None
    best_loss = None
    for bw in BWS:
        quantizer.update_bitwidth(bw)
        score, loss, energy = eval_fn(x, target, eta)
        if score < best_score:
            best_score = score
            best_bw = bw
            best_energy = energy
            best_loss = loss
    if best_bw is not None:
        quantizer.update_bitwidth(best_bw)
    if best_energy is None:
        best_energy = 0
    if best_loss is None:
        best_loss = 0
    return best_energy, best_loss


def optimize_lut_variant_config(qgroup, lut_dict, x, target, eval_fn, eta):
    lut = qgroup.module
    if lut is None or lut not in lut_dict:
        return optimize_quantizer_config(qgroup, x, target, eval_fn, eta)

    # otherwise:
    lut.q_group.update_bitwidth(fmot.qat.double)
    name, parent = lut_dict[lut]

    def set_config(config):
        bw, interpolate = config
        if bw == fmot.qat.double and interpolate:
            setattr(parent, name, lut)
        else:
            new_lut = lut.to_simple_lut()
            setattr(parent, name, new_lut)
            new_lut.q_group.update_bitwidth(bw)

    CANDIDATES = [
        (fmot.qat.double, True),
        (fmot.qat.double, False),
        (fmot.qat.standard, False),
    ]
    best_score = float("inf")
    best_config = None
    best_energy = None
    best_loss = None
    for config in CANDIDATES:
        set_config(config)
        score, loss, energy = eval_fn(x, target, eta)
        if score < best_score:
            best_score = score
            best_config = config
            best_energy = energy
            best_loss = loss
    set_config(best_config)
    return best_energy, best_loss


def is_lut_variant(quant):
    if isinstance(quant, fmot.qat.nn.Quantizer):
        return False
    else:
        return isinstance_among(quant.module, *LUT_VARIANT_TYPES)


def tuple_to(x, device, keep_type=True):
    if isinstance(x, tuple):
        return tuple([xx.to(device) for xx in x])
    else:
        if keep_type:
            return x.to(device)
        else:
            return (x.to(device),)


def optimize_mixed_precision(
    converter,
    model,
    objective,
    eta,
    inputs,
    targets,
    niter=1,
    ramp_eta=True,
    topological_sort=True,
    use_groups=True,
    loss_type="polynomial",
    device="cpu",
    num_inputs_per_step=None,
):
    """
    Optimize Mixed Precision Configuration

    Args:
        converter (ConvertedModel): Model needs to be quantized first
        objective (function): Function with signature
            `objective(output, target) -> loss`.
        eta (float): hyperparameter, between 0 and 1, selecting relative importance
            energy minimization vs loss minimization.
    """
    X0 = inputs[0]
    if num_inputs_per_step is not None:
        inputs, targets = iter(cycle(inputs)), iter(cycle(targets))

    # get energy and loss for standard and double precision
    with torch.no_grad():
        if num_inputs_per_step is None:
            x, targ = inputs, targets
        else:
            x = [next(inputs) for __ in range(num_inputs_per_step)]
            targ = [next(targets) for __ in range(num_inputs_per_step)]
        energy = defaultdict(float)
        mean_loss = defaultdict(float)
        for precision in ["double", "standard"]:
            converter.modify_precision(precision)
            energy[precision], is_joules = fqir_energy(converter.trace())
            for x_i, targ_i in zip(x, targ):
                targ_i = tuple_to(targ_i, device)
                x_i = tuple_to(x_i, device, keep_type=False)
                mean_loss[precision] += objective(model(*x_i), targ_i) / len(x)
        converter.modify_precision("double")
        E_dbl, E_std = energy["double"], energy["standard"]
        L_dbl, L_std = mean_loss["double"], mean_loss["standard"]

    # normalize the objective function based on the mean double/standard loss
    @torch.no_grad()
    def normalized_objective(x, target):
        x = tuple_to(x, device, keep_type=False)
        target = tuple_to(target, device)
        y = model(*x)
        loss = objective(y, target)
        assert loss.numel() == 1

        if loss_type == "polynomial":
            l_normed = loss / (L_std - L_dbl).abs()
        elif loss_type == "logarithmic":
            l_normed = torch.exp(loss)
            l_normed /= (torch.exp(L_std) - torch.exp(L_dbl)).abs()
        elif loss_type == "exponential":
            l_normed = torch.log(loss / L_dbl) / (torch.log(L_std / L_dbl)).abs()
        else:
            raise ValueError(f"Loss type {loss_type} not understood")
        return loss, l_normed

    # define the evaluation function
    @torch.no_grad()
    def evaluate(inputs, targets, eta):
        mean_loss = 0.0
        mean_loss_normalized = 0.0
        for x, target in zip(inputs, targets):
            loss, l_normed = normalized_objective(x, target)
            mean_loss += loss
            mean_loss_normalized += l_normed
        mean_loss /= len(inputs)
        mean_loss_normalized /= len(inputs)
        energy, is_joules = fqir_energy(converter.trace())
        e_ratio = energy / E_dbl
        cost = (1 - eta) * mean_loss_normalized + eta * e_ratio
        if is_joules:
            return cost, mean_loss, energy
        else:
            return cost, mean_loss, e_ratio

    # Iterate niter times; display nice progress bar
    for n in range(niter):
        if ramp_eta:
            eta_eff = eta * (n + 1) / niter
        else:
            eta_eff = eta

        # refresh quantizer and lut sets at each iteration
        quantizers = get_quantizers(model, *tuple_to(X0, device, keep_type=False))
        if use_groups:
            quantizers = group_quantizers(quantizers)
        lut_dict = get_lut_variants(model)

        if not topological_sort:
            quantizers = np.random.permutation(quantizers)

        # For each quantizer, choose a best quantization config
        iterator = get_tqdm()(quantizers, total=len(quantizers))
        for quant in iterator:
            if num_inputs_per_step is None:
                x, targ = inputs, targets
            else:
                x = [next(inputs) for __ in range(num_inputs_per_step)]
                targ = [next(targets) for __ in range(num_inputs_per_step)]
            if is_lut_variant(quant):
                energy, loss = optimize_lut_variant_config(
                    quant, lut_dict, x, targ, evaluate, eta_eff
                )
            else:
                energy, loss = optimize_quantizer_config(
                    quant, x, targ, evaluate, eta_eff
                )
            if is_joules:
                iterator.set_postfix({"Energy": f"{energy:.3E} J", "Loss": loss})
            else:
                iterator.set_postfix({"Compression": energy, "Loss": loss})
    return model, energy, loss
