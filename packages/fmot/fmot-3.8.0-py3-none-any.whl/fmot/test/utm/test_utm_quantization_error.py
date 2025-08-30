from fmot.test.utm.get_utms import ALL_UTMS
import pytest
from fmot.test.utm.quant_tolerances import load_tolerances

TOLERANCES = load_tolerances()
CASES = (
    [(name, "standard") for name in ALL_UTMS]
    + [(name, "double") for name in ALL_UTMS]
    + [(name, "eights") for name in ALL_UTMS]
)


@pytest.mark.parametrize("name,precision", CASES)
def test_quantization_error(name, precision):
    utm = ALL_UTMS[name]
    key = f"{name}-{precision}"
    if key in TOLERANCES:
        tol = TOLERANCES[key]
        utm.test_quantization_error(tol, bw_conf=precision)
    else:
        pytest.skip(reason=f"No tolerance defined for testcase {key}")


if __name__ == "__main__":
    test_quantization_error(list(ALL_UTMS.keys())[0])
