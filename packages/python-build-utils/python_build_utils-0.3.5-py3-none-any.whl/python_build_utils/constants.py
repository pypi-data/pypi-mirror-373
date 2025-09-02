"""Project-wide constants for CLI tools and utilities."""

import logging


# ---------------------------------------------------------------------------------------
# Logging & Verbosity
# ---------------------------------------------------------------------------------------

# Verbosity levels passed via CLI (e.g., -v, -vv)
VERBOSITY_INFO = 1
VERBOSITY_DEBUG = 2

# Corresponding logging levels
LOGLEVEL_DEFAULT = logging.WARNING
LOGLEVEL_INFO = logging.INFO
LOGLEVEL_DEBUG = logging.DEBUG


# ---------------------------------------------------------------------------------------
# Exit codes
# ---------------------------------------------------------------------------------------

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_INVALID_USAGE = 2
EXIT_FILE_ERROR = 3
EXIT_DEPENDENCY_ERROR = 4


# ---------------------------------------------------------------------------------------
# File extensions & conventions
# ---------------------------------------------------------------------------------------

WHEEL_EXTENSION = ".whl"
SDIST_EXTENSION = ".tar.gz"
PYD_EXTENSION = ".pyd"
SO_EXTENSION = ".so"
PYTHON_SOURCE_EXTENSIONS = [".py", ".pyi"]
COMPILED_EXTENSIONS = [".pyd", ".so", ".dll", ".dylib"]

PYD_FILE_FORMATS: dict[str, str] = {
    "long": "{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.pyd",
    "short": "{distribution}.{python tag}-{platform tag}.pyd",
}


# ---------------------------------------------------------------------------------------
# __all__ to restrict wildcard imports
# ---------------------------------------------------------------------------------------

__all__ = [
    "COMPILED_EXTENSIONS",
    "EXIT_DEPENDENCY_ERROR",
    "EXIT_FAILURE",
    "EXIT_FILE_ERROR",
    "EXIT_INVALID_USAGE",
    "EXIT_SUCCESS",
    "LOGLEVEL_DEBUG",
    "LOGLEVEL_DEFAULT",
    "LOGLEVEL_INFO",
    "PYD_EXTENSION",
    "PYTHON_SOURCE_EXTENSIONS",
    "SDIST_EXTENSION",
    "VERBOSITY_DEBUG",
    "VERBOSITY_INFO",
    "WHEEL_EXTENSION",
]
