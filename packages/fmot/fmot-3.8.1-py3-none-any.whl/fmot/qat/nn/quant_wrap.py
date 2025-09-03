from functools import partial
import torch
from torch import Tensor
from .quantizers import DEFAULT_OBSERVERS, Quantizer, FixedQuantaObserver
from .atomics import Requantize
from ..annotated_tensors import tag_dim, supports_int24
from typing import *
from inspect import Signature, _empty
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class QuantizationSpecificationError(Exception):
    pass


def recursive_key(x: Union[Tensor, dict, list, tuple], key: str):
    if x is None:
        return []
    elif isinstance(x, Tensor):
        return [key]
    elif isinstance(x, dict):
        return sum(
            [recursive_key(v, f"{key}.{subkey}") for subkey, v in x.items()], start=[]
        )
    elif isinstance(x, (list, tuple)):
        return sum(
            [recursive_key(v, f"{key}.{idx}") for idx, v in enumerate(x)], start=[]
        )


class ListQuantCollection(torch.nn.Module):
    def __init__(self, bitwidth, observer=DEFAULT_OBSERVERS["default"], **kwargs):
        super().__init__()
        self.bitwidth = bitwidth
        self.obs_class = partial(observer, **kwargs)
        self.quantizers = torch.nn.ModuleList()
        self.kwargs = kwargs

    def add_quantizer(self, value: Union[list, dict, Tensor]):
        if value is None or isinstance(value, Tensor):
            self.quantizers.append(Quantizer(self.bitwidth, observer=self.obs_class))
        elif isinstance(value, list):
            self.quantizers.append(ListQuantCollection(self.bitwidth, self.obs_class))
        elif isinstance(value, dict):
            self.quantizers.append(DictQuantCollection(self.bitwidth, self.obs_class))
        else:
            raise ValueError(f"Unexpected type {type(value)}")

    def forward(self, x: list):
        outputs = []
        for i, x in enumerate(x):
            if i + 1 > len(self.quantizers):
                self.add_quantizer(x)
            outputs.append(self.quantizers[i](x))
        return outputs

    def all_quantizers(self):
        out = []
        for q in self.quantizers:
            if isinstance(q, Quantizer):
                out.append(q)
            else:
                out += q.all_quantizers()
        return out

    def set_quantizer_quanta(self, idx, quanta=None, limits=None):
        bw = self.bitwidth.bitwidth


class DictQuantCollection(torch.nn.Module):
    def __init__(self, bitwidth, observer=DEFAULT_OBSERVERS["default"], **kwargs):
        super().__init__()
        self.bitwidth = bitwidth
        self.obs_class = partial(observer, **kwargs)
        self.quantizers = torch.nn.ModuleDict()
        self.kwargs = kwargs

    def add_quantizer(self, key: str, value: Union[list, tuple, dict, Tensor]):
        if value is None or isinstance(value, Tensor):
            self.quantizers[key] = Quantizer(self.bitwidth, observer=self.obs_class)
        elif isinstance(value, dict):
            self.quantizers[key] = DictQuantCollection(self.bitwidth, self.obs_class)
        elif isinstance(value, (list, tuple)):
            self.quantizers[key] = ListQuantCollection(self.bitwidth, self.obs_class)
        else:
            raise ValueError(f"Unexpected type {type(value)}")

    def forward(self, x: dict):
        outputs = OrderedDict()
        for k, v in x.items():
            if k not in self.quantizers:
                self.add_quantizer(k, v)
            outputs[k] = self.quantizers[k](v)
        return outputs

    def all_quantizers(self):
        out = []
        for q in self.quantizers.values():
            if isinstance(q, Quantizer):
                out.append(q)
            else:
                out += q.all_quantizers()
        return out


def get_fixed_observer(bitwidth: int, quanta, limits):
    if quanta is not None:
        obs = FixedQuantaObserver(quanta)
    elif limits is not None:
        assert isinstance(limits, tuple)
        assert len(limits) == 2
        obs = FixedQuantaObserver.from_limits(
            *limits, bitwidth, i16_clipping_tolerance=2
        )
    else:
        raise QuantizationSpecificationError(
            f"Need either non-None quanta or non-None limits to contruct a FixedQuantaObserver"
        )
    return obs


