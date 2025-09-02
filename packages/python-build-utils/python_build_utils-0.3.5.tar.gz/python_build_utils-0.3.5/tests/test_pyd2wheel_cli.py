"""Tests for the `pyd2wheel` CLI command from `python_build_utils.pyd2wheel`."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.pyd2wheel import pyd2wheel


@pytest.fixture
def setup_wheel_files(tmp_path: Path) -> callable:
    """Create a dummy .pyd file for testing.

    Args:
    ----
        tmp_path: Temporary directory provided by pytest.

    Returns:
    -------
        Callable[[str], str]: Function that creates a file and returns its path.

    """

    def _create_pyd_file(dummy_file_name: str) -> str:
        pyd_file_path = tmp_path / dummy_file_name
        pyd_file_path.write_text('print("hello")', encoding="utf-8")
        return str(pyd_file_path)

    return _create_pyd_file


@pytest.mark.parametrize(
    "dummy_file_name",
    [
        "DAVEcore.cp310-win_amd64.pyd",
        "dummy-0.1.0-py311-win_amd64.pyd",
        "dummy2-1.0-py311-win_amd64.pyd",
        "dummy3-1-py311-win_amd64.pyd",
    ],
)
def test_cli_make_wheels(setup_wheel_files: callable, dummy_file_name: str) -> None:
    """Run pyd2wheel CLI on various filename formats.

    Args:
    ----
        setup_wheel_files: Factory fixture for creating a .pyd file.
        dummy_file_name: Name of the dummy file to test.

    """
    pyd_file_path = setup_wheel_files(dummy_file_name)

    runner = CliRunner()
    result = runner.invoke(pyd2wheel, [pyd_file_path, "--package-version=1.2.3"])

    assert result.exit_code == 0
