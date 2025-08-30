"""Public API and version retrieval for the python_build_utils package."""

from importlib.metadata import PackageNotFoundError, version

from .collect_dep_modules import collect_package_dependencies
from .collect_pyd_modules import collect_pyd_modules_from_venv


DIST_NAME: str = "python_build_utils"
LOGGER_NAME: str = DIST_NAME

try:
    __version__: str = version(DIST_NAME)
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "LOGGER_NAME",
    "__version__",
    "collect_package_dependencies",
    "collect_pyd_modules_from_venv",
]
