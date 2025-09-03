import torch
import fmot
from torch import nn, Tensor
from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
from typing import *
import yaml
import numpy as np
from fmot.beta.heirarchical_labeling import get_hierarchical_ticks, plot_merged_labels


@dataclass
class FPvsQAT:
    """Dataclass to store full-precision and quantized tensors,
    as well as useful annotations.

    Has useful methods to compute error, dynamic-range
    utilization, etc."""

    fp: Tensor
    qat: Tensor
    layer_type: str = None
    quanta: int = None

    def rmse(self):
        return (self.fp - self.qat).pow(2).mean().sqrt().detach().cpu()

    def nrmse(self):
        num = (self.fp - self.qat).pow(2).mean()
        den = self.fp.pow(2).mean()
        return (num / den).sqrt().detach().cpu()

    def qsnr(self):
        return (
            10
            * torch.log10(
                ((self.fp).pow(2).mean() + 1e-12)
                / ((self.fp - self.qat).pow(2).mean() + 1e-12)
            )
            .detach()
            .cpu()
        )

    def std_over_dynamic(self):
        if self.quanta is not None:
            std = torch.std(self.qat)
            mv = 2 ** (15 + self.quanta)
            return (std / mv).detach().cpu()
        else:
            return None

    def max_over_dynamic(self):
        if self.quanta is not None:
            num = torch.max(torch.abs((self.qat)))
            mv = 2 ** (15 + self.quanta)
            return num / mv
        else:
            return None

    def meanabs_over_dynamic(self):
        if self.quanta is not None:
            num = torch.mean(torch.abs((self.qat)))
            den = torch.max(torch.abs(self.qat))
            return num / den
        else:
            return None

    def meanabs_over_max(self):
        if self.quanta is not None:
            num = torch.mean(torch.abs((self.qat)))
            mv = 2 ** (15 + self.quanta)
            return num / mv
        else:
            return None


def flatten_iterator(x):
    if isinstance(x, Tensor):
        return [x]
    elif isinstance(x, (list, tuple)):
        return sum((flatten_iterator(xx) for xx in x), start=[])
    else:
        raise NotImplementedError()


def _get_layer_hook(act_dict: Dict[str, Tensor], anno_dict: dict, name: str):
    """Returns a forward hook function to save activations and annotations
    from the forward pass under given name"""

    def wrapper(module, inputs, outputs):
        outputs = flatten_iterator(outputs)

        for i, x in enumerate(outputs):
            key = f"{name}_{i}"
            act_dict[key].append(x.detach().cpu())
            quanta = None
            if hasattr(x, "quanta"):
                quanta = x.quanta
                if quanta is not None:
                    quanta = quanta.detach().cpu().item()
            anno_dict[key] = {"quanta": quanta}

    return wrapper


def _wrap_model_recursive(
    model: nn.Module, init_name: str, act_dict: dict, anno_dict: dict, hooks: list
):
    """Recursively hook atomic modules and LUT modules inside the module"""
    for name, module in model.named_children():
        if isinstance(
            module,
            (
                fmot.qat.nn.AtomicModule,
                fmot.qat.nn.ILUT,
                fmot.qat.nn.TLUT,
                fmot.qat.nn.AddIdentityTLUT,
                fmot.qat.nn.MulIdentityTLUT,
                fmot.qat.nn.TILUT,
                fmot.qat.nn.FastILUT,
                fmot.nn.signal_processing.Magnitude,
            ),
        ) and not isinstance(
            module,
            (
                fmot.qat.nn.Transpose,
                fmot.qat.nn.FTranspose,
                fmot.qat.nn.Requantize,
                fmot.qat.nn.BareCat,
            ),
        ):
            hook = _get_layer_hook(act_dict, anno_dict, f"{init_name}.{name}")
            hooks.append(module.register_forward_hook(hook))
        else:
            _wrap_model_recursive(
                module,
                init_name=f"{init_name}.{name}",
                act_dict=act_dict,
                hooks=hooks,
                anno_dict=anno_dict,
            )


def _wrap_model(model: nn.Module):
    """Recursively hook atomic modules and LUT modules inside the module.

    Returns:
        act_dict: dictionary will be filled with activations from the forward pass
        anno_dict: dictionary will be filled with additional annotations (e.g. quantas)
            from forward pass
        hooks (list[removable_hook]): list of removable forward hooks
    """
    hooks = []
    act_dict = defaultdict(list)
    anno_dict = {}
    _wrap_model_recursive(model, "", act_dict, anno_dict, hooks)
    return act_dict, anno_dict, hooks


