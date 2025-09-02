"""Tests for the `rename_wheel_files` CLI from `python_build_utils.rename_wheel_files`."""

import logging
import os
import sys
import sysconfig
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import pytest
from click.testing import CliRunner

from python_build_utils.rename_wheel_files import rename_wheel_files


logger = logging.getLogger("python_build_utils.rename_wheel_files")
logger.setLevel(logging.INFO)


@pytest.fixture
def setup_wheel_files(tmp_path: Path) -> Path:
    """Create a temporary directory with a sample wheel file for testing.

    Args:
    ----
        tmp_path: Temporary path provided by pytest.

    Returns:
    -------
        Path: Path to the directory containing the sample wheel file.

    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    wheel_file = dist_dir / "example-1.0.0-py3-none-any.whl"
    wheel_file.touch()
    return dist_dir


@pytest.fixture
def create_dummy_wheel() -> Callable[[Path, str], Path]:
    """Create a factory fixture for dummy wheel files.

    Returns
    -------
        Callable: Function to create dummy wheel files.

    """

    def _create(dist_dir: Path, filename: str) -> Path:
        dist_dir.mkdir(parents=True, exist_ok=True)
        file = dist_dir / filename
        file.write_text("dummy content")
        return file

    return _create


def test_rename_wheel_files_default_tags(setup_wheel_files: Path) -> None:
    """Test renaming wheel files with default Python and platform tags."""
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist-dir={setup_wheel_files}"])

    python_version_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    platform_tag = sysconfig.get_platform().replace("-", "_")
    expected_tag = f"{python_version_tag}-{python_version_tag}-{platform_tag}"

    assert result.exit_code == 0
    assert (setup_wheel_files / f"example-1.0.0-{expected_tag}.whl").exists()


def test_rename_wheel_files_custom_tags(setup_wheel_files: Path) -> None:
    """Test renaming wheel files with custom Python and platform tags."""
    runner = CliRunner()
    result = runner.invoke(
        rename_wheel_files,
        [f"--dist-dir={setup_wheel_files}", "--python-version-tag=cp39", "--platform-tag=win_amd64"],
    )

    expected_tag = "cp39-cp39-win_amd64"

    assert result.exit_code == 0
    assert (setup_wheel_files / f"example-1.0.0-{expected_tag}.whl").exists()


def test_rename_wheel_files_custom_wheel_tag(setup_wheel_files: Path) -> None:
    """Test renaming wheel files with a completely custom wheel tag."""
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist-dir={setup_wheel_files}", "--wheel-tag=custom_tag"])

    expected_tag = "custom_tag"

    assert result.exit_code == 0
    assert (setup_wheel_files / f"example-1.0.0-{expected_tag}.whl").exists()


def test_rename_with_defaults(tmp_path: Path, create_dummy_wheel: Callable[[Path, str], Path]) -> None:
    """Test default renaming behavior."""
    create_dummy_wheel(tmp_path, "package-1.0.0-py3-none-any.whl")

    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])

    pyver = f"cp{sys.version_info.major}{sys.version_info.minor}"
    plat = sysconfig.get_platform().replace("-", "_")
    expected_suffix = f"{pyver}-{pyver}-{plat}.whl"

    assert result.exit_code == 0
    assert any(f.endswith(expected_suffix) for f in os.listdir(tmp_path))


def test_no_matching_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test behavior when no wheel files match the criteria."""
    runner = CliRunner()

    with caplog.at_level(logging.INFO):
        result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert any("No matching wheel files" in record.message for record in caplog.records)


def test_file_exists_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    create_dummy_wheel: Callable[[Path, str], Path],
) -> None:
    """Test behavior when target wheel file already exists."""
    (tmp_path / "example-1.0-custom.whl").touch()
    create_dummy_wheel(tmp_path, "example-1.0-py3-none-any.whl")

    def mock_rename(_: Path, __: Path) -> NoReturn:
        msg = "Mocked"
        raise FileExistsError(msg)

    monkeypatch.setattr("pathlib.Path.rename", mock_rename)

    runner = CliRunner()
    with caplog.at_level(logging.WARNING):  # <-- hier aangepast
        result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path), "--wheel-tag", "custom"])

    assert result.exit_code == 0
    assert any("File already exists" in record.message for record in caplog.records)
