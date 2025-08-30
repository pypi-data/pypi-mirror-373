import torch
from collections import defaultdict, OrderedDict, namedtuple
import fmot

__all__ = ["fp_and_quant_activation_trace"]


def isinstanceamong(obj, *types):
    return any([isinstance(obj, typ) for typ in types])


def combine_iterators(x):
    """
    Combines all tuples/lists contained inside of x into a single list.
    Example:

        x = (1, [2,3,4], (5, 6))
        print(combine_iterators(x))
        >>> [1,2,3,4,5,6]
    """
    out = []
    _combine_iterators(x, out)
    return out


def _combine_iterators(x, out):
    """Construct a flattened list recursively"""
    if isinstance(x, (list, tuple)):
        for xx in x:
            _combine_iterators(xx, out)
    else:
        out.append(x)


def _save_inputs_and_outputs_hook(module, inputs, outputs):
    """
    A forward hook that saves a layer's inputs and outputs under the
    'act_history' attribute. CPU memory is used for storage.

    The 'act_history' object is a dict[list[list[Tensor]]]. The dictionary
    has two keys: 'inputs', 'outputs'
    Each dictionary entry is a list[list[Tensor]]. The outer list iterates
    through time-steps (if the layer is called multiple times in a sequential model),
    and may often have length 1 (in the case where the layer was only called once).

    The inner list iterates through different inputs/outputs for models that have
    multiple input/output tensors.
    """
    c_inputs = combine_iterators(inputs)
    c_outputs = combine_iterators(outputs)
    # detach tensors
    for tensorlist in [c_inputs, c_outputs]:
        for i, tensor in enumerate(tensorlist):
            if isinstance(tensor, torch.Tensor):
                tensorlist[i] = tensor.detach().cpu()
            else:
                del tensorlist[i]
    if not hasattr(module, "act_history"):
        module.act_history = defaultdict(list)
    module.act_history["inputs"].append(c_inputs)
    module.act_history["outputs"].append(c_outputs)


def collate_saved_activations(act_history):
    """
    Collates an activation history dictionary dict[list[list[Tensor]]] into
    dict[list[Tensor]]. The dictionary will have 'inputs' and 'outputs' keys.
    Each dictionary item will contain a list of tensors; one entry for each of
    the layer's inputs/outputs.
    """
    collated = {}
    for k, v in act_history.items():
        T = len(v)
        if T > 0:
            N = len(v[0])
            v_stacked = [
                torch.stack([v[t][n] for t in range(T)], dim=1) for n in range(N)
            ]
        else:
            v_stacked = []
        collated[k] = v_stacked
    return collated


def collect_saved_activations(model):
    """
    Returns a dict[dict[list[Tensor]]]
    Outer dict iterates over layers in the model
    Inner dict iterates between 'inputs' and 'outputs'
    List iterates between different inputs/outputs to the layer
    (in case of a multi-tensor input/output from a layer)
    """
    collected = OrderedDict()
    for name, module in model.named_modules():
        if hasattr(module, "act_history"):
            collected[name] = collate_saved_activations(module.act_history)
    return collected


def reset_saved_activations(model):
    for module in model.modules():
        if hasattr(module, "act_history"):
            module.act_history = defaultdict(list)


def collect_saved_activations(model):
    collected = OrderedDict()
    for name, module in model.named_modules():
        if hasattr(module, "act_history"):
            ah = module.act_history
            key = f'{name.replace(".", "_")}_<{type(module).__name__}>'
            collected[key] = {}
            for k, v in ah.items():
                T = len(v)
                if T > 0:
                    N = len(v[0])
                    v_stacked = [
                        torch.stack([v[t][n] for t in range(T)], dim=1)
                        for n in range(N)
                    ]
                else:
                    v_stacked = v
                collected[key][k] = v_stacked
    return collected


IGNORED_LAYERS = [fmot.qat.nn.ObserverBase, fmot.qat.nn.Quantizer]


def wrap_model_to_save_activations(model):
    handles = []
    for module in model.modules():
        if isinstance(module, fmot.qat.nn.AtomicModule):
            handles.append(module.register_forward_hook(_save_inputs_and_outputs_hook))
    return model, handles


def clean_model(model, handles):
    for h in handles:
        h.remove()
    for module in model.modules():
        if hasattr(module, "act_history"):
            del module.act_history
    return model


def fp_and_quant_activation_trace(model, *model_input):
    """
    Runs a model on the provided input tensor(s), saves internal activations.
    The model is run in both full-precision and quantized modes. This tool
    is useful for inspecting internal activations of the quantized model to
    find quantization bottlenecks and/or places where a sub-optimal quantization
    configuration may have been chosen.

    Returns:
        dict[dict[list[Tensor]]]: The outer dictionary is indexed by the names
            of the model's layers. The inner dictionary has the follow four keys:
            ['fp_inputs', 'fp_outputs', 'quant_inputs', 'quant_outputs']. The
            list iterates through different input/output tensors for layers that
            take multiple inputs/outputs.

        Example:

            trace = fp_and_quant_activation_trace(model, torch.randn(32, 32))
            y_fp = trace['layer0']['fp_outputs'][0]
            y_quant = trace['layers0']['quant_outputs'][0]

    """
    # Prepare model to save internal activations
    prev_training = model.training
    model = model.eval()
    model, handles = wrap_model_to_save_activations(model)

    # Get quantized model internal activations
    with torch.no_grad():
        __ = model(*model_input)
    quant_history = collect_saved_activations(model)

    # Get full-precision model internal activations
    reset_saved_activations(model)
    model = fmot.qat.control.disable_quantization(model)
    with torch.no_grad():
        __ = model(*model_input)
    fp_history = collect_saved_activations(model)

    # Restore model to its original state
    model = clean_model(model, handles)
    if prev_training:
        model = model.train()
    model = fmot.qat.control.enable_quantization(model)

    # Combine quant and fp activation traces
    combined_trace = OrderedDict()
    for key in quant_history.keys():
        combined = dict(
            fp_inputs=fp_history[key]["inputs"],
            fp_outputs=fp_history[key]["outputs"],
            quant_inputs=quant_history[key]["inputs"],
            quant_outputs=quant_history[key]["outputs"],
        )
        combined_trace[key] = combined
    return combined_trace
