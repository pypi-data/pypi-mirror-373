"""Tests for internal functions of `collect_pyd_modules` from `python_build_utils`.

Includes tests for collecting `.pyd` files, filtering via regex, handling nested directories,
platform-specific suffix stripping, and resolving site-packages paths.
"""

import sys
from pathlib import Path

import pytest

from python_build_utils.collect_pyd_modules import (
    _find_modules_in_site_packages,
    _get_venv_site_packages,
)


@pytest.fixture
def mock_venv_site_packages(tmp_path: Path) -> Path:
    """Create a mock site-packages directory for testing.

    Args:
    ----
        tmp_path: Temporary test directory provided by pytest.

    Returns:
    -------
        Path: Path to the created mock site-packages.

    """
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    return site_packages


def test_collect_all_pyd_modules_no_files(mock_venv_site_packages: Path) -> None:
    """Return empty list when no .pyd files are present."""
    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_files(mock_venv_site_packages: Path) -> None:
    """Collect .pyd files from top-level and nested directories."""
    (mock_venv_site_packages / "module1.pyd").touch()
    nested = mock_venv_site_packages / "subdir"
    nested.mkdir()
    (nested / "module2.pyd").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert "module1" in result
    assert "subdir.module2" in result


def test_collect_all_pyd_modules_with_regex(mock_venv_site_packages: Path) -> None:
    """Filter collected .pyd files using a regex."""
    (mock_venv_site_packages / "module1.pyd").touch()
    (mock_venv_site_packages / "module2.pyd").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages, regex=r"module1")
    assert "module1" in result
    assert "module2" not in result


def test_collect_all_pyd_modules_remove_init(mock_venv_site_packages: Path) -> None:
    """Convert '__init__.pyd' files to their parent package name."""
    path = mock_venv_site_packages / "package" / "__init__.pyd"
    path.parent.mkdir(parents=True)
    path.touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert "package" in result


def test_collect_all_pyd_modules_invalid_path() -> None:
    """Return empty list for invalid site-packages path."""
    result = _find_modules_in_site_packages(Path("/invalid/path/to/site-packages"))
    assert result == []


def test_collect_all_pyd_modules_case_insensitive_regex(mock_venv_site_packages: Path) -> None:
    """Support case-insensitive regex filtering."""
    (mock_venv_site_packages / "Module1.pyd").touch()
    (mock_venv_site_packages / "module2.pyd").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages, regex=r"(?i)module1")
    assert "Module1" in result
    assert "module2" not in result


def test_collect_all_pyd_modules_nested_directories(mock_venv_site_packages: Path) -> None:
    """Detect .pyd files in deeply nested packages."""
    nested = mock_venv_site_packages / "package" / "subpackage"
    nested.mkdir(parents=True)
    (nested / "module.pyd").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert "package.subpackage.module" in result


def test_collect_all_pyd_modules_no_pyd_extension(mock_venv_site_packages: Path) -> None:
    """Ignore files without .pyd extension."""
    (mock_venv_site_packages / "module1.txt").touch()
    (mock_venv_site_packages / "module2.py").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_platform_specific_suffix(mock_venv_site_packages: Path) -> None:
    """Strip platform-specific suffixes from module names."""
    (mock_venv_site_packages / "module1.cp310-win_amd64.pyd").touch()
    (mock_venv_site_packages / "module2.cp39-win_amd64.pyd").touch()

    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert "module1" in result
    assert "module2" in result


def test_collect_all_pyd_modules_empty_directory(mock_venv_site_packages: Path) -> None:
    """Return empty list when directory is empty."""
    result = _find_modules_in_site_packages(mock_venv_site_packages)
    assert result == []


def test_get_venv_site_packages_valid_path(tmp_path: Path) -> None:
    """Return correct site-packages path for a valid venv path."""
    venv_path = tmp_path / "venv"
    site_packages = venv_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    result = _get_venv_site_packages(str(venv_path))
    assert result == site_packages


def test_get_venv_site_packages_invalid_path() -> None:
    """Return None when venv path is invalid."""
    result = _get_venv_site_packages("/invalid/venv/path")
    assert result is None


def test_get_venv_site_packages_none_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Return site-packages path when no venv path is provided."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir(parents=True)

    monkeypatch.setattr(sys, "path", [str(site_packages)])
    result = _get_venv_site_packages()
    assert result == site_packages


def test_get_venv_site_packages_no_site_packages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return None when no site-packages path is found in sys.path."""
    monkeypatch.setattr(sys, "path", ["/some/random/path"])
    result = _get_venv_site_packages()
    assert result is None


def test_extract_submodule_name_strips_init(tmp_path: Path) -> None:
    """Ensure .__init__ suffix is removed correctly from dotted name."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    pkg_dir = site_packages / "mypkg"
    pkg_dir.mkdir()
    file = pkg_dir / "__init__.pyd"
    file.touch()

    from python_build_utils.collect_pyd_modules import _extract_submodule_name

    result = _extract_submodule_name(file, site_packages)
    assert result == "mypkg"


def test_extract_submodule_name_with_suffix_and_init(tmp_path: Path) -> None:
    """Ensure __init__ with platform suffix is correctly normalized."""
    site_packages = tmp_path / "site-packages"
    pkg_dir = site_packages / "mymodule"
    pkg_dir.mkdir(parents=True)
    file = pkg_dir / "__init__.cp311-win_amd64.pyd"
    file.touch()

    from python_build_utils.collect_pyd_modules import _extract_submodule_name

    result = _extract_submodule_name(file, site_packages)

    assert result == "mymodule"


def test_extract_submodule_name_with_platform_suffix_and_init(tmp_path: Path) -> None:
    """Test that '__init__.cpXXX.pyd' is correctly normalized to package name."""
    site_packages = tmp_path / "site-packages"
    package_dir = site_packages / "my_package"
    package_dir.mkdir(parents=True)
    init_file = package_dir / "__init__.cp311-win_amd64.pyd"
    init_file.touch()

    from python_build_utils.collect_pyd_modules import _extract_submodule_name

    result = _extract_submodule_name(init_file, site_packages)

    assert result == "my_package"
