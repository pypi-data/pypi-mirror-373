"""Unit tests for the CLI behavior of `python_build_utils.cli_tools`.

Tests:
- CLI entrypoint help and version options
- Verbose logging flag behavior (-v, -vv)
"""

import logging
from typing import Any

from click.testing import CliRunner

from python_build_utils.cli_tools import cli


def test_cli_help() -> None:
    """Check that the help message displays correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Register CLI tools for Python build utilities." in result.output


def test_cli_version() -> None:
    """Check that the version output is shown correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Version: " in result.output


def test_cli_verbose_levels(monkeypatch: Any) -> None:
    """Verify that verbose flags (-v, -vv) adjust logger levels appropriately."""
    runner = CliRunner()

    import python_build_utils.cli_tools as mod

    test_logger = logging.getLogger("test_logger")
    monkeypatch.setattr(mod, "logger", test_logger)

    result = runner.invoke(mod.cli, ["-v"])
    assert result.exit_code == 0
    assert test_logger.level == logging.INFO

    result = runner.invoke(mod.cli, ["-vv"])
    assert result.exit_code == 0
    assert test_logger.level == logging.DEBUG

    result = runner.invoke(mod.cli, [])
    assert result.exit_code == 0
    assert test_logger.level == logging.WARNING
