import torch
from typing import List
from ..utils.rich_attr import rgetattr
from .pruning import pencil_pruning
from .pruning_schedulers import QuadrantSinePruningSchedule


def prune_model_parameters(
    model,
    amount,
    pruning_function=pencil_pruning,
    min_numel=2056,
    pencil_size=4,
    skip_prune_layers: List[str] = [],
):
    r"""Apply a pruning function to apply to all of the model's parameters
         that have at least two dimensions (biases are discarded), that
         have more elements than a certain threshold, and that supposed to be trained
         (have `requires_grad` attribute set to True). The parameters following
         these criteria will be pruned by the amount argument.

    Args:
        model: PyTorch / ConvertedModel to prune
        amount: percentage of the parameters that will be pruned
        pruning_function: the pruning method to appply to the model
            Default: fmot.pruning.pencil_pruning: pencil-structured L1 pruning
        min_numel (int): minimum number of elements that a parameter
            should contain in order to be pruned
        pencil_size (int, optional): Pencil size to use when using pencil pruner.
            Default 4.
        skip_prune_layers (List[str]) : If specified, skips pruning a layer if the
                    name of the layer matches with any of the specified skip_prune_layers.
                    An example of the same

                    eg. layer_name: model.model.backbone.conformer.linear.weight
                        skip_prune_layer = ['model.model.backbone.conformer'] ...
                        In the above case, the `layer_name` will not be pruned

    Returns:

    """
    assert (amount >= 0) and (amount <= 1.0)

    if amount != 0.0:
        for param_name, param in list(model.named_parameters()):
            if any(param_name.startswith(f"{layer}") for layer in skip_prune_layers):
                pass
            elif not param.requires_grad:
                pass
            else:
                if param.dim() >= 2 and param.numel() > min_numel:
                    # If the param name is not directly related to top level
                    # module, we have to get the string to link to it
                    if param_name.find(".") != -1:
                        parent, param_name = param_name.rsplit(".", 1)
                        if param_name.find("_orig") != -1:
                            param_name = param_name.rsplit("_orig")[0]
                        layer = rgetattr(model, parent)
                    else:
                        layer = model
                    pruning_function(layer, param_name, amount, pencil_size=pencil_size)


def remove_pruning(model):
    r"""Remove the pruning reparametrization from all the
         modules of a model.

    Args:
        model: a PyTorch model or ConvertedModel

    Returns:

    """
    # for name, param in model.named_parameters():
    #     if name.find('_orig') != -1:
    #         path_name, param_name = name.rsplit('.', 1)
    #         torch.nn.utils.prune.remove(rgetattr(model, path_name), param_name[:-5])
    param_names = []
    for name, param in model.named_parameters():
        param_names.append(name)
    for name in param_names:
        if name.find("_orig") != -1:
            path_name, param_name = name.rsplit(".", 1)
            torch.nn.utils.prune.remove(rgetattr(model, path_name), param_name[:-5])

    return


def get_prune_amount(param):
    r"""

    Args:
        param (torch.nn.Parameter): a PyTorch parameter

    Returns:
        prune_amount (float): the percentage of zero elements
            in the parameter

    """
    nb_param = 1.0
    for dim in param.shape:
        nb_param *= dim

    prune_amount = torch.sum(param == 0) / nb_param

    return prune_amount


class _Pruner:
    r"""Base class to inherit from for Pruners.

    Attributes:
        prune_target (float): the final amount of pruning that will be applied.
            once the pruning scheduler has ramped up to its maximum.
        ramp_time (int): the number of ramp increments before the pruning amount reaches its
            final value.
        step_size (int): number of times we need to call the `step` method
            before ramping up the pruning schedule.
        prune_scheduler (fmot.AbstractPruningSchedule): a pruning scheduler in charge of
            managing how the pruning should ramp up.
        ramp_idx (int): the index in the ramping process.
        step_count (int): the step index. It's the number of time we have called `step`
            so far.
        prune_amount (float): current pruning amount that is to be applied
            according to the pruning schedule
        prune_start (float): initial pruning amount that is applied on the first step
            of the pruning schedule
    """

    def __init__(
        self,
        prune_target,
        ramp_time,
        step_size,
        prune_scheduler,
        ramp_idx=0,
        prune_start=0.0,
    ):
        self.prune_target = prune_target
        self.ramp_time = ramp_time
        self.step_size = step_size
        self.prune_amount = prune_start
        self.prune_start = prune_start
        self.prune_scheduler = prune_scheduler(
            self.prune_target, self.ramp_time, self.prune_start
        )
        self.ramp_idx = ramp_idx
        self.step_count = 0

    def prune(self, model):
        r"""Prunes a model with a given pruning methodology according
        to the pruning schedule
        """
        raise Exception("Not implemented.")

    def step(self, model):
        r"""This step will prune the model, increment the
        step count, and if enough steps have been made, the pruning schedule
        will increment the pruning amount according to the pruning schedule
        for the next mini-batch.
        """
        self.prune(model)
        self.prune_amount = self.prune_scheduler(self.ramp_idx)
        self.step_count += 1
        if self.step_count % self.step_size == 0:
            self.ramp_idx += 1


class L1StructPruner(_Pruner):
    r"""Pruner that will perform Structured (Hardware Aware) L1 Pruning

    Attributes:
        prune_target (float): the final amount of pruning that will be applied.
            once the pruning scheduler has ramped up to its maximum.
        ramp_time (int): the number of ramp increments before the pruning amount reaches its
            final value.
        step_size (int): number of times we need to call the `step` method
            before ramping up the pruning schedule.
        prune_scheduler (fmot.AbstractPruningSchedule): a pruning scheduler in charge of
            managing how the pruning should ramp up.
            Default is :class:`fmot.utils.pruning.QuadrantSinePruningSchedule`.
        ramp_idx (int): the index in the ramping process.
        step_count (int): the step index. It's the number of time we have called `step`
            so far.
        min_numel (int): minimum number of elements that a parameter
            should contain in order to be pruned.
        prune_amount (float): current pruning amount that is to be applied
            according to the pruning schedule
    """

    def __init__(
        self,
        prune_target,
        ramp_time,
        step_size,
        prune_scheduler=QuadrantSinePruningSchedule,
        ramp_idx=0,
        prune_start=0.0,
        min_numel=2056,
        pencil_size=4,
        skip_prune_layers: List[int] = [],
    ):
        super().__init__(
            prune_target, ramp_time, step_size, prune_scheduler, ramp_idx, prune_start
        )
        self.min_numel = min_numel
        self.pencil_size = pencil_size
        self.skip_prune_layers = skip_prune_layers

    def prune(self, model):
        prune_model_parameters(
            model,
            self.prune_amount,
            pruning_function=pencil_pruning,
            min_numel=self.min_numel,
            pencil_size=self.pencil_size,
            skip_prune_layers=self.skip_prune_layers,
        )
