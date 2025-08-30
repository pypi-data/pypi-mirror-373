"""Unit tests for the cythonized_setup function in cythonize_setup.py."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import python_build_utils.cythonized_setup as mod


@pytest.fixture(autouse=True)
def restore_env() -> None:
    """Ensure environment is reset after each test."""
    original = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original)


def test_pure_python_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that setup is called without Cython when CYTHON_BUILD is not set."""
    monkeypatch.delenv("CYTHON_BUILD", raising=False)
    mock_setup = MagicMock()
    monkeypatch.setattr(mod, "setup", mock_setup)

    mod.cythonized_setup("dummy_module")

    mock_setup.assert_called_once()
    args, kwargs = mock_setup.call_args
    assert kwargs["ext_modules"] == []


def test_cythonized_setup_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test that setup is called with Cythonized extensions when CYTHON_BUILD is set."""
    os.environ["CYTHON_BUILD"] = "1"

    # Prepare dummy .py file
    src_dir = tmp_path / "src" / "dummy_module"
    src_dir.mkdir(parents=True)
    dummy_file = src_dir / "foo.py"
    dummy_file.write_text("def bar(): pass")

    monkeypatch.chdir(tmp_path)

    with (
        patch("Cython.Build.cythonize", return_value=["dummy_ext"]) as mock_cythonize,
        patch("Cython.Compiler.Options"),
        patch("python_build_utils.cythonized_setup.setup") as mock_setup,
    ):
        mod.cythonized_setup("dummy_module")
        mock_cythonize.assert_called()
        mock_setup.assert_called()
        mock_setup.assert_called_once()


def test_cython_required_but_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ImportError is raised with clear message when Cython is missing."""
    os.environ["CYTHON_BUILD"] = "1"

    monkeypatch.setattr(mod, "setup", MagicMock())

    with (
        patch.dict(sys.modules, {"Cython": None, "Cython.Build": None, "Cython.Compiler": None}),
        pytest.raises(ImportError, match="Cython is required"),
    ):
        mod.cythonized_setup("dummy_module")
