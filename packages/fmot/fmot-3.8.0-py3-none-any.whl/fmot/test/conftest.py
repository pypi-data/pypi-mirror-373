import pytest
import fmot


@pytest.fixture(autouse=True)
def setup_code():
    fmot.CONFIG.reset()
    fmot.ROUND_CONFIG.reset()
