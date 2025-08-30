"""Remove .tar.gz source distribution files from a build directory."""

import logging
from pathlib import Path

import click


logger = logging.getLogger(__name__)


@click.command(name="remove-tarballs", help="Remove .tar.gz files from the given dist directory.")
@click.option(
    "--dist-dir",
    default="dist",
    help="Directory containing the .tar.gz files. Defaults to 'dist'.",
)
def remove_tarballs(dist_dir: str) -> None:
    """Remove all .tar.gz source distribution files from the specified directory."""
    dist_path = Path(dist_dir.rstrip("/"))
    tarball_paths = list(dist_path.glob("*.tar.gz"))

    if not tarball_paths:
        logger.info("No .tar.gz files found in '%s'.", dist_path)
        return

    for path in tarball_paths:
        try:
            path.unlink()
        except FileNotFoundError:  # noqa: PERF203
            logger.warning("File not found: %s", path)
        except OSError:
            logger.exception("Error removing file: %s", path)
        else:
            logger.info("🗑️ Removed: %s", path)
