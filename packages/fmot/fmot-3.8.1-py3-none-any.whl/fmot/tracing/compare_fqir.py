import torch
from torch import nn
import fmot
import numpy as np
from typing import *

### For debugging purposes, we create a dictionary
### that attributes each FQIR tensor to the corresponding
### pytorch module, so we can run the two side-by-side and
### locate the source of any errors
# Dict: {fqir_varname: (Module, output_index)}


def flatten_outputs(outputs) -> List[torch.Tensor]:
    if isinstance(outputs, (tuple, list)):
        return outputs
    elif isinstance(outputs, torch.Tensor):
        return [outputs]
    elif outputs is None:
        return []
    else:
        raise ValueError(f"Unexpected output type {type(outputs)}")


def add_hook(
    module: nn.Module,
    output_idx: int,
    fqir_name: str,
    state_dump: dict,
    src_types: dict,
):
    def hook_fn(module, input, outputs):
        outputs = flatten_outputs(outputs)
        out = outputs[output_idx]
        y = out.detach().cpu().numpy()
        if hasattr(out, "quanta"):
            y = y / 2 ** (torch.as_tensor(out.quanta).cpu().numpy())
            y = y.astype(int)
        state_dump[fqir_name] = y
        src_types[fqir_name] = type(module)

    return module.register_forward_hook(hook_fn)


def get_modules_below_sequencer(model: nn.Module, below: set):
    if isinstance(model, fmot.nn.Sequencer):
        below.add(model)
        for module in model.modules():
            below.add(module)
    else:
        for module in model.children():
            get_modules_below_sequencer(module, below)


@torch.no_grad()
def compare_to_fqir(
    cmodel: fmot.ConvertedModel, graph: fmot.fqir.GraphProto, inputs: List[torch.Tensor]
):
    if not hasattr(cmodel, "tsrc_dict"):
        raise RuntimeError(
            "No tsrc_dict to source FQIR tensors to their qat counterparts"
        )
    tsrc_dict = cmodel.tsrc_dict

    skip = set()
    # get_modules_below_sequencer(cmodel, skip)

    handles = []
    fmot_state = {}
    src_types = {}
    for fqir_name, (module, idx) in tsrc_dict.items():
        if module not in skip:
            handles.append(add_hook(module, idx, fqir_name, fmot_state, src_types))

    cmodel(*inputs)

    np_inputs = [x.cpu().numpy()[0] for x in inputs]
    __, fqir_state = graph.run(*np_inputs, return_objs=True)

    for handle in handles:
        handle.remove()

    return fmot_state, fqir_state, src_types


def run_fqir_autocompare(
    cmodel: fmot.ConvertedModel, graph: fmot.fqir.GraphProto, inputs: List[torch.Tensor]
):
    fmot_state, fqir_state, src_types = compare_to_fqir(cmodel, graph, inputs)
    keys = set(fmot_state.keys())
    keys.intersection_update(set(fqir_state.keys()))
    keys = list(sorted(keys))

    annotated_graph = []

    for node in graph.subgraphs["ARITH"].nodes:
        annotated_graph += [str(node)]
        for x in node.outputs:
            if x.name in keys:
                k = x.name
                x_fqir = fqir_state[k].flatten()
                x_fmot = fmot_state[k]
                if x_fmot.ndim == 3:
                    x_fmot = x_fmot[0, -1].flatten()
                elif x_fmot.ndim == 2:
                    x_fmot = x_fmot[0].flatten()
                else:
                    x_fmot = x_fmot.flatten()
                if x_fqir.shape == x_fmot.shape:
                    error = np.sqrt(np.mean((x_fqir - x_fmot) ** 2))
                    # qsnr = 10 * np.log10(np.mean(x_fmot**2 + 1e-6) / (error + 1e-6))
                    annotated_graph += [f"  error {k}: {error:3E}"]
                else:
                    annotated_graph += [
                        f"  shape mismatch... {x_fqir.shape=} {x_fmot.shape=}"
                    ]
    return "\n".join(annotated_graph)
