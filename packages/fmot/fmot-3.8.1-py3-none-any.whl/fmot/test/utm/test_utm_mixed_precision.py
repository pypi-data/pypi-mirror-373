from .get_utms import ALL_UTMS
import pytest
import numpy as np

np.random.seed(0)
N_mixed = 100
mixed_prec_ids = np.random.choice(list(ALL_UTMS.keys()), size=N_mixed)


# @pytest.mark.parametrize("name", mixed_prec_ids)
# def test_mixed_precision_fqir_runtime(name):
#     ALL_UTMS[name].test_mixed_precision_fqir_runtime()
