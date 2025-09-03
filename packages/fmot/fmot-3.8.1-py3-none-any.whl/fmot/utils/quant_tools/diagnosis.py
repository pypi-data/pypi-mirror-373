from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import pandas as pd
from typing import List, Set, Union
from torch import nn, Tensor
from ..rich_attr import rgetattr

from ... import ConvertedModel


def get_quant_diagnosis(
    model: nn.Module,
    cmodel: ConvertedModel,
    sample_input: Union[Tensor, List[Tensor]],
    to_register: Set[str] = None,
    kind: str = "output",
    submodule: str = None,
    plot: bool = True,
    dump_dir: str = None,
    how: str = "log",
):
    """Prints a diagnosis for all sub-layers of the model,
        comparing the activations for the torch model and for the ConvertedModel, for a given sample_input.
        If the model does not have sub-layers, it will not print anything.

    Args:
        model (torch.nn.Module): a PyTorch Model
        cmodel (fmot.ConvertedModel): its converted/quantized equivalent
        sample_input (torch.Tensor or List[torch.Tensor]): sample input on which the comparison is carried out.
            If the model ingests multiple inputs, it can be an list of input tensors.
        to_register (Set[str]): if None, the comparison will be carried out on all layers.
            If a set of strings is used, the comparison will only be carried out on the
            layer with these names.
        kind (str): 'output' or 'input', so that the comparison will be carried out on outputs
            or inputs of the layers respectively.
        submodule (str): The pathname of a submodule (from the top-level model) that we want to perform the quant.
            analysis on. If None, the analysis is done on the top-level model. Example: "model.layer_0.rnn"
        plot (bool): default True, determines whether a plot will be generated for each layer.
        dump_dir (str): default None. If not None, will dump the png of the debug graphs in the dump directory.
        how (str): default 'log'. Can be 'log' or 'linear'. Defines the kind of scale that is used for color-mapping.
    """
    acts = get_activations(
        model, sample_input, to_register, kind=kind, submodule=submodule
    )
    qacts = get_activations(
        cmodel,
        sample_input,
        to_register=set(acts.keys()),
        kind=kind,
        submodule=submodule,
    )
    if submodule is not None:
        plot_acts(
            rgetattr(model, submodule),
            acts,
            qacts,
            kind=kind,
            how=how,
            plot=plot,
            dump_dir=dump_dir,
        )
    else:
        plot_acts(model, acts, qacts, kind=kind, how=how, plot=plot, dump_dir=dump_dir)


def act_hook_fn(name: str, activations: dict, kind="output"):
    if kind == "output":

        def reg_act(model, input, output):
            if type(output) in {tuple, list}:
                activations[name] = output[0].detach()
            else:
                activations[name] = output.detach()

    elif kind == "input":

        def reg_act(model, input, output):
            if type(input) in {tuple, list}:
                activations[name] = input[0].detach()
            else:
                activations[name] = input.detach()

    else:
        raise Exception("Unknown kind.")

    return reg_act


def register_act_hooks(
    net,
    activations: OrderedDict,
    handles: list,
    to_register=None,
    kind="output",
    top_level_name="",
):
    for name, layer in net._modules.items():
        if isinstance(layer, nn.Sequential) or isinstance(layer, nn.ModuleList):
            register_act_hooks(
                layer,
                activations,
                handles,
                to_register,
                kind=kind,
                top_level_name=name + ".",
            )
        else:
            activation_name = top_level_name + name
            hook_fn = act_hook_fn(activation_name, activations, kind=kind)

            if to_register is not None:
                if activation_name in to_register:
                    hdl = layer.register_forward_hook(hook_fn)
                    handles.append(hdl)
            else:
                hdl = layer.register_forward_hook(hook_fn)
                handles.append(hdl)


def get_activations(
    model, sample_input, to_register=None, kind="output", submodule=None
):
    """

    Args:
        model:
        sample_input:
        to_register (set(str)): if None, the comparison will be carried out on all layers.
            If a set of strings is used, the comparison will only be carried out on the
            layer with these names.
        kind:

    Returns:

    """
    activations = OrderedDict()
    handles = []
    if isinstance(model, ConvertedModel):
        if submodule is not None:
            module = rgetattr(model.model.model, submodule)
        else:
            module = model.model.model
        register_act_hooks(module, activations, handles, to_register, kind=kind)
    else:
        if submodule is not None:
            module = rgetattr(model, submodule)
        else:
            module = model
        register_act_hooks(module, activations, handles, to_register, kind=kind)
    if isinstance(sample_input, Tensor):
        model(sample_input)
    else:
        model(*sample_input)
    for handle in handles:
        handle.remove()

    # TODO: need to handle substitutions

    return activations


def plot_acts(
    net,
    acts: OrderedDict,
    qacts: dict,
    kind="output",
    how="log",
    plot=True,
    dump_dir=None,
    top_level_name="",
):
    for name, layer in net._modules.items():
        full_name = top_level_name + name
        if isinstance(layer, nn.Sequential) or isinstance(layer, nn.ModuleList):
            plot_acts(
                layer, acts, qacts, kind, how, plot, dump_dir, top_level_name=name + "."
            )
        else:
            if full_name in acts.keys():
                x = acts[full_name].reshape(1, -1).squeeze().numpy()
                y = qacts[full_name].reshape(1, -1).squeeze().numpy()
                df = pd.DataFrame(data=np.stack([x, y], axis=-1), columns=["x", "y"])

                fig = plt.figure(figsize=(5.5, 5.5))

                plt.hist2d(df["x"], df["y"], bins=100, cmap="viridis", norm=how)
                cbar = plt.colorbar()
                cbar.set_label("# of neurons", rotation=270)
                plt.xlabel("FP Model Activations")
                plt.ylabel("QModel Activations")
                plt.title(f"{name}: {kind}")
                if dump_dir is not None:
                    plt.savefig(dump_dir + f"/{name}_{kind}.png")
                if plot:
                    plt.show()
