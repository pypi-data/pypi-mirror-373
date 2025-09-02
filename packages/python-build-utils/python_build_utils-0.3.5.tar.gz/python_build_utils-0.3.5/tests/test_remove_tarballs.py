"""Tests for `remove_tarballs` function from `python_build_utils.remove_tarballs`."""

import logging
from pathlib import Path
from typing import NoReturn

import pytest
from click.testing import CliRunner

from python_build_utils.remove_tarballs import remove_tarballs


logger = logging.getLogger("python_build_utils.remove_tarballs")
logger.setLevel(logging.INFO)


@pytest.fixture
def setup_test_environment(tmp_path: Path) -> Path:
    """Create a temporary dist directory with a dummy tarball file.

    Args:
    ----
        tmp_path: Temporary directory path provided by pytest.

    Returns:
    -------
        Path: Path to the created 'dist' directory containing a dummy tarball.

    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_file = dist_dir / "test.tar.gz"
    tarball_file.write_text("dummy content")
    return dist_dir


def test_remove_tarballs(setup_test_environment: Path) -> None:
    """Test that `remove_tarballs` successfully removes existing tarball files.

    Args:
    ----
        setup_test_environment: Fixture providing a directory with a dummy tarball.

    """
    dist_dir = setup_test_environment
    runner = CliRunner()

    assert list(dist_dir.glob("*.tar.gz"))

    result = runner.invoke(remove_tarballs, ["--dist-dir", str(dist_dir)])

    assert result.exit_code == 0
    assert not list(dist_dir.glob("*.tar.gz"))


def test_remove_tarballs_no_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test `remove_tarballs` behavior when no tarball files are present."""
    from python_build_utils.remove_tarballs import remove_tarballs  # zorg dat deze import correct is

    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(remove_tarballs, ["--dist-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert any("No .tar.gz files found" in r.message for r in caplog.records)


# Voor test_remove_tarballs_file_not_found
def test_remove_tarballs_file_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test dat een FileNotFoundError netjes wordt gelogd."""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_path = dist_dir / "ghost.tar.gz"
    tarball_path.write_text("dummy content")
    tarball_path.unlink()

    def fake_glob(self: Path, pattern: str) -> list[Path]:
        return [tarball_path]

    monkeypatch.setattr(Path, "glob", fake_glob)

    runner = CliRunner()
    with caplog.at_level(logging.WARNING):
        result = runner.invoke(remove_tarballs, ["--dist-dir", str(dist_dir)])

    assert result.exit_code == 0
    assert any("File not found" in r.message for r in caplog.records)


# Voor test_remove_tarballs_oserror
def test_remove_tarballs_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test dat een OSError netjes wordt gelogd met een traceback."""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_path = dist_dir / "unremovable.tar.gz"
    tarball_path.write_text("dummy content")

    def fake_glob(self: Path, pattern: str) -> list[Path]:
        return [tarball_path]

    error_message = "Permission denied"

    def fake_unlink(self: Path) -> NoReturn:
        raise OSError(error_message)

    monkeypatch.setattr(Path, "glob", fake_glob)
    monkeypatch.setattr(Path, "unlink", fake_unlink)

    runner = CliRunner()
    with caplog.at_level(logging.ERROR):
        result = runner.invoke(remove_tarballs, ["--dist-dir", str(dist_dir)])

    assert result.exit_code == 0
    assert any("Error removing file" in r.message for r in caplog.records)