class QuantCollection(torch.nn.Module):
    """Stores a set of quantizers of the inputs to the model."""

    def __init__(
        self,
        bitwidth,
        signature: Optional[Signature] = None,
        observer=DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        super().__init__()
        self.bitwidth = bitwidth
        self._user_quanta_configs = {}
        self.obs_class = partial(observer, **kwargs)
        self.quantizers = torch.nn.ModuleList()
        self.signature = signature
        if signature is not None:
            for _ in range(len(signature.parameters)):
                self.add_quantizer()

        self.utilized_signature = []
        self._built = False

    def add_quantizer(self):
        quantizer = Quantizer(self.bitwidth, observer=self.obs_class)
        idx = len(self.quantizers)
        if idx in self._user_quanta_configs:
            fixed_obs_conf = self._user_quanta_configs[idx]
            obs = get_fixed_observer(self.bitwidth.bitwidth, **fixed_obs_conf)
            quantizer.observer = obs
        self.quantizers.append(quantizer)

    def check_matches_signature(self, *args, **kwargs):
        if self.signature is not None:
            params = self.signature.parameters
            kwarg_keys = set(list(params.keys())[len(args) :])
            for k in kwargs:
                kwarg_keys.remove(k)

            # make sure remaining kwarg_keys have defaults
            for k in kwarg_keys:
                if params[k] == _empty:
                    raise ValueError(
                        f"Called model without specifying required arg {kwarg_keys}"
                    )

    def get_signature_name(self, key: Union[int, str]):
        if isinstance(key, int):
            return list(self.signature.parameters.keys())[key]
        else:
            return key

    def call_quantizer(self, idx: int, x: Optional[Union[Tensor, dict, list, tuple]]):
        key = self.get_signature_name(idx)
        quantizer = self.quantizers[idx]

        if x is None:
            res = None

        elif isinstance(x, Tensor) and isinstance(quantizer, Quantizer):
            logger.debug(f"calling quantizer {idx} with {quantizer.quantize=}")
            res = quantizer(x)
        else:
            # need to change the type of quantizer
            if idx in self._user_quanta_configs:
                raise QuantizationSpecificationError(
                    f"input index {idx} has a specified quanta config, but needs a structured "
                    "quantizer."
                )

            if isinstance(x, Tensor) and not isinstance(quantizer, Quantizer):
                if self._built:
                    raise QuantizationSpecificationError(
                        f"Input does not match the known signature (Tensor input into {type(quantizer)})"
                    )
                quantizer = Quantizer(self.bitwidth, self.obs_class)
                self.quantizers[idx] = quantizer
                res = quantizer(x)

            elif isinstance(x, dict) and isinstance(quantizer, DictQuantCollection):
                res = quantizer(x)

            elif isinstance(x, dict) and not isinstance(quantizer, DictQuantCollection):
                if self._built:
                    raise QuantizationSpecificationError(
                        f"Input does not match the known signature (dict input into {type(quantizer)})"
                    )
                if isinstance(quantizer.observer, FixedQuantaObserver):
                    raise QuantizationSpecificationError(
                        f"Input {idx} has a specified quanta config, but needs a structured quantizer."
                    )
                quantizer = DictQuantCollection(self.bitwidth, self.obs_class)
                self.quantizers[idx] = quantizer
                res = quantizer(x)

            elif isinstance(x, (list, tuple)) and not isinstance(
                quantizer, ListQuantCollection
            ):
                if self._built:
                    raise QuantizationSpecificationError(
                        f"Input does not match the known signature (list/tuple input into {type(quantizer)})"
                    )
                if isinstance(quantizer.observer, FixedQuantaObserver):
                    raise QuantizationSpecificationError(
                        f"Input {idx} has a specified quanta config, but needs a structured quantizer."
                    )
                quantizer = ListQuantCollection(self.bitwidth, self.obs_class)
                self.quantizers[idx] = quantizer
                res = quantizer(x)
            elif isinstance(x, (list, tuple)) and isinstance(
                quantizer, ListQuantCollection
            ):
                res = quantizer(x)

            else:
                raise ValueError(
                    f"Incompatible types: quantizer: {type(quantizer)} x: {type(x)}"
                )

        sig = recursive_key(res, key)
        return res, sig

    def forward(self, *args, **kwargs):
        self.check_matches_signature(*args, **kwargs)
        new_args = []
        self.utilized_signature = []

        for i, arg in enumerate(args):
            if i + 1 > len(self.quantizers):
                if self.signature is None:
                    self.add_quantizer()
                else:
                    raise ValueError("Recieved an unexpected number of inputs")
            arg, sig = self.call_quantizer(i, arg)
            new_args.append(arg)
            self.utilized_signature += sig

        if len(kwargs) != 0 and self.signature is None:
            raise ValueError(
                f"Cannot call model with unknown signature using keyword arguments"
            )

        new_kwargs = {}
        for key, arg in kwargs.items():
            idx = list(self.signature.parameters.keys()).index(key)
            arg, sig = self.call_quantizer(idx, arg)
            new_kwargs[key] = arg
            self.utilized_signature += sig

        self._built = True

        return new_args, new_kwargs

    def all_quantizers(self) -> List[Quantizer]:
        out = []
        for q in self.quantizers:
            if isinstance(q, Quantizer):
                out.append(q)
            elif isinstance(q, (DictQuantCollection, ListQuantCollection)):
                out += q.all_quantizers()
            else:
                raise ValueError(f"Unexpected type {type(q)} in self.quantizers")
        return out

    def set_quanta(self, idx: int, quanta=None, limits=None):
        if idx >= len(self.quantizers):
            # hold this as an annotation for later when we construct the quantizer
            self._user_quanta_configs[idx] = {"quanta": quanta, "limits": limits}
        else:
            quantizer = self.quantizers[idx]
            if not isinstance(quantizer, Quantizer):
                raise QuantizationSpecificationError(
                    f"input at index {idx} is structured, cannot have a predefined quant-config"
                )
            obs = get_fixed_observer(
                self.bitwidth.bitwidth, quanta=quanta, limits=limits
            )
            quantizer.observer = obs


class RequantizeCollection(torch.nn.Module):
    def __init__(
        self,
        bitwidth,
        observer=DEFAULT_OBSERVERS["default"],
        **kwargs,
    ):
        super().__init__()
        self.requantizers = torch.nn.ModuleList()
        self.idx_to_req_idx: Dict[int, int] = dict()
        self.bitwidth = bitwidth
        self.obs_cls = partial(observer, **kwargs)
        self._built = False

    def get_requantizer(self, idx):
        if idx in self.idx_to_req_idx:
            return self.requantizers[self.idx_to_req_idx[idx]]
        else:
            # create a new requantizer at the given index
            req = Requantize(self.bitwidth, observer=self.obs_cls)
            self.requantizers.append(req)
            self.idx_to_req_idx[idx] = len(self.idx_to_req_idx)
            return req

    @supports_int24(False, reason="int24 outputs are not supported")
    def forward(self, args: Any):
        # do nothing if no requantizers are registered
        if len(self.requantizers) == 0:
            return args

        # if there are registered requantizers,
        # apply them to the arguments
        if isinstance(args, Tensor):
            orig_type = "tensor"
            args = (args,)
        elif isinstance(args, tuple):
            orig_type = "tuple"
        elif isinstance(args, list):
            orig_type = "list"
        else:
            raise ValueError(
                f"RequantizeCollection recieved an input of type {type(args)}, "
                "expected Tensor, list[Tensor], or tuple[Tensor]"
            )

        new_args = []
        for i, arg in enumerate(args):
            if i in self.idx_to_req_idx:
                assert isinstance(
                    arg, Tensor
                ), f"Output requantization expected a Tensor, got {type(arg)}"
                req = self.get_requantizer(i)
                arg = req(arg)
            new_args.append(arg)

        self._built = True

        if orig_type == "tensor":
            res = new_args[0]
            assert isinstance(res, Tensor)
            return res
        elif orig_type == "tuple":
            return tuple(new_args)
        elif orig_type == "list":
            return new_args
        else:
            raise NotImplementedError(f"Need to implement casting rule for {orig_type}")

    def set_quanta(self, idx, quanta=None, limits=None):
        bw = self.bitwidth.bitwidth
        obs = get_fixed_observer(bw, quanta, limits)
        req = self.get_requantizer(idx)
        req.quantizer.observer = obs


class QuantWrapper(torch.nn.Module):
    def __init__(
        self,
        model,
        bitwidth,
        observer=DEFAULT_OBSERVERS["default"],
        signature: List[str] = None,
        dimensions=None,
        **kwargs,
    ):
        super().__init__()
        self.quantizers = QuantCollection(
            bitwidth, signature=signature, observer=observer, **kwargs
        )
        self.bitwidth = bitwidth
        self.model = model
        self.dimensions = dimensions
        self.signature = signature
        self.requantizers = RequantizeCollection(bitwidth, observer, **kwargs)

    @tag_dim
    def forward(self, *args, **kwargs):
        args, kwargs = self.quantizers(*args, **kwargs)
        res = self.model(*args, **kwargs)
        new_res = self.requantizers(res)
        return new_res
