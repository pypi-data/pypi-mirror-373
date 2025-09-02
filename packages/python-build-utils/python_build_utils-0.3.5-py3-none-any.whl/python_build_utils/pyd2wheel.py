"""Convert compiled .pyd files into valid Python wheel (.whl) files."""

import hashlib
import logging
import re
import shutil
from pathlib import Path

import click

from .exceptions import PydFileFormatError, PydFileSuffixError, VersionNotFoundError


logger = logging.getLogger(__name__)


@click.command(name="pyd2wheel", help="Create a Python wheel file from a compiled .pyd file.")
@click.argument("pyd_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--package-version",
    help="Version of the package. If not provided, the version is extracted from the file name.",
    default=None,
)
@click.option(
    "--abi-tag",
    help="ABI tag for the wheel. Defaults to 'none'.",
    default=None,
)
def pyd2wheel(
    pyd_file: Path,
    package_version: str | None = None,
    abi_tag: str | None = None,
) -> Path | None:
    """CLI entrypoint to convert a .pyd file into a Python wheel."""
    logger.info("Converting %s to wheel...", pyd_file)
    return convert_pyd_to_wheel(pyd_file, package_version, abi_tag)


def convert_pyd_to_wheel(
    pyd_file: Path,
    package_version: str | None = None,
    abi_tag: str | None = None,
) -> Path | None:
    """Convert a .pyd file into a valid Python wheel."""
    try:
        name, version_from_filename, py_tag, platform = _extract_pyd_file_info(pyd_file)
    except (PydFileFormatError, PydFileSuffixError):
        logger.exception("Error extracting metadata")
        return None

    try:
        package_version = _get_package_version(package_version, version_from_filename)
    except VersionNotFoundError:
        logger.exception("Version extraction failed")
        return None

    abi_tag = abi_tag or "none"

    logger.info("=" * 80)
    logger.info("Wheel Metadata:\n%s", _get_wheel_info(name, package_version, py_tag, platform, abi_tag))
    logger.info("=" * 80)

    wheel_name = f"{name}-{package_version}-{py_tag}-{abi_tag}-{platform}.whl"
    temp_root = create_temp_directory(pyd_file)
    dist_info = create_dist_info_directory(temp_root, name, package_version)

    _create_metadata_file(dist_info, name, package_version)
    _create_wheel_file(dist_info, py_tag, abi_tag, platform)
    _create_record_file(temp_root, dist_info)

    wheel_path = _create_wheel_archive(pyd_file, wheel_name, temp_root)
    logger.info("✅ Created wheel file: %s", wheel_path)

    shutil.rmtree(temp_root)
    return wheel_path


def _extract_pyd_file_info(pyd_file: Path) -> tuple[str, str | None, str, str]:
    """Extract metadata from .pyd filename."""
    if pyd_file.suffix != ".pyd":
        raise PydFileSuffixError(pyd_file.name)

    stem = pyd_file.stem

    match = re.match(r"(.*?)-((?:\d\.){0,2}\d)[.-](.*)-(.*)", stem)
    if match:
        return match.groups()[0], match.groups()[1], match.groups()[2], match.groups()[3]

    match = re.match(r"(.*?)\.(.*)-(.*)", stem)
    if match:
        return match.groups()[0], None, match.groups()[1], match.groups()[2]

    raise PydFileFormatError(stem)


def _get_package_version(version: str | None, fallback: str | None) -> str:
    """Determine package version from CLI or filename."""
    if version:
        return version
    if fallback:
        return fallback
    raise VersionNotFoundError


def _get_wheel_info(name: str, version: str, py_tag: str, platform: str, abi_tag: str) -> str:
    """Return formatted wheel metadata."""
    lines = [
        f"{'Field':<25}Value",
        "-" * 80,
        f"{'Name:':<25}{name}",
        f"{'Version:':<25}{version}",
        f"{'Python Version:':<25}{py_tag}",
        f"{'Platform:':<25}{platform}",
        f"{'ABI Tag:':<25}{abi_tag}",
        "-" * 80,
    ]
    return "\n".join(lines)


def create_temp_directory(pyd_file: Path) -> Path:
    """Create temp directory and copy the .pyd file there."""
    temp = pyd_file.parent / "wheel_temp"
    temp.mkdir(exist_ok=True)
    shutil.copy(pyd_file, temp / pyd_file.name)
    return temp


def create_dist_info_directory(root: Path, name: str, version: str) -> Path:
    """Create .dist-info directory under temp root."""
    dist_info = root / f"{name}-{version}.dist-info"
    dist_info.mkdir(exist_ok=True)
    return dist_info


def _create_metadata_file(dist_info: Path, name: str, version: str) -> None:
    """Write METADATA file."""
    content = f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
    dist_info.joinpath("METADATA").write_text(content, encoding="utf-8")


def _create_wheel_file(dist_info: Path, py_tag: str, abi_tag: str, platform: str) -> None:
    """Write WHEEL file."""
    content = (
        "Wheel-Version: 1.0\n"
        "Generator: bdist_wheel 1.0\n"
        "Root-Is-Purelib: false\n"
        f"Tag: {py_tag}-{abi_tag}-{platform}\n"
        "Build: 1"
    )
    dist_info.joinpath("WHEEL").write_text(content, encoding="utf-8")


def _create_record_file(root: Path, dist_info: Path) -> None:
    """Write RECORD file listing all files in the wheel."""
    lines: list[str] = []
    for file in root.rglob("*"):
        if file.is_file():
            sha256 = hashlib.sha256()
            with file.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            digest = sha256.hexdigest()
            size = file.stat().st_size
            rel_path = file.relative_to(root).as_posix()
            lines.append(f"{rel_path},sha256={digest},{size}")
    rel_record = dist_info.relative_to(root).joinpath("RECORD").as_posix()
    lines.append(f"{rel_record},,")
    dist_info.joinpath("RECORD").write_text("\n".join(lines), encoding="utf-8")


def _create_wheel_archive(pyd_file: Path, wheel_name: str, root: Path) -> Path:
    """Zip temp directory into final .whl file."""
    wheel_path = pyd_file.parent / wheel_name
    zip_path = wheel_path.with_suffix(".zip")

    if zip_path.exists():
        zip_path.unlink()

    created = shutil.make_archive(str(wheel_path), "zip", root)

    if wheel_path.exists():
        wheel_path.unlink()

    Path(created).rename(wheel_path)
    return wheel_path
