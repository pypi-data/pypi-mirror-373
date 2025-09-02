"""Tests for functions in `python_build_utils.pyd2wheel`."""

from pathlib import Path

import pytest

from python_build_utils.pyd2wheel import (
    PydFileFormatError,
    PydFileSuffixError,
    VersionNotFoundError,
    _extract_pyd_file_info,
    _get_package_version,
    convert_pyd_to_wheel,
)


def test_extract_pyd_file_info_long_format() -> None:
    """Test `_extract_pyd_file_info` with long filename format."""
    pyd_file = Path("dummy-0.1.0-py311-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)

    assert name == "dummy"
    assert package_version == "0.1.0"
    assert python_version == "py311"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_short_format() -> None:
    """Test `_extract_pyd_file_info` with short filename format."""
    pyd_file = Path("DAVEcore.cp310-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)

    assert name == "DAVEcore"
    assert package_version is None
    assert python_version == "cp310"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_invalid_format() -> None:
    """Ensure `_extract_pyd_file_info` raises error on invalid format."""
    pyd_file = Path("invalid_format.pyd")

    with pytest.raises(PydFileFormatError):
        _extract_pyd_file_info(pyd_file)


def test_extract_pyd_file_info_invalid_suffix() -> None:
    """Ensure `_extract_pyd_file_info` raises error on invalid suffix."""
    pyd_file = Path("DAVEcore.cp310-win_amd64.whl")

    with pytest.raises(PydFileSuffixError):
        _extract_pyd_file_info(pyd_file)


def test_get_package_version_from_filename() -> None:
    """Check `_get_package_version` extracts version from filename."""
    version = _get_package_version(None, "0.1.0")

    assert version == "0.1.0"


def test_get_package_version_provided() -> None:
    """Check `_get_package_version` uses explicitly provided version."""
    version = _get_package_version("0.2.0", None)

    assert version == "0.2.0"


def test_get_package_version_error() -> None:
    """Ensure `_get_package_version` raises error when no version provided."""
    with pytest.raises(VersionNotFoundError):
        _get_package_version(None, None)


def test_convert_pyd_to_wheel(tmp_path: Path) -> None:
    """Test conversion of .pyd file to .whl file."""
    pyd_file = tmp_path / "dummy-0.1.0-py311-win_amd64.pyd"
    pyd_file.touch()

    wheel_file = convert_pyd_to_wheel(pyd_file)

    assert wheel_file.exists()
    assert wheel_file.suffix == ".whl"
