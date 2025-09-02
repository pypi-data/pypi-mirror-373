"""Command-line interface (CLI) for Python build utilities.

This module uses the `click` library to create a CLI group with commands for
renaming wheel files and removing tarballs.

Functions:
    cli(): CLI entrypoint that registers available commands.

Commands:
    rename_wheel_files: Rename wheel files to match a standardized format.
    remove_tarballs: Remove `.tar.gz` source distributions from the current directory.
"""

import logging

import click

from . import __version__
from .clean_pyd_modules import clean_pyd_modules
from .cli_logger import initialize_logging
from .collect_dep_modules import collect_dependencies
from .collect_pyd_modules import collect_pyd_modules
from .constants import LOGLEVEL_DEBUG, LOGLEVEL_DEFAULT, LOGLEVEL_INFO, VERBOSITY_DEBUG, VERBOSITY_INFO
from .pyd2wheel import pyd2wheel
from .remove_tarballs import remove_tarballs
from .rename_wheel_files import rename_wheel_files


logger = initialize_logging()


@click.group(help="Register CLI tools for Python build utilities.", invoke_without_command=True)
@click.version_option(
    __version__,
    "--version",
    message="Version: %(version)s",
    help="Show the version and exit.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity level. Use -v for info, -vv for debug.",
)
def cli(verbose: int) -> None:
    """Register CLI tools for Python build utilities.

    This function is the entrypoint for the CLI. It adjusts the logging level based
    on verbosity flags and registers all available subcommands.
    """
    if verbose >= VERBOSITY_DEBUG:
        log_level = LOGLEVEL_DEBUG
    elif verbose == VERBOSITY_INFO:
        log_level = LOGLEVEL_INFO
    else:
        log_level = LOGLEVEL_DEFAULT

    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)

    if log_level <= logging.INFO:
        logger.info(
            "🚀 Python Build Utilities CLI — ready to build, package, and manage your Python projects.",
        )


# Register all subcommands
cli.add_command(pyd2wheel)
cli.add_command(collect_pyd_modules)
cli.add_command(clean_pyd_modules)
cli.add_command(collect_dependencies)
cli.add_command(rename_wheel_files)
cli.add_command(remove_tarballs)

# Aka with a different name without duplication
collect_compiled_modules = collect_pyd_modules
collect_compiled_modules.name = "collect-compiled-modules"
cli.add_command(collect_compiled_modules)


if __name__ == "__main__":
    cli()
