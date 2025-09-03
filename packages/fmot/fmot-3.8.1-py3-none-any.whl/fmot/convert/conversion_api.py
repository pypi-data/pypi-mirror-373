import torch
from fmot.qat import bitwidths, control, standard, double
from fmot.exceptions import ConversionDependencyError
from fmot.tracing import trace
from fmot.qat.nn import DEFAULT_OBSERVERS, density_matmul, act_density, ObserverBase
from fmot.convert.default_substitutions import get_default_substitutions
from fmot import utils
from .quantizer_manager import generate_param2quantizer
from .prune_reparametrization import remove_all_pruners, reapply_all_pruners
from ._convert_to_qat import convert
from typing import *
from tabulate import tabulate
from fmot.configure import CONFIG
from fmot.fqir.utilities.set_signature import set_signature
from fmot.nn import (
    TemporalConv1d,
    TemporalConv2d,
    TemporalUnfold1d,
    TemporalConvTranspose1d,
    TemporalFoldTranspose1d,
    Sequencer,
    SRU,
)
import warnings


SEQ_LAYERS = (
    TemporalConv1d,
    TemporalConv2d,
    TemporalUnfold1d,
    TemporalConvTranspose1d,
    TemporalFoldTranspose1d,
    SRU,
    Sequencer,
    torch.nn.GRU,
    torch.nn.LSTM,
    torch.nn.RNN,
)


def is_sequential(model):
    """Checks recursively if the model contains layers that will be mapped to a Sequencer"""
    if isinstance(model, SEQ_LAYERS):
        return True

    for _, submodule in model.named_children():
        if is_sequential(submodule):
            return True

    return False


