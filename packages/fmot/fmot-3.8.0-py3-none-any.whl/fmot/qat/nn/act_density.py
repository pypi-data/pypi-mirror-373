import torch
from .density_matmul import _MMBase


def measure_density_metrics(model, *metrics):
    output = {}
    for metric in metrics:
        output[metric] = measure_density_metric(model, metric)
    return output


def measure_density_metric(model, metric):
    if metric == "act_density":
        return ActDensity.measure_act_density(model)
    elif metric == "lookup_density":
        return ActDensity.measure_lookup_density(model)
    elif metric == "fanout_density":
        return ActDensity.measure_fanout_density(model)
    else:
        raise Exception("Unknown activation density")


class ActDensity:
    r"""Class storing static methods for
    activation density computations. These densities
    are computed only for matrix-vector multiplication layers
    of the form :math:`W \cdot x` that are following a
    ReLU (sparsification layer).

    The activation densities computations are based on four factors:
        - :math:`f_i` is the fanout (number of non-zero) for column i
        - :math:`\delta_i` is the per-element average activation density vector
        - :math:`N_i` is the number of times the operation is called
        - :math:`S_i` is the total number of elements in the matrix
    """

    @staticmethod
    def measure_act_density(model):
        r"""Measure the Activation Density for a model. The formula
        is given by:

        .. math::
            \frac{\bar{\delta_i} N_i}{\sum_i N_i}
        """

        tot_density = 0
        tot_weight = 0
        for module in model.modules():
            if isinstance(module, _MMBase) and module.has_sparse_input:
                tot_density += module.delta.mean() * module.nb_iter
                tot_weight += module.nb_iter

        if tot_weight == 0:
            raise Exception(
                "The model don't have any sparsified layers. "
                "Density metrics can only be measured after ReLU activations."
            )

        return tot_density / tot_weight

    @staticmethod
    def measure_lookup_density(model):
        r"""Measure the Lookup Density for a model, which indicates
        the fraction of matrix elements to be read from memory.
        The formulais given by:

        .. math::
            \frac{\sum_{i}f_i \cdot \delta_i N_i}{\sum_i S_i N_i}
        """
        tot_lookup = 0
        tot_weight = 0
        for module in model.modules():
            if isinstance(module, _MMBase) and module.has_sparse_input:
                tot_lookup += module.delta.dot(module.fanout()) * module.nb_iter
                tot_weight += module.mat.numel() * module.nb_iter

        if tot_weight == 0:
            raise Exception(
                "The model don't have any sparsified layers. "
                "Density metrics can only be measured after ReLU activations."
            )

        return tot_lookup / tot_weight

    @staticmethod
    def measure_fanout_density(model):
        r"""Measure the Fanout Density for a model, which provides
        the average activation density of the vector weighted by the
        fanout of the matrix.

        .. math::
            \frac{\sum_{i}f_i \cdot \delta_i N_i}{\sum_i (\sum_k f_i(k)) N_i}
        """
        tot_fanout = 0
        tot_weight = 0
        for module in model.modules():
            if isinstance(module, _MMBase) and module.has_sparse_input:
                tot_fanout += module.delta.dot(module.fanout()) * module.nb_iter
                tot_weight += module.fanout().sum() * module.nb_iter

        if tot_weight == 0:
            raise Exception(
                "The model don't have any sparsified layers. "
                "Density metrics can only be measured after ReLU activations."
            )

        return tot_fanout / tot_weight
