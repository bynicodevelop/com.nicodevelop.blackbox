"""Tests for core trading logic."""

from blackbox import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Test that version follows semantic versioning."""
    parts = __version__.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()