class ConvertedModel(torch.nn.Module):
    """
    Converts standard pytorch models to a form that can be quantized,
    pruned, and compiled to run on Femtosense hardware.

    Args:
        model (torch.nn.Module): pytorch model to convert
        precision (str): :attr:`'double'` for 8-bit parameters and 16-bit
            activations, or :attr:`'standard'` for 4-bit parameters and 8-bit
            activations. Default is :attr:`'double'`
        batch_dim (int): the batch dimension for the model's inputs. Default
            is :attr:`0`.
        seq_dim (int): temporal/sequential dimension, if the model recieves
            sequential data. Default is :attr:`None`.
        interpolate (bool): whether to use interpolating lookup tables for
            soft nonlinearities, default is :attr:`True`. Interpolation is
            only used in :attr:`'double'` precision.
        observer (fmot.qat.nn.ObserverBase): observer class to use when
            choosing quantization configurations for parameter and activation
            tensors. Default is :class:`fmot.qat.nn.MinMaxObserver`.
        observer_config (dict): keyword arguments to pass to the observer class,
            default is :attr:`None`.
        param_observer (str, optional): algorithm used to calibrate parameter quantization.
            Options: 'min_max' (default), 'gaussian'
    """

    def __init__(
        self,
        model,
        precision="double",
        named_dims=None,
        batch_dim=0,
        seq_dim=None,
        interpolate=None,
        observer=DEFAULT_OBSERVERS["default"],
        observer_config=None,
        param_observer: str = "min_max",
    ):
        super().__init__()
        self.named_dims = named_dims
        self.batch_dim = batch_dim
        self.seq_dim = seq_dim

        if interpolate is None:
            interpolate = CONFIG.interpolate

        if not isinstance(model, torch.nn.Module):
            raise ValueError("model must be a torch.nn.Module")
        if is_sequential(model) and (seq_dim is None):
            raise Exception(
                "Cannot convert sequential models (i.e. RNNs and Conv1d) "
                "without a seq_dim, denoting which input tensor dimension "
                "is the sequential dimension."
            )

        self.model, self._param_mapping_dict = convert(
            model=model,
            precision=precision,
            interpolate=interpolate,
            observer=observer,
            observer_conf=observer_config,
            verbose=False,
            dimensions=self._dimensions,
            param_observer=param_observer,
        )

        if not model.training:
            self.eval()

        self.quantized = False  #: whether the model simulates fixed-point quantization
        self._seen_input = False

        self.num_tracing_inputs = 0

        # attribute objects
        self.param2quant = dict()

        self.tracing_result = None

    def _set_tracing_inputs(self, *args):
        if all(isinstance(x, torch.Tensor) or x is None for x in args):
            self.num_tracing_inputs = len(args)
            for i, arg in enumerate(args):
                self.register_buffer(f"tracing_input_{i}", arg, persistent=False)
        else:
            self.num_tracing_inputs = None

    def _get_tracing_inputs(self):
        if self.num_tracing_inputs is not None:
            output = []
            for i in range(self.num_tracing_inputs):
                output.append(getattr(self, f"tracing_input_{i}"))
            return tuple(output)
        else:
            return None

    @property
    def _dimensions(self):
        """
        a list of the tensor dimensions,
        i.e. ['B', 'T', 'F'] for batch_dim, sequential_dim, feature_dim
        """
        if self.named_dims is not None:
            return self.named_dims

        if self.seq_dim is not None:
            dimensions = ["F"] * 3
            dimensions[self.batch_dim] = "B"
            dimensions[self.seq_dim] = "T"
        else:
            dimensions = ["F"] * 2
            dimensions[self.batch_dim] = "B"
        return dimensions

    def forward(self, *args, **kwargs):
        """
        Wrapper to the forward method of the converted model.
        """
        for module in self.modules():
            if isinstance(module, density_matmul._MMBase):
                module.reset_act_densities()

        self._seen_input = True
        return self.model(*args, **kwargs)

    def quantize(self, calibration_inputs):
        """Quantizes the model, given a set of calibration inputs. The model
        will be quantized after calling this method.

        Args:
            calibration_inputs (list[Tensor] or list[tuple[Tensor]]): A list
                of representative inputs to the model, used to calibrate the
                quantization configuration.
        """
        # save the first input as the tracing input
        cal0 = calibration_inputs[0]
        if isinstance(cal0, torch.Tensor):
            cal0 = [cal0]
        self._set_tracing_inputs(*cal0)

        if CONFIG.insert_fixed_range_observers:
            try:
                self._insert_fixed_range_observers(tuple(cal0))
            except:
                # warnings.warn("Failed to insert fixed range observers.")
                pass

        control.quantize(
            self.model, input_iterator=calibration_inputs, dimensions=self._dimensions
        )
        self.param2quant = generate_param2quantizer(self, calibration_inputs[0])

        self.quantized = True
        self._seen_input = True

    def trace(self, *args, **kwargs):
        """Express the model's computational graph as an FQIR graph.
        The FQIR graph describes an equivalent model, using only integer datatypes
        and operations.

        An error will be raised if the model has not been quantized first.

        Returns:
            :class:`fqir.GraphProto`: The FQIR representation of :attr:`quant_model`
        """
        training = self.training

        self.eval()

        if not self.quantized:
            raise ConversionDependencyError(
                'Must quantize model before tracing. Call "quantize" method first.'
            )

        if len(args) == 0 and len(kwargs) == 0:
            tracing_input = self._get_tracing_inputs()

            if tracing_input is None:
                raise ConversionDependencyError(
                    "Please pass inputs to the model in to trace()."
                )
            if isinstance(tracing_input, torch.Tensor):
                tracing_input = (tracing_input,)

            tracing_kwargs = {}
        else:
            tracing_input = args
            tracing_kwargs = kwargs

        result, tsrc_dict = trace(
            self.model,
            *tracing_input,
            batch_dim=self.batch_dim,
            seq_dim=self.seq_dim,
            **tracing_kwargs,
        )

        if training:
            self.train()

        self.tsrc_dict = tsrc_dict
        self.tracing_result = result

        arith = result["graph"].subgraphs["ARITH"]
        arith = set_signature(
            arith, input_names=self.model.quantizers.utilized_signature
        )

        return result["graph"]

    def get_iospec(self):
        """Get the IOSpec object for the traced FQIR graph. The IOSpec defines how input and
        output shapes changed when using strided :attr:`fmot.nn.TemporalConv1d` and :attr:`TemporalConvTranspose1d`
        layers."""
        if self.tracing_result is None:
            raise ValueError("Trace your model first.")
        else:
            return self.tracing_result["iospec"]

    def measure_density_metrics(self, *metrics):
        """Measure density metrics after a forward pass of the converted/quantized model

        Args:
            metrics (str): One or more density metrics to measure.
                Options include "act_density", "fanout_act_density", and "lookup_density".

        Returns:
            dict: Density measurements
        """
        if not self._seen_input:
            raise ConversionDependencyError(
                "At least one input must be passed through the "
                "model before enabling density metrics"
            )
        return act_density.measure_density_metrics(self, *metrics)

    def modify_precision(self, precision, in_place=True, orig_model=None):
        """Changes the model's precision

        Args:
            - precision (str): New precision to use
        """
        control.change_bitwidth_in_place(self, precision)

    def set_param_precision(self, param_name, precision):
        """Change a parameter bitwidth.

        Args:
            param_name (str): name of the parameter whose precision will be modified.
            precision (str): :attr:`'standard'`or :attr:`'double'`,
                new precision level for the associated quantizer.
        """
        if not self.quantized:
            raise ConversionDependencyError(
                "Model must be quantized before changing a parameter bitwidth."
                + " Call `.quantize()` first"
            )
        param_quantizer = self.param2quant[param_name]
        if precision == "standard":
            param_quantizer.update_bitwidth(standard)
        elif precision == "double":
            param_quantizer.update_bitwidth(double)
        else:
            raise Exception(
                "Unknown precision argument: available parameter precisions "
                + "are `standard` and `double`"
            )

    def set_input_details(self, input_index: int, quanta: int):
        """Enforces a particular quantization scale to be used for one
        of the model's inputs.

        Arguments:
            input_index (int): the index of the input with respect to the model's input signature
            quanta (int): the power-of-two exponent in the scaling factor
        """
        assert isinstance(quanta, int)
        self.model.quantizers.set_quanta(input_index, quanta=quanta)

    def set_output_details(self, output_index: int, quanta: int):
        """Enforces a particular quantization scale to be used for one
        of the model's outputs.

        Arguments:
            output_index (int): the index of the output with respect to the model's output signature
            quanta (int): the power-of-two exponent in the scaling factor
        """
        assert isinstance(quanta, int)
        self.model.requantizers.set_quanta(output_index, quanta=quanta)

    def _insert_fixed_range_observers(self, tracing_input):
        """
        Inserts fixed-range-observers into the model upstream of saturating nonlinearities.
        This restricts the output dynamic range of operations preceding operations like
        sigmoid or tanh to avoid wasting quantized dynamic range.
        """
        return utils.insert_fixed_range_observers(self.model, tracing_input)

    def enable_quantization(self, quantize=True):
        """
        Turns on quantization.

        Args:
            quantize (bool): if False, will disable quantization.
                Default :attr:`True`.
        """
        control.enable_quantization(self, value=quantize)

    def disable_quantization(self):
        """
        Turns off quantization.
        """
        control.disable_quantization(self)

    def enable_observation(self, observe=True):
        """
        Turns on observation.

        Args:
            observe (bool): if False, will disable observation.
                Default :attr:`True`.
        """
        control.enable_observation(self, value=observe)

    def disable_observation(self):
        """
        Turns off observation.
        """
        control.disable_observation(self)

    def get_parameter_table(self):
        """Returns out a summary of the model's parameters attributes:
        - tensor shape
        - density (percentage of non-zero elements)
        - precision (if parameter has been quantized)
        - memory (in Bytes, if parameter has been quantized)
        """
        # We remove amd reapply pruning in order to access to the updated
        # parameters if they have been pruned previously
        pruning_info = remove_all_pruners(self)
        parameter_table = dict()
        for name, param in self.named_parameters():
            if self.quantized:
                if name.endswith("_orig"):
                    name = name.split("_orig")[0]
                param_quantizer = self.param2quant[name]
            else:
                param_quantizer = None
            parameter_table[name] = utils.get_param_attributes(
                param, param_quantizer, formatting=False
            )

        reapply_all_pruners(self, self, pruning_info, self._param_mapping_dict)

        return parameter_table

    def print_parameter_table(self):
        """Prints out a summary of the model's parameters attributes:
        - name (use utils.rgetattr(self, name) to access to the param)
        - shape
        - density (percentage of non-zero elements)
        - precision (if parameter has been quantized)
        - memory (if parameter has been quantized)

        Output example:
            name                shape     precision    density    memory
            ------------------  --------  -----------  ---------  --------
            model.model.weight  (64, 64)  fqint8       100.0 %    4.0 kB
            model.model.bias    (64,)     fqint16      100.0 %    128.0 B
        """
        table = []
        headers = ["name", "shape", "precision", "density", "memory"]
        for name, param in self.named_parameters():
            if self.quantized:
                param_quantizer = self.param2quant[name]
            else:
                param_quantizer = None
            param_attr = utils.get_param_attributes(param, param_quantizer)
            param_attr["name"] = name
            table.append([param_attr[h] for h in headers])
        print(tabulate(table, headers=headers))

    def reset_observers(self):
        for module in self.modules():
            if isinstance(module, ObserverBase):
                module.reset()

        self.disable_quantization()
