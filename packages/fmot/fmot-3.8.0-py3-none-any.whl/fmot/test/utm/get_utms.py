from fmot.test import atomic_library, rnn_library, feedforward_library
from .unittest_objects import UTM
import pytest
import numpy as np
from typing import *

SKIPPED_UTMS = [
    ("row_major_addmm", 13),
    ("lin_gru_lin", 2),
    ("lin_gru_lin", 3),
]

# disable of big_conv1d, dw_conv1d, tc_resnet
skipped_rnns = ["big_conv1d", "tc_resnet", "small_tc_resnet", "tiny_tc_resnet"]
for skipped in skipped_rnns:
    for i in range(len(rnn_library[skipped])):
        SKIPPED_UTMS.append((skipped, i))


def get_name(library, key, idx):
    return f"{library.name}_{key}_{idx}"


def get_all_utms(libraries) -> Dict[str, UTM]:
    all_utms = {}
    for library in libraries:
        for key, test_set in library.items():
            for idx in range(len(test_set)):
                if (key, idx) not in SKIPPED_UTMS:
                    all_utms[get_name(library, key, idx)] = library[key][idx]
    return all_utms


ALL_UTMS = get_all_utms([atomic_library, feedforward_library, rnn_library])
