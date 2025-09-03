"""Test the fmot package"""


def test_package_setup():
    """Test that the package can be imported"""
    import fmot as pkg

    assert hasattr(pkg, "__file__")  # is it installed?
    assert hasattr(pkg, "__version__")  # does it define a version attribute?


if __name__ == "__main__":
    test_package_setup()
