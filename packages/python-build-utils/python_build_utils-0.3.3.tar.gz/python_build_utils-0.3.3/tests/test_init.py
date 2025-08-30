"""Tests for the public API and version fallback logic in python_build_utils.__init__."""

import importlib
import importlib.metadata
import sys
from importlib.metadata import PackageNotFoundError

import pytest

from python_build_utils import __version__


def test_version_found() -> None:
    """Sanity check: version is a non-empty string (should be fetched normally)."""
    assert isinstance(__version__, str)
    assert __version__  # not empty


def test_version_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simuleer een PackageNotFoundError om fallback naar 'unknown' te testen."""

    def raise_not_found(_: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)

    # Herlaad het __init__-bestand om opnieuw het version-fetchpad uit te voeren
    if "python_build_utils" in sys.modules:
        importlib.reload(sys.modules["python_build_utils"])

    import python_build_utils

    assert python_build_utils.__version__ == "unknown"
