"""Tests for the CLI behavior of python_build_utils.rename_wheel_files.

Covers scenarios like:
- Successful renaming of wheel files
- Handling of missing directories
- FileExistsError and OSError handling
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from python_build_utils.rename_wheel_files import rename_wheel_files


def test_rename_wheel_file_exists(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Log a warning if the target wheel file already exists."""
    wheel_file = tmp_path / "example-1.0.0-py3-none-any.whl"
    wheel_file.touch()

    # Simuleer FileExistsError bij rename
    with patch.object(Path, "rename", side_effect=FileExistsError):
        runner = CliRunner()
        with caplog.at_level("WARNING"):
            result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert any("already exists" in r.message for r in caplog.records)


def test_rename_wheel_oserror(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Log an exception when rename fails with OSError."""
    wheel_file = tmp_path / "example-1.0.0-py3-none-any.whl"
    wheel_file.touch()

    with patch.object(Path, "rename", side_effect=OSError("disk error")):
        runner = CliRunner()
        with caplog.at_level("ERROR"):
            result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert any("Unexpected error while renaming" in r.message for r in caplog.records)
