def _get_dir():
    import pathlib

    return pathlib.Path(__file__).parent.resolve()


__version__ = (_get_dir() / "VERSION").read_text(encoding="utf-8").strip()

import torch
from . import torchscript_utils
from . import configure
from .configure import CONFIG, ROUND_CONFIG
from . import nn
from . import qat, utils, convert, tracing
from ._open_docs import open_docs
from ._supported_ops import supported_ops, conversion_branch
from .convert.conversion_api import ConvertedModel
from .convert.lut_registry import LUT_REGISTRY, register_lut, LUTConfig
from .utils import save, load
from .sparse import *
from .beta import *
from . import fqir
from .stateful_sequencer import set_sequencer_p_inherit
from .control import *
from .functional import tag
from . import precisions
from .precisions import int24, int16, int8, Precision
from .iospec import iospec_from_fqir
