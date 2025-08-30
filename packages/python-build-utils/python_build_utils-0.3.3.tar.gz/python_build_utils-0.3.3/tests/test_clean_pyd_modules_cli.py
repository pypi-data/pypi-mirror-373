"""CLI tests for the clean_pyd_modules tool in python_build_utils.

Covers:
- No files to clean
- File removal behavior
- Regex filtering
- Invalid path handling
"""

import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.clean_pyd_modules import clean_pyd_modules


logger = logging.getLogger("python_build_utils.clean_pyd_modules")
logger.setLevel(logging.INFO)


def test_clean_pyd_modules_no_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test behavior when no .pyd or .c files are present."""
    runner = CliRunner()
    with caplog.at_level("INFO"):
        result = runner.invoke(clean_pyd_modules, ["--src-path", str(tmp_path)])
    assert result.exit_code == 0
    assert any("No *.pyd files found" in r.message for r in caplog.records)
    assert any("No *.c files found" in r.message for r in caplog.records)


def test_clean_pyd_modules_removes_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that .pyd and .c files are removed as expected."""
    file1 = tmp_path / "test1.pyd"
    file2 = tmp_path / "test2.c"
    file1.write_text("dummy")
    file2.write_text("dummy")

    runner = CliRunner()
    with caplog.at_level("INFO"):
        result = runner.invoke(clean_pyd_modules, ["--src-path", str(tmp_path)])

    assert result.exit_code == 0
    assert not file1.exists()
    assert not file2.exists()
    assert any("Removing" in r.message for r in caplog.records)


def test_clean_pyd_modules_with_regex(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that regex filtering only removes matching .pyd files."""
    (tmp_path / "match_this.pyd").write_text("dummy")
    (tmp_path / "skip_this.pyd").write_text("dummy")

    runner = CliRunner()
    with caplog.at_level("INFO"):
        result = runner.invoke(clean_pyd_modules, ["--src-path", str(tmp_path), "--regex", "match_"])

    assert result.exit_code == 0
    assert (tmp_path / "skip_this.pyd").exists()
    assert not (tmp_path / "match_this.pyd").exists()
    assert any("Removing" in r.message for r in caplog.records)


def test_clean_pyd_modules_invalid_path(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test behavior when an invalid src-path is provided."""
    bad_path = tmp_path / "nonexistent"
    runner = CliRunner()
    with caplog.at_level("ERROR"):
        result = runner.invoke(clean_pyd_modules, ["--src-path", str(bad_path)])
    assert result.exit_code == 0
    assert any("does not exist or is not a directory" in r.message for r in caplog.records)
