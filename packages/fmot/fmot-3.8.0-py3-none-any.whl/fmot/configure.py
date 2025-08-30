from typing import *
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager


@dataclass
class FMOTConfig:
    """
    FMOTConfig can be used to change the behavior of
    model conversion, enabling/disabling certain optimizations
    and mappings.
    """

    # observers
    param_observer: str = "min_max"
    default_observer: str = "min_max"
    minmax_headroom: int = 0

    # nn.Linear quantization mode
    pow2_linear_scale: bool = True
    perchannel_linear: bool = False

    # lookup table interpolation
    interpolate: bool = True
    sim_fixed_range_fp: bool = True
    ilut_requant: bool = False
    insert_fixed_range_observers: bool = True
    # telescoping luts
    telescope_interpolate: bool = True
    # efficient LUT implementations
    fast_ilut: bool = True

    # endpoint saturation for sigmoid/tanh
    forced_endpoint_saturation = False

    # rnn configuration
    rnn_mm_limits: bool = False

    # lstm config
    fused_lstm: bool = True

    # sim quantization w/ rounding
    quant_round: bool = True
    quant_round_all: bool = False

    """
    addition decimal alignment behavior:
       z = x + y
       quantas: qz, qx, qy
       WLOG, qy >= qx, so qy - qx >= 0
    If lshift_qmax = True: 
       z = (x + y << (qy - qx)) << (qz - qx)
    If lshift_qmax = False:
       z = (x >> (qy - qx) + y) << (qz - qy)
    """
    lshift_qmax: bool = False

    @contextmanager
    def configure(self, **kwargs):
        prev_state = asdict(self)

        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            yield
        finally:
            for k, v in prev_state.items():
                setattr(self, k, v)

    def reset(self):
        cfg = FMOTConfig()
        for key, value in asdict(cfg).items():
            setattr(self, key, value)


CONFIG = FMOTConfig()


@dataclass
class RoundingConfig:
    """Determines the rounding behavior of different fmot
    operators"""

    prod: bool = True
    mul: bool = True
    add: bool = True
    lut: bool = False
    imm: bool = True
    shift: bool = False

    @property
    def vvadd(self):
        return CONFIG.quant_round and self.add

    @property
    def viadd(self):
        return CONFIG.quant_round and self.add and self.imm

    @property
    def vvmul(self):
        return CONFIG.quant_round and self.mul

    @property
    def vimul(self):
        return CONFIG.quant_round and self.mul and self.imm

    @property
    def matmul(self):
        return CONFIG.quant_round and self.prod

    @property
    def fast_ilut_add(self):
        return CONFIG.quant_round and self.add and self.lut

    @property
    def fast_ilut_mul(self):
        return CONFIG.quant_round and self.mul and self.lut

    @property
    def vshift(self):
        return CONFIG.quant_round and self.shift

    def reset(self):
        cfg = RoundingConfig()
        for key, value in asdict(cfg).items():
            setattr(self, key, value)


ROUND_CONFIG = RoundingConfig()


def configure_param_observer(obs_class: str = "min_max"):
    """
    Configure the default parameter observer.

    Arguments:
        obs_class (str): Default 'min_max'. Options are:
                'min_max': MinMaxObserver
                'moving_min_max': MovingAverageMinMaxObserver
                'gaussian': GaussianObserver
    """
    CONFIG.param_observer = obs_class


def configure_act_observer(obs_class: str = "min_max"):
    """
    Configure the default activation observer.

    Arguments:
        obs_class (str, or class): Default 'min_max'. Options are:
                'min_max': MinMaxObserver
                'moving_min_max': MovingAverageMinMaxObserver
                'gaussian': GaussianObserver
    """
    CONFIG.default_observer = obs_class
