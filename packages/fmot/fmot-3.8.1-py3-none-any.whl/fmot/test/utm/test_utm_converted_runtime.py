from .get_utms import ALL_UTMS
import pytest


@pytest.mark.parametrize("name", ALL_UTMS.keys())
def test_converted_runtime(name):
    ALL_UTMS[name].test_converted_runtime()
