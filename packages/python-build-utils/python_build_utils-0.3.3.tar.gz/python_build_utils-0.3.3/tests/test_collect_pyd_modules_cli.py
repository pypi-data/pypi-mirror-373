"""CLI tests for `python_build_utils.collect_pyd_modules`.

Covers scenarios like:
- Default module collection
- Regex filtering
- Collection of `.py` modules
- Writing to output file
- Handling of invalid or missing site-packages path
"""

import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import collect_pyd_modules


logger = logging.getLogger("python_build_utils.collect_pyd_modules")
logger.setLevel(logging.INFO)


@pytest.fixture
def mock_venv_structure(tmp_path: Path) -> Path:
    """Create a mock venv directory structure with site-packages and files.

    Args:
        tmp_path: Temporary directory for the mock venv.

    Returns:
        Path: Root path of the mock venv.

    """
    site_packages = tmp_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    (site_packages / "pkg").mkdir()
    (site_packages / "pkg" / "mod1.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "subpkg").mkdir()
    (site_packages / "pkg" / "subpkg" / "mod2.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "__init__.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "altmod.py").touch()

    return tmp_path


def test_collect_pyd_modules_default(mock_venv_structure: Path) -> None:
    """Collect .pyd modules from the mock environment using default options."""
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure)])

    assert result.exit_code == 0
    output = result.output.strip().splitlines()
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
    """Collect .py modules instead of .pyd when --collect-py is used."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--collect-py"],
    )

    assert result.exit_code == 0
    output = result.output
    assert "pkg.altmod" in output
    assert "mod1" not in output


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
    assert any("Could not locate site-packages" in r.message for r in caplog.records)


def test_collect_pyd_modules_invalid_path(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Gracefully handle nonexistent venv-path argument."""
    invalid_path = tmp_path / "does_not_exist"
    runner = CliRunner()

    with caplog.at_level("ERROR"):
        result = runner.invoke(collect_pyd_modules, ["--venv-path", str(invalid_path)])

    assert result.exit_code == 0
    assert any("does not exist" in record.message for record in caplog.records)


def test_collect_pyd_modules_no_matches(mock_venv_structure: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Log and return None when no modules match regex or extension."""
    runner = CliRunner()

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
    """Test that '__init__.cp311-win_amd64.pyd' is correctly normalized to package name."""
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

    from click.testing import CliRunner

    from python_build_utils.collect_pyd_modules import collect_pyd_modules

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
