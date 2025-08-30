from torch import nn
import torch
import fmot
from fmot import qat as Q
import numpy as np
from torch import Tensor, nn
from typing import List, Tuple, Optional
import textwrap
from functools import wraps
from fmot.qat.annotated_tensors import asint
from fmot.beta import optimize_mixed_precision
import warnings
import pytest
from fmot import CONFIG

################################################
# > Base UTM Class and Test Container Objects


def eval_method(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        _self = args[0]
        if isinstance(_self, nn.Module):
            _self.eval()
        output = func(*args, **kwargs)
        if isinstance(output, torch.nn.Module):
            output.eval()
        return output

    return new_func


class UTM(nn.Module):
    """Unit Test Module

    UTMs provide a method to reproducibly generate random inputs
    """

    def __init__(
        self,
        batch_dim=0,
        seq_dim=None,
        converted_rtol=5e-3,
        converted_rms=1e-3,
        quantized_rtol=1e-2,
        allow_fqir_offby=1,
        skip_mixed=False,
        skip_standard=False,
    ):
        super().__init__()
        self.seed = 0
        self.bw_conf = None
        self.interpolate = None
        self.batch_dim = batch_dim
        self.seq_dim = seq_dim
        self.converted_rtol = converted_rtol
        self.converted_rms = converted_rms
        self.allow_fqir_offby = allow_fqir_offby
        self.quantized_rtol = quantized_rtol
        self.skip_mixed = skip_mixed
        self.skip_standard = skip_standard
        self.config_kwargs = {}

    def set_config_kwargs(self, **kwargs):
        self.config_kwargs = kwargs

    def get_random_inputs(self, batch_size):
        """Returns a random batch of inputs to the model, incrementing the random seed

        UTMs provide reproducible inputs. For the same sequence of get_random_inputs calls,
        the same sequence of inputs will be returned.

        Args:
            batch_size (int): Batch size of inputs to generate
        """
        torch.manual_seed(self.seed)
        self.seed += 1
        inputs = self._get_random_inputs(batch_size)
        if not isinstance(inputs, tuple):
            inputs = (inputs,)
        return inputs

    def reset_seed(self):
        """Reset the random seed that is used for generating random inputs"""
        self.seed = 0

    def _get_random_inputs(self, batch_size):
        """Implemented by each UTM subclass

        Expected to return a set of inputs for the model at a given batch size.

        Called by :method:`get_random_inputs`
        """
        raise NotImplementedError(
            f"UTM subclass {self.__class__.__name__} must implement _get_random_inputs"
        )

    @eval_method
    def get_converted_model(self, bw_conf="double", interpolate=True):
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        with CONFIG.configure(**self.config_kwargs):
            if self.bw_conf is not None:
                bw_conf = self.bw_conf
            if self.interpolate is not None:
                interpolate = self.interpolate
            cmodel = fmot.ConvertedModel(
                self,
                precision=bw_conf,
                batch_dim=self.batch_dim,
                seq_dim=self.seq_dim,
                interpolate=interpolate,
            )

        return cmodel

    @eval_method
    def get_quantized_model(
        self, B_quant=8, N_quant=10, bw_conf="double", interpolate=True
    ):
        """Returns a quantized (reproducibly), converted qat model

        .. warning::

            Quant config may change if the user changes ``B_quant`` or ``N_quant`` from defaults

        Args:
            B_quant (int): Batch size for quantizing inputs
            N_quant (int): Number of quantizing inputs
            bw_conf (str): Bitwidth config
        """
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        cmodel = self.get_converted_model(bw_conf, interpolate)
        self.reset_seed()
        inputs = [self.get_random_inputs(B_quant) for __ in range(N_quant)]
        cmodel.quantize(inputs)
        return cmodel

    @eval_method
    @torch.no_grad()
    def get_mixed_precision_model(self, eta=0.3, B_quant=8, N_quant=10):
        self.reset_seed()
        inputs = [self.get_random_inputs(B_quant) for __ in range(N_quant)]
        targets = [self(*x) for x in inputs]

        def objective(output, target):
            if isinstance(output, torch.Tensor):
                output = (output,)
            if isinstance(target, torch.Tensor):
                target = (target,)
            mse = 0
            for y, targ in zip(output, target):
                mse += (y - targ).pow(2).mean() / targ.pow(2).mean()
            return mse

        cmodel = self.get_quantized_model(
            B_quant, N_quant, bw_conf="double", interpolate=True
        )
        optimize_mixed_precision(cmodel, objective, eta, inputs, targets)
        return cmodel

    @eval_method
    def get_fqir(
        self, B_quant=8, N_quant=10, bw_conf="double", interpolate=True, eta=0.3
    ):
        """Reproducibly generates fqir graph for the test model.

        .. warning::

            FQIR graph is not guaranteed to be the same if the user changes
            ``B_graph``, ``B_quant``, or ``N_quant`` from defaults.

        Args:
            B_graph (int): batch size used when tracing graph
            B_quant (int): Batch size for quantizing inputs
            N_quant (int): Number of quantizing inputs
            bw_conf (str): Bitwidth config
            remove_batchdim (int): Batch dimension to remove from fqir
        """
        self.reset_seed()
        if bw_conf == "mixed":
            cmodel = self.get_mixed_precision_model(eta, B_quant, N_quant)
        else:
            cmodel = self.get_quantized_model(B_quant, N_quant, bw_conf, interpolate)
        return cmodel.trace()

    @torch.no_grad()
    def test_converted_runtime(self, B_test=8, bw_conf="double", interpolate=True):
        """Test that the prequantized model outputs matches the original model outputs"""
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        self.reset_seed()
        cmodel = self.get_converted_model(bw_conf=bw_conf, interpolate=interpolate)
        x = self.get_random_inputs(B_test)
        y0 = self(*x)
        y1 = cmodel(*x)
        if not (isinstance(y0, tuple) or isinstance(y0, list)):
            y0, y1 = [y0], [y1]
        for yy0, yy1 in zip(y0, y1):
            rmse = (yy0 - yy1).square().mean().sqrt() / (
                yy0.square().mean().sqrt() + 1e-9
            )
            assert (
                rmse < self.converted_rms
            ), f"Normalized RMS error {rmse:.3E} above tolerance {self.converted_rms}"

            # np.testing.assert_allclose(yy0.numpy(), yy1.numpy(), rtol=self.converted_rtol)

    @torch.no_grad()
    def get_quantization_nrmse(
        self, B_test=8, B_quant=8, N_quant=10, bw_conf="double", interpolate=True
    ):
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        self.reset_seed()
        qmodel = self.get_quantized_model(B_quant, N_quant, bw_conf, interpolate)

        x = self.get_random_inputs(B_test)
        y0 = self(*x)
        y1 = qmodel(*x)
        if not (isinstance(y0, tuple) or isinstance(y0, list)):
            y0, y1 = [y0], [y1]

        y0, y1 = [
            torch.cat(list(map(torch.flatten, x))).detach().numpy() for x in [y0, y1]
        ]

        error = np.mean((y0 - y1) ** 2) / np.mean(y0**2)
        error = np.sqrt(error)
        error = float(error)
        return error

    @torch.no_grad()
    def test_quantization_error(
        self,
        tolerance: float,
        B_test=8,
        B_quant=8,
        N_quant=10,
        bw_conf="double",
        interpolate=True,
    ):
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        error = self.get_quantization_nrmse(
            B_test, B_quant, N_quant, bw_conf, interpolate
        )

        if error > tolerance:
            raise RuntimeError(
                f"Quant-Error {error:.3E} above tolerances: {tolerance:.3E}"
            )

    @staticmethod
    def _test_fqir_runtime(model, graph, x, remove_batchdim=0, offby=0):
        y_torch = model(*x)
        if isinstance(y_torch, torch.Tensor):
            y_torch = [y_torch]
        xq = tuple([xx.numpy() for xx in x])
        if remove_batchdim is not None:
            xq = tuple([np.take(xx, 0, axis=remove_batchdim) for xx in xq])
        y_fqir = graph.run(*xq)
        if isinstance(y_fqir, np.ndarray):
            y_fqir = [y_fqir]
        for yy_torch, yy_fqir in zip(y_torch, y_fqir):
            yy_torch = asint(yy_torch).numpy()
            if remove_batchdim is not None:
                yy_torch = np.take(yy_torch, 0, axis=remove_batchdim)

            diff = np.abs(yy_torch - yy_fqir)
            n_off = np.sum(diff > offby)
            assert np.max(diff) <= offby, (
                "Diff detected greater than allowed"
                f" off-by of {offby} in {n_off}/{diff.size} elements. max error: {np.max(diff)}"
            )
            if np.max(diff) > 0:
                warnings.warn(
                    f"Had nonzero FQIR-vs-QAT diff. Was {np.max(diff)}, within the set integer tolerance {offby}."
                )

    @torch.no_grad()
    def test_fqir_runtime(
        self,
        B_test=8,
        B_quant=8,
        N_quant=10,
        bw_conf="double",
        interpolate=True,
        remove_batchdim=0,
    ):
        """Test that the fqir runtime outputs matches the quantized qat outputs"""
        if bw_conf in ["standard", "eights"] and self.skip_standard:
            pytest.skip()

        qmodel = self.get_quantized_model(
            B_quant=B_quant, N_quant=N_quant, bw_conf=bw_conf, interpolate=interpolate
        )
        graph = qmodel.trace()

        self.reset_seed()
        x = self.get_random_inputs(B_test)
        UTM._test_fqir_runtime(
            qmodel,
            graph,
            x,
            remove_batchdim=remove_batchdim,
            offby=self.allow_fqir_offby,
        )

    @torch.no_grad()
    def test_mixed_precision_fqir_runtime(
        self, B_test=8, B_quant=8, N_quant=10, eta=0.3, remove_batchdim=0
    ):
        if self.skip_mixed:
            pytest.skip("Skipping mixed-precision testing")

        self.reset_seed()
        qmodel = self.get_mixed_precision_model(
            eta=eta, B_quant=B_quant, N_quant=N_quant
        )
        graph = qmodel.trace()
        self.reset_seed()
        x = self.get_random_inputs(B_test)
        UTM._test_fqir_runtime(
            qmodel,
            graph,
            x,
            remove_batchdim=remove_batchdim,
            offby=self.allow_fqir_offby,
        )


class SUTM(UTM):
    """Sequencer Unit Test Module

    A subclass of UTM for modules containing sequencers
    """

    def __init__(
        self, batch_dim=0, seq_dim=1, input_size=None, nb_timesteps=None, **kwargs
    ):
        super().__init__(batch_dim=batch_dim, seq_dim=seq_dim, **kwargs)
        self.input_size = input_size
        self.nb_timesteps = nb_timesteps

    def forward(self, x):
        # We assume state to be None to avoid KeyError: 'aten::__is__'
        # Rk: We could make SUTM super structures
        assert hasattr(self, "net")
        output, __ = self.net(x)
        return output

    def _get_random_inputs(self, batch_size):
        x = torch.randn(batch_size, self.nb_timesteps, self.input_size)
        return x


class TestSet:
    """
    A container holding multiple parametrizations for a given UTM (unit
    test model) class.

    Args:
        utm (:class:`UTM`): A unit test model class
        par_sets (list): A list of dictionaries containing keyword arguments to initialize the UTM.
            Par sets may also specify a ``seed``, which will set the initial seed.
            Otherwise, the seed will be set to zero.
    """

    def __init__(self, utm, par_sets):
        assert issubclass(utm, UTM)
        self.utm = utm
        self.par_sets = par_sets

    def __getitem__(self, idx):
        """Manually reset the seed and initialize the utm from the idx'th parametrization"""
        kwargs = self.par_sets[idx].copy()

        if "seed" in kwargs:
            seed = kwargs.pop("seed")
        else:
            seed = 0

        torch.manual_seed(seed)
        utm = self.utm(**kwargs)
        return utm

    def __len__(self):
        return len(self.par_sets)

    def add_pars(self, pars):
        """Append a new parametrization dict to the par_set list"""
        self.par_sets.append(pars)

    def __repr__(self):
        return f"{self.utm.__name__}: {self.__len__()} test cases"

    def __str__(self):
        return f"{self.__len__()} test cases"


class TestLibrary:
    """A library holding pytorch model test sets"""

    def __init__(self, name):
        self.name = name
        self.test_sets = {}

    def __setitem__(self, key, test_set):
        assert isinstance(test_set, TestSet)
        self.test_sets[key] = test_set

    def __getitem__(self, key):
        return self.test_sets[key]

    def keys(self):
        return self.test_sets.keys()

    def values(self):
        return self.test_sets.values()

    def items(self):
        return self.test_sets.items()

    def __repr__(self):
        rep = f"TestLibrary {self.name}"
        rep += "\n\t" + "\n\t".join(
            [f"{k}:  {str(v)}" for k, v in self.test_sets.items()]
        )
        return rep
