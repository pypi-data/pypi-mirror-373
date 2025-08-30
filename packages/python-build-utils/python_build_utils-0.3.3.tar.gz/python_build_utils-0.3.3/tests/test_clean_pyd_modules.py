"""Tests for the clean_pyd_modules CLI and helpers."""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from python_build_utils.clean_pyd_modules import clean_by_extensions


logger = logging.getLogger("python_build_utils.clean_pyd_modules")
logger.setLevel(logging.INFO)


@pytest.fixture
def mock_src_path(tmp_path: Path) -> Path:
    """Fixture to create a temporary src directory."""
    src_path = tmp_path / "src"
    src_path.mkdir()
    return src_path


def test_clean_by_extensions_no_files_found(mock_src_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test when no files with the specified extension are found."""
    with caplog.at_level(logging.INFO):
        clean_by_extensions(mock_src_path, regex=None, extension="*.pyd")
    assert any("No *.pyd files found" in r.message for r in caplog.records)


def test_clean_by_extensions_files_removed(mock_src_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that files with the specified extension are removed."""
    file1 = mock_src_path / "module1.pyd"
    file2 = mock_src_path / "module2.pyd"
    file1.touch()
    file2.touch()

    with caplog.at_level(logging.INFO):
        clean_by_extensions(mock_src_path, regex=None, extension="*.pyd")

    assert not file1.exists()
    assert not file2.exists()
    assert any("Removing" in r.message for r in caplog.records)


def test_clean_by_extensions_regex_filter(mock_src_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that only files matching the regex are removed."""
    file1 = mock_src_path / "module1.pyd"
    file2 = mock_src_path / "test_module.pyd"
    file1.touch()
    file2.touch()

    with caplog.at_level(logging.INFO):
        clean_by_extensions(mock_src_path, regex="^test_.*", extension="*.pyd")

    assert file1.exists()
    assert not file2.exists()
    assert any("Removing" in r.message and "test_module.pyd" in r.message for r in caplog.records)


def test_clean_by_extensions_no_match_with_regex(mock_src_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that no files are removed if none match the regex."""
    file1 = mock_src_path / "module1.pyd"
    file2 = mock_src_path / "module2.pyd"
    file1.touch()
    file2.touch()

    with caplog.at_level(logging.INFO):
        clean_by_extensions(mock_src_path, regex="^test_.*", extension="*.pyd")

    assert file1.exists()
    assert file2.exists()
    assert any("No *.pyd files with '^test_.*' filter found" in r.message for r in caplog.records)


def test_clean_by_extensions_error_handling(mock_src_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that errors during file removal are logged."""
    file1 = mock_src_path / "module1.pyd"
    file1.touch()

    with patch("pathlib.Path.unlink", side_effect=OSError("Mocked error")), caplog.at_level(logging.WARNING):
        clean_by_extensions(mock_src_path, regex=None, extension="*.pyd")

    assert any("Error removing" in r.message and "Mocked error" in r.message for r in caplog.records)
