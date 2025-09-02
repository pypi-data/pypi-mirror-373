"""CLI tool to clean up compiled build modules from a Python src directory.

This tool scans a specified source path and removes compiled artifacts:
- Windows: `.pyd`
- Linux/Unix: `.so`
- Generated C sources: `.c`

An optional regex filter can be used to restrict which files are removed.
"""

import logging
import re
from pathlib import Path

import click

from .constants import PYD_EXTENSION, SO_EXTENSION


logger = logging.getLogger(__name__)


@click.command(
    name="clean-pyd-modules",
    help="Clean all compiled modules (.pyd/.so) and generated C files (.c) in the given src path.",
)
@click.option(
    "--src-path",
    default="src",
    help="Path to the src folder to scan for compiled modules. Defaults to 'src' in the current folder.",
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter files by name (matched against relative paths).",
)
def clean_pyd_modules(src_path: str | None = None, regex: str | None = None) -> None:
    """Remove compiled modules (.pyd/.so) and generated C files (.c) in a given source path, optionally filtered by a regex."""
    clean_cython_build_artifacts(src_path=src_path, regex=regex)


def clean_cython_build_artifacts(src_path: str | None = None, regex: str | None = None) -> None:
    """Clean all compiled artifacts from the given source path."""
    resolved_src = _get_src_path(src_path)

    if resolved_src is None:
        logger.error("Could not locate source path: %s", src_path)
        return

    # Remove platform-specific compiled modules and generated C sources
    for extension in (f"*{PYD_EXTENSION}", f"*{SO_EXTENSION}", "*.c"):
        logger.info("Cleaning %s files with regex='%s' in '%s'...", extension, regex, resolved_src)
        clean_by_extensions(src_path=resolved_src, regex=regex, extension=extension)


def _get_src_path(src_path: str | None = None) -> Path | None:
    """Resolve the source directory path."""
    if src_path:
        path = Path(src_path).resolve()
        if not path.exists() or not path.is_dir():
            logger.error("Path '%s' does not exist or is not a directory.", path)
            return None
        return path
    return Path("src").resolve()


def clean_by_extensions(src_path: Path, regex: str | None, extension: str) -> None:
    """Remove files with the specified extension from the source directory."""
    file_candidates = list(src_path.rglob(extension))

    if not file_candidates:
        logger.info("No %s files found in %s.", extension, src_path)
        return

    deleted_any = False

    for file_path in file_candidates:
        relative_path = file_path.relative_to(src_path).as_posix()
        if regex and not re.search(regex, relative_path, re.IGNORECASE):
            continue

        logger.info("Removing %s", file_path)
        try:
            file_path.unlink()
        except OSError as e:
            logger.warning("Error removing %s: %s", file_path, e)
        else:
            deleted_any = True

    if not deleted_any:
        logger.info("No %s files with '%s' filter found in %s", extension, regex, src_path)
