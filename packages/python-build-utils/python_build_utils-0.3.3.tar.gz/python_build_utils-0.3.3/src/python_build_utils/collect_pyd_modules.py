"""Collect .pyd or .py submodules from a virtual environment."""

import logging
import os
import re
import sys
from pathlib import Path

import click


logger = logging.getLogger(__name__)


@click.command(
    name="collect-pyd-modules",
    help="Collect and display .pyd or .py submodules from a virtual environment.",
)
@click.option(
    "--venv-path",
    default=None,
    help="Path to the virtual environment to scan for modules. Defaults to the current environment.",
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter module names.",
)
@click.option(
    "--collect-py",
    is_flag=True,
    default=False,
    help="If set, collect .py files instead of .pyd files.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    help="Optional file path to write the list of found modules.",
)
def collect_pyd_modules(
    venv_path: str | None = None,
    regex: str | None = None,
    *,
    collect_py: bool = False,
    output: str | None = None,
) -> list[str] | None:
    """Collect and optionally write `.pyd` or `.py` submodules from a virtual environment."""
    venv_site_packages = _get_venv_site_packages(venv_path)

    if venv_site_packages is None:
        logger.error("Could not locate site-packages in the specified environment.")
        return None

    logger.info("Collecting %s modules in '%s'...", ".py" if collect_py else ".pyd", venv_site_packages)

    found_modules = _find_modules_in_site_packages(
        venv_site_packages=venv_site_packages,
        regex=regex,
        collect_py=collect_py,
    )

    if not found_modules:
        logger.info("No matching modules found.")
        return None

    click.echo("\n".join(found_modules))
    logger.info("Found %d modules.", len(found_modules))

    if output:
        output_path = Path(output)
        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(found_modules))
        click.echo(f"Module list written to {output_path}")

    return found_modules


def collect_pyd_modules_from_venv(
    venv_path: str | None = None,
    regex: str | None = None,
    *,
    collect_py: bool = False,
) -> list[str]:
    """Collect `.pyd` or `.py` submodules from the given virtual environment."""
    venv_site_packages = _get_venv_site_packages(venv_path)

    if venv_site_packages is None:
        msg = f"Could not locate site-packages in the specified environment: {venv_path}"
        logger.error(msg)
        raise ValueError(msg)

    return _find_modules_in_site_packages(
        venv_site_packages=venv_site_packages,
        regex=regex,
        collect_py=collect_py,
    )


def _get_venv_site_packages(venv_path: str | None = None) -> Path | None:
    """Get the site-packages directory from the given or current virtual environment."""
    if venv_path:
        venv = Path(venv_path).resolve()
        if not venv.exists() or not venv.is_dir():
            logger.error("Path '%s' does not exist or is not a directory.", venv)
            return None
        return venv / "Lib" / "site-packages"
    return next((Path(p) for p in sys.path if "site-packages" in p), None)


def _find_modules_in_site_packages(
    venv_site_packages: Path,
    regex: str | None = None,
    *,
    collect_py: bool = False,
) -> list[str]:
    """Find all submodules in site-packages matching the file extension and optional regex."""
    extension = ".py" if collect_py else ".pyd"
    files = list(venv_site_packages.rglob(f"*{extension}"))

    submodules: set[str] = set()

    for file in files:
        module_name = _extract_submodule_name(file, venv_site_packages)

        if regex and not re.search(regex, module_name, re.IGNORECASE):
            continue

        submodules.add(module_name)

    return sorted(submodules)


def _extract_submodule_name(module_file: Path, venv_site_packages: Path) -> str:
    """Convert a file path to a dotted submodule name, normalized for .py/.pyd endings."""
    relative_path = module_file.relative_to(venv_site_packages)
    module_name = re.sub(r"\.cp\d+.*\.(pyd|py)$", "", str(relative_path))

    # Remove the suffix .pyd if it exists
    module_name = re.sub(r"\.(pyd|py)$", "", module_name)

    # Convert the path to a dotted module name
    module_name = module_name.replace(os.sep, ".")

    if module_name.endswith(".__init__"):
        module_name = re.sub(r"\.__init__$", "", module_name)

    return module_name
