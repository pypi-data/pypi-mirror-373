from fmot.exceptions import ConversionDependencyError
from . import auto_multiprecision


def optimize_mixed_precision(
    cmodel,
    objective,
    eta,
    inputs,
    targets,
    niter=1,
    loss_type="polynomial",
    device="cpu",
    **kwargs
):
    r"""Heuristic search for an optimal mixed-precision configuration.

    A mixed-precision configuration uses different integer bitwidths throughout
    the model to reduce computational latency and energy when deployed in
    hardware.

    Args:
        objective (callable): Objective function to co-minimize with energy.
            Must have the signature :attr:`fn(output, target)` where
            :attr:`output` is the model output and :attr:`target` is a
            ground truth target. Must also return a single value.
        eta (float): A hyperparameter between 0 and 1 to tune the relative weighting between
            the objective function and energy minimization
        inputs (list[Tensor] or list[tuple[Tensor]]): A set of inputs to the model.
            If the model takes multiple inputs, :attr:`inputs` can be a list of tuples of
            tensors, where each tuple holds a set of model inputs.
        targets (list[Tensor]): A set of ground-truth targets; should be the same length and
            1-to-1 with :attr:`inputs`. Used as the second argument to :attr:`objective`.
        niter (int): Number of iterations of the optimization algorithm. Default is 1.
        ramp_eta (bool): If true, :attr:`eta` will be linearly ramped over
            the course of the :attr:`niter` repetitions. Default is True.
        loss_type (str): :attr:`'polynomial'`, :attr:`'logarithmic'`, or
            :attr:`'exponential'`. :attr:`polynomial` is the default. :attr:`logarithmic`
            should be used for loss functions that are logarithmic with the model's
            performance, such as cross-entropy, kl-divergence, and signal-to-noise-ratio.
            :attr:`polynomial` should used if the loss function is linear or polynomial with
            the model's performance, such as mean-squared-error, accuracy, F1, precision,
            and recall.
        num_inputs_per_step (int): number of inputs to use for each step of optimization.
            Default is :attr:`None`, in which case the objective will be averaged on
            all of the provided inputs and targets for each step of optimization. For
            large models and/or large sets of inputs/targets, this can be prohibitively
            slow, in which case a subset of the inputs/targets of size
            :attr:`num_inputs_per_step` can be used.
        device (str or :class:`torch.device`): Device that model is on. Default is 'cpu'.

    The mixed-precision-optimization algorithm tries to co-minimize the objective
    function with the model's energy. The overall objective is:

    .. math::

        C = (1-\eta)*\tilde{L}(y, \hat{y}) + \eta * \tilde{E}(model)

    Here, :math:`\tilde{L}(y, \hat{y})` is the function provided as :attr:`objective`, normalized
    and rescaled so that the most aggressively quantized version of the model gets a
    value of 0 and the least aggressively quantized version of the model gets a value of
    1. :math:`\tilde{E}(model)` is a rough energy estimate of the model's energy consumption,
    rescaled between 0 and 1.

    Mixed-precision-optimization will affect the model in-place, but the model can
    always be reverted back by calling `modify_precision` or
    calling mixed-precision-optimization again with different parameters.
    """
    if not cmodel.quantized:
        raise ConversionDependencyError(
            "Model must be quantized before optimizing mixed-precision config."
            + " Call `.quantize()` first"
        )
    model, energy, loss = auto_multiprecision.optimize_mixed_precision(
        cmodel,
        cmodel,
        objective=objective,
        eta=eta,
        inputs=inputs,
        targets=targets,
        niter=niter,
        ramp_eta=True,
        loss_type=loss_type,
        device=device,
        **kwargs
    )
    return energy, loss
