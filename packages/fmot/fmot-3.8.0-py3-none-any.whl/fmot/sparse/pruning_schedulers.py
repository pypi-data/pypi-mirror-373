import math


def get_ramp_time(dl_len, n_epochs_to_ramp, step_size):
    """

    Args:
        dl_len (int): length of the dataloader, which is the number of batches.
        n_epochs_to_ramp (int): number of epochs to ramp. How many  epochs before we reach the target pruning parameter.
        step_size (int): number of batches

    Returns:

    """
    ramps_per_epoch = dl_len / step_size
    ramp_time = n_epochs_to_ramp * ramps_per_epoch

    return ramp_time


class AbstractPruningSchedule:
    r"""Base class to inherit from for Pruning Schedule.

    Attributes:
        target (float): pruning amount to attain at ramp_time
        ramp_time (int): number of steps before reaching
            the final pruning target amount
        init_level (float): initial amount of pruning to
            start with

    """

    def __init__(self, target, ramp_time, init_level=0.0):
        assert (target >= 0.0) and (target <= 1.0)
        assert ramp_time >= 0
        self.target = target
        self.ramp_time = ramp_time
        self.init_level = init_level

    def __call__(self, epoch_idx):
        r"""

        Args:
            epoch_idx (int): current step index

        Returns:
            prune_amount (float): the percentage of elements
                to prune for that epoch
        """
        raise Exception("Not implemented.")


class QuadrantSinePruningSchedule(AbstractPruningSchedule):
    r"""Sine Pruning Schedule class. Ramps from 0 to 1
     using the sine function over the first quadrant.

    Attributes:
        target (float): pruning amount to attain at ramp_time
        ramp_time (int): number of steps before reaching
            the final pruning target amount
        init_level (float): initial amount of pruning to
            start with

    """

    def __call__(self, epoch_idx):
        if self.ramp_time == 0:
            return self.target

        t = min(epoch_idx / self.ramp_time, 1)
        prune_amount = (self.target - self.init_level) * math.sin(
            math.pi / 2 * t
        ) + self.init_level

        return prune_amount


class ExponentialPruningSchedule(AbstractPruningSchedule):
    r"""Exponential Pruning Schedule class. The time constant tau
     of the exponential growth is set to :math:`ramp_time / 4`.
     For this Schedule, the pruning target is attained at ramp_time thanks to
     a scaling factor, instead of reaching 99.3% of the target value.

    Attributes:
        target (float): pruning amount to attain at ramp_time.
        ramp_time (int): number of steps before reaching
            the final pruning target amount.
        init_level (float): initial amount of pruning to
            start with

    """

    def __call__(self, epoch_idx):
        if self.ramp_time == 0:
            return self.target

        tau = self.ramp_time / 4
        # Scaling factor so we can converge to the prune_target
        scaling_factor = 1 - math.exp(-4)
        t = epoch_idx / tau
        prune_amount = (self.target - self.init_level) * min(
            1.0, (1 - math.exp(-t)) / scaling_factor
        ) + self.init_level

        return prune_amount


class LinearPruningSchedule(AbstractPruningSchedule):
    r"""Linear Pruning Schedule class.

    Attributes:
        target (float): pruning amount to attain at ramp_time
        ramp_time (int): number of steps before reaching
            the final pruning target amount
        init_level (float): initial amount of pruning to
            start with

    """

    def __call__(self, epoch_idx):
        if self.ramp_time == 0:
            return self.target

        t = min(epoch_idx / self.ramp_time, 1)
        prune_amount = (self.target - self.init_level) * t + self.init_level

        return prune_amount


PRUNING_SCHEDULERS = {
    "sine": QuadrantSinePruningSchedule,
    "linear": LinearPruningSchedule,
    "exponential": ExponentialPruningSchedule,
}
