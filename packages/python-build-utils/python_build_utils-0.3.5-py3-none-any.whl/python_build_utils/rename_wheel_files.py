"""Rename wheel files to include platform and Python version tags."""

import logging
import sys
import sysconfig
from pathlib import Path

import click


logger = logging.getLogger(__name__)


@click.command(
    name="rename-wheel-files",
    help="Rename wheel files by replacing 'py3-none-any' with a custom wheel tag.",
)
@click.option(
    "--dist-dir",
    default="dist",
    help="Directory containing the wheel files. Defaults to 'dist'.",
)
@click.option(
    "--python-version-tag",
    default=None,
    help="Python version tag (e.g. cp310). Defaults to current Python version.",
)
@click.option(
    "--platform-tag",
    default=None,
    help="Platform tag (e.g. win_amd64). Defaults to current platform.",
)
@click.option(
    "--wheel-tag",
    default=None,
    help="Full custom wheel tag (e.g. cp310-cp310-win_amd64). Overrides other tag options.",
)
def rename_wheel_files(
    dist_dir: str,
    python_version_tag: str | None,
    platform_tag: str | None,
    wheel_tag: str | None,
) -> None:
    """Rename all wheel files in dist-dir with a custom Python/platform tag."""
    dist_path = Path(dist_dir.rstrip("/")).resolve()

    if not dist_path.exists() or not dist_path.is_dir():
        logger.error("Distribution directory '%s' does not exist.", dist_path)
        return

    if wheel_tag:
        new_tag = wheel_tag
    else:
        py_tag = python_version_tag or f"cp{sys.version_info.major}{sys.version_info.minor}"
        plat_tag = platform_tag or sysconfig.get_platform().replace("-", "_")
        new_tag = f"{py_tag}-{py_tag}-{plat_tag}"

    wheel_files = list(dist_path.glob("*py3-none-any.whl"))

    if not wheel_files:
        logger.info("No matching wheel files found in '%s'.", dist_path)
        return

    for wheel_file in wheel_files:
        new_name = wheel_file.name.replace("py3-none-any", new_tag)
        new_path = wheel_file.with_name(new_name)

        try:
            wheel_file.rename(new_path)
            logger.info("📝 Renamed: %s → %s", wheel_file.name, new_path.name)
        except FileExistsError:
            logger.warning("❌ File already exists: %s", new_path)
        except OSError:
            logger.exception("Unexpected error while renaming: %s", wheel_file)
