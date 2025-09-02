"""CLI tests for `python_build_utils.collect_pyd_modules`.

Covers scenarios like:
- Default module collection (.pyd on Windows-like layout)
- Regex filtering
- Collection of `.py` modules
- Collection of `.so` modules (Unix-like layout)
- Writing to output file
- Handling of invalid or missing site-packages path
- Normalization of '__init__' with ABI suffixes
"""

import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import collect_pyd_modules


# Ensure the module logger is chatty enough for caplog in INFO tests
logger = logging.getLogger("python_build_utils.collect_pyd_modules")
logger.setLevel(logging.INFO)


# -------------------------------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------------------------------


@pytest.fixture
def mock_venv_structure(tmp_path: Path) -> Path:
    """Windows-like venv: <venv>/Lib/site-packages with .pyd and .py files."""
    site_packages = tmp_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    (site_packages / "pkg").mkdir()
    (site_packages / "pkg" / "mod1.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "subpkg").mkdir()
    (site_packages / "pkg" / "subpkg" / "mod2.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "__init__.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "altmod.py").touch()

    return tmp_path


@pytest.fixture
def mock_venv_structure_unix(tmp_path: Path) -> Path:
    """Unix-like venv: <venv>/lib/python3.12/site-packages with .so and .py files."""
    site_packages = tmp_path / "lib" / "python3.12" / "site-packages"
    site_packages.mkdir(parents=True)

    (site_packages / "upkg").mkdir()
    (site_packages / "upkg" / "umod1.cpython-312-x86_64-linux-gnu.so").touch()
    (site_packages / "upkg" / "subu").mkdir()
    (site_packages / "upkg" / "subu" / "umod2.cpython-312-x86_64-linux-gnu.so").touch()
    (site_packages / "upkg" / "__init__.cpython-312-x86_64-linux-gnu.so").touch()
    (site_packages / "upkg" / "ualt.py").touch()

    return tmp_path


# -------------------------------------------------------------------------------------------------
# Tests (Windows-like / .pyd)
# -------------------------------------------------------------------------------------------------


def test_collect_pyd_modules_default(mock_venv_structure: Path) -> None:
    """Collect .pyd modules from the mock environment using default options."""
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure)])

    assert result.exit_code == 0
    output = result.output.strip().splitlines()
    # Package __init__ maps to just 'pkg'
    assert "pkg" in output
    assert "pkg.mod1" in output
    assert "pkg.subpkg.mod2" in output


def test_collect_pyd_modules_with_regex(mock_venv_structure: Path) -> None:
    """Collect .pyd modules filtered by a regex expression."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--regex", "subpkg"],
    )

    assert result.exit_code == 0
    output = result.output
    assert "pkg.subpkg.mod2" in output
    assert "pkg.mod1" not in output


def test_collect_pyd_modules_py_mode(mock_venv_structure: Path) -> None:
    """Collect .py modules instead of compiled ones when --collect-py is used."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--collect-py"],
    )

    assert result.exit_code == 0
    output = result.output
    assert "pkg.altmod" in output
    assert "mod1" not in output  # ensure compiled names are not present


def test_collect_pyd_modules_output_file(mock_venv_structure: Path, tmp_path: Path) -> None:
    """Test that collected modules are written to the output file and echoed."""
    output_file = tmp_path / "modules.txt"

    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    contents = output_file.read_text()
    assert "pkg.mod1" in contents
    assert "pkg.subpkg.mod2" in contents
    assert f"Module list written to {output_file}" in result.output


def test_collect_pyd_modules_site_packages_not_found(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Fallback behavior when no site-packages directory is found."""
    monkeypatch.setattr("sys.path", [])

    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(collect_pyd_modules, [])

    assert result.exit_code == 0
    # Should log an error about site-packages not found
    assert any("Could not locate site-packages" in r.message for r in caplog.records)


def test_collect_pyd_modules_invalid_path(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Gracefully handle nonexistent venv-path argument."""
    invalid_path = tmp_path / "does_not_exist"
    runner = CliRunner()

    with caplog.at_level(logging.ERROR):
        result = runner.invoke(collect_pyd_modules, ["--venv-path", str(invalid_path)])

    assert result.exit_code == 0
    assert any("does not exist" in record.message for record in caplog.records)


def test_collect_pyd_modules_no_matches(
    mock_venv_structure: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log and return None when no modules match regex or extension."""
    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(
            collect_pyd_modules,
            ["--venv-path", str(mock_venv_structure), "--collect-py", "--regex", "doesnotmatch"],
        )

    assert result.exit_code == 0

    # Make sure no known module names are printed
    assert "pkg.mod1" not in result.output
    assert "pkg.subpkg.mod2" not in result.output
    assert "pkg.altmod" not in result.output

    # Check that log line about "no matches" is present
    assert any("No matching modules found." in r.message for r in caplog.records)


def test_extract_submodule_name_with_suffix_and_init(tmp_path: Path) -> None:
    """'__init__.cp311-win_amd64.pyd' is normalized to package name."""
    site_packages = tmp_path / "site-packages"
    package_dir = site_packages / "my_package"
    package_dir.mkdir(parents=True)

    init_file = package_dir / "__init__.cp311-win_amd64.pyd"
    init_file.touch()

    from python_build_utils.collect_pyd_modules import _extract_submodule_name

    result = _extract_submodule_name(init_file, site_packages)
    assert result == "my_package"


def test_collect_pyd_modules_output_written_via_cli(tmp_path: Path) -> None:
    """Ensure output file is written and echoed via CLI."""
    site_packages = tmp_path / "Lib" / "site-packages" / "pkg"
    site_packages.mkdir(parents=True)
    (site_packages / "mod.cp311-win_amd64.pyd").touch()

    output_file = tmp_path / "mods.txt"

    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(tmp_path), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    contents = output_file.read_text(encoding="utf-8")
    assert "pkg.mod" in contents
    assert f"Module list written to {output_file}" in result.output


# -------------------------------------------------------------------------------------------------
# Tests (Unix-like / .so)
# -------------------------------------------------------------------------------------------------


def test_collect_so_modules_unix_layout(mock_venv_structure_unix: Path) -> None:
    """Collect .so modules from a Unix-like venv using --ext=so."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure_unix), "--ext=so"],
    )

    assert result.exit_code == 0
    output = result.output.strip().splitlines()

    # __init__ yields just the package name
    assert "upkg" in output
    # regular modules
    assert "upkg.umod1" in output
    assert "upkg.subu.umod2" in output
    # .py should not appear when ext=so
    assert "upkg.ualt" not in output
