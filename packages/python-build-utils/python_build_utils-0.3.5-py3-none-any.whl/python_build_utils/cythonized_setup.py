# cythonized_setup.py
"""Build Python package with optional Cython extensions."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from setuptools import setup


logger = logging.getLogger(__name__)

CYTHON_REQUIRED_MESSAGE = (
    "Cython is required for building this package with Cython extensions. Please install Cython and try again."
)


def cythonized_setup(module_name: str) -> None:
    """If CYTHON_BUILD is set/non-empty: compile all .py under src/{module_name} via Cython.

    Otherwise: install as pure Python (keep .py files in the wheel).
    """
    should_use_cython = os.environ.get("CYTHON_BUILD", "").strip() != ""
    ext_modules = []
    exclude_package_data = {}

    if should_use_cython:
        try:
            from Cython.Build import cythonize
            from Cython.Compiler import Options
        except ImportError as e:
            raise ImportError(CYTHON_REQUIRED_MESSAGE) from e

        # slimmer/faster artefacten
        Options.docstrings = False
        Options.emit_code_comments = False

        logger.info("⛓️ Building with Cython extensions")

        py_files = [str(p) for p in Path("src", module_name).rglob("*.py")]
        # let cythonize derive module names; language_level=3 is enough
        ext_modules = cythonize(
            py_files,
            compiler_directives={"language_level": "3"},
            annotate=False,
        )

        # Only remove the source files from the Wheel at Cythonized Build
        exclude_package_data = {
            module_name: [
                "**/*.py",
                "**/*.c",
                "**/*.pxd",
                "**/*.pyi",
                "**/**/*.py",
                "**/**/*.c",
                "**/**/*.pxd",
                "**/**/*.pyi",
            ]
        }
    else:
        logger.info("🚫 No Cython build — pure Python package")

    setup(
        name=module_name,
        package_dir={"": "src"},
        # Include both .so (Linux) and .pyd (Windows)
        package_data={module_name: ["**/*.so", "**/*.pyd", "**/**/*.so", "**/**/*.pyd"]},
        exclude_package_data=exclude_package_data,
        ext_modules=ext_modules,
        zip_safe=False,
    )