@torch.no_grad()
def _compare_fp_vs_qat(model: fmot.ConvertedModel, *args: Tensor):
    """Record internal activations in the model with and without quantization.

    Arguments:
        model (ConvertedModel): ConvertedModel (must be quantized)
        *args (tuple[Tensor]): inputs to run through the model

    Returns:
        Dict[str, FPvsQAT]: dictionary mapping each layer output to a FPvsQAT object
    """

    model.enable_quantization()
    quant_dict, anno_dict, hooks = _wrap_model(model)
    model(*args)
    for hook in hooks:
        hook.remove()

    model.disable_quantization()
    fp_dict, __, hooks = _wrap_model(model)
    model(*args)
    for hook in hooks:
        hook.remove()

    model.enable_quantization()

    compare_dict: Dict[str, FPvsQAT] = {}

    layer2type = {name: type(module).__name__ for name, module in model.named_modules()}

    for key in quant_dict:
        layer_key = key[1:].rsplit("_", 1)[0]
        compare_dict[key] = FPvsQAT(
            torch.stack(fp_dict[key], 0),
            torch.stack(quant_dict[key], 0),
            layer_type=layer2type.get(layer_key),
            quanta=anno_dict[key]["quanta"],
        )
        if layer2type.get(layer_key) is None:
            print(f"Can't find type for {layer_key}")

    return compare_dict


class QuantizationErrorAnalyzer:
    """Quantization Error Analysis Tool

    Arguments:
        model (ConvertedModel): ConvertedModel to analyze (must be quantized)
        inputs (Tensor, Tuple[Tensor]): Input to run throught the model. Can be a single tensor
            if the model accepts a single input, or a tuple of tensors if the model requires
            multiple inputs.
    """

    def __init__(
        self, model: fmot.ConvertedModel, inputs: Union[Tensor, Tuple[Tensor]]
    ):
        if isinstance(inputs, Tensor):
            inputs = (inputs,)

        self.model = model
        print("Running F.P. vs. Quant Comparison")
        self._compare_dict = _compare_fp_vs_qat(self.model, *inputs)
        print("Done!")

    def save_metric_to_yaml(self, attr: str, filename: str):
        to_save = []
        for name, comp in self._compare_dict.items():
            value = getattr(comp, attr)()
            if isinstance(value, torch.Tensor):
                value = value.detach().cpu().item()
            if isinstance(value, np.ndarray):
                value = value[0]
            value = float(value)
            to_save.append([name[len(".model.model.") :], comp.layer_type, value])

        with open(filename, "w") as f:
            yaml.dump(to_save, f)

    def _plot_metric(
        self,
        attr: str,
        label: str = None,
        with_tags=False,
        heirarchical_labels=True,
        depth=4,
        axes=None,
    ):
        if axes is None:
            if heirarchical_labels:
                fig, ax = plt.subplots(2, sharex=True)
            else:
                fig, ax = plt.subplots()
                ax = [ax]

        else:
            ax = axes

        y = [getattr(cmp, attr)() for cmp in self._compare_dict.values()]
        ax[0].plot(y, ".-", label=label)

        if axes is None:
            if heirarchical_labels:
                labelsets = get_hierarchical_ticks(
                    map(lambda x: x[len(".model.model.") :], self._compare_dict.keys()),
                    depth,
                )
                plot_merged_labels(ax[1], *labelsets)
                # ax[1].set_xticks([])
                ax[1].set_yticks([])

            if with_tags:
                raise NotImplementedError()

        for a in ax:
            a.grid(True)

        return ax

    def plot_qsnr(
        self,
        with_tags=False,
        show=False,
        heirarchical_labels=True,
        depth=4,
        fname: str = None,
    ):
        """Plot SNR between quantized and full-precision tensors vs. network depth.

        Arguments:
            with_tags (bool, optional): If True, x-axis is labeled by the operator name.
                Otherwise, x-axis is numbered by operation index. Default True.
            show (bool, optional): If True, plt.show() will be called on the figure after
                generation. Default False.
            fname (str, optional): If not None, plt.savefig() will be called, saving the
                figure as a .png file under the given filename. Default None.
        """
        ax = self._plot_metric(
            "qsnr",
            with_tags=with_tags,
            heirarchical_labels=heirarchical_labels,
            depth=depth,
        )
        ax[0].set_ylabel("qSNR [dB]")
        ax[0].set_title("qSNR vs. Layer")

        if fname is not None:
            plt.savefig(fname)
        if show:
            plt.show()

    def plot_dynamic_range_utilization(
        self,
        with_tags=False,
        show=False,
        fname: str = None,
        heirarchical_labels=True,
        depth=4,
    ):
        """Plot degree of dynamic range utilization for each of the intermediate activation tensors.

        Arguments:
            with_tags (bool, optional): If True, x-axis is labeled by the operator name.
                Otherwise, x-axis is numbered by operation index. Default True.
            show (bool, optional): If True, plt.show() will be called on the figure after
                generation. Default False.
            fname (str, optional): If not None, plt.savefig() will be called, saving the
                figure as a .png file under the given filename. Default None.
        """
        axes = self._plot_metric(
            attr="std_over_dynamic",
            label="std",
            with_tags=with_tags,
            heirarchical_labels=heirarchical_labels,
            depth=depth,
        )
        axes = self._plot_metric(
            attr="meanabs_over_dynamic", label="meanabs", axes=axes
        )
        axes = self._plot_metric(attr="max_over_dynamic", label="max", axes=axes)
        axes[0].grid(True)
        axes[0].legend()
        axes[0].set_yscale("log", base=2)
        axes[0].set_ylabel("Ratio over i16 Dynamic Range")
        axes[0].set_title("Dynamic Range Utilization vs. Network Depth")

        if fname is not None:
            plt.savefig(fname)
        if show:
            plt.show()
