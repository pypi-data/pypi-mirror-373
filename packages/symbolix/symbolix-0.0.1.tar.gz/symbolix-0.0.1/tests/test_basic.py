"""Basic tests for symbolix package."""

import symbolix


def test_package_import() -> None:
    """Test that the package can be imported."""
    assert symbolix.__version__ == "0.1.0"


def test_package_has_version() -> None:
    """Test that the package has a version attribute."""
    assert hasattr(symbolix, "__version__")
    assert isinstance(symbolix.__version__, str)
