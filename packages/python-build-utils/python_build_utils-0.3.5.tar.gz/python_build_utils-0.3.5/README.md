# python-build-utils

[![GitHub Release](https://img.shields.io/github/v/release/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/releases)
[![PyPI Version](https://img.shields.io/pypi/v/python-build-utils)](https://pypi.org/project/python-build-utils/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/dave-Lab-and-Engineering/python-build-utils/main.yml?branch=main)](https://github.com/dave-Lab-and-Engineering/python-build-utils/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/dave-Lab-and-Engineering/python-build-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/dave-Lab-and-Engineering/python-build-utils)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/commits/main)
[![License](https://img.shields.io/github/license/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/blob/main/LICENSE)

Small collection of command-line utilities to assist with building and packaging Python wheels.

- GitHub repository: <https://github.com/dave-Lab-and-Engineering/python-build-utils>
- Documentation: <https://dave-lab-and-engineering.github.io/python-build-utils/>

---

## Installation

Install via PyPI:

```shell
pip install python-build-utils[all]
```

The optional `[all]` extra installs additional dependencies like `pipdeptree`, used by tools such as `collect-dependencies`.

---

## Description

A curated set of CLI tools for managing Python build artifacts, dependencies, and wheel files.
Recent change: **`clean-pyd-modules` now also cleans Linux/Unix `.so` extension modules** (besides Windows `.pyd`) and generated `*.c` files.
Also, **`collect-pyd-modules`** can now discover multiple file types via `--ext` (e.g. `.pyd`, `.so`, `.py`).

---

## CLI Tools Overview

Check available commands:

```text
Usage: python-build-utils [OPTIONS] COMMAND [ARGS]...

  A collection of CLI tools for Python build utilities.

Options:
  --version      Show the version and exit.
  -v, --verbose  Increase verbosity level. Use -v for info, -vv for debug.
  --help         Show this message and exit.

Commands:
  clean-pyd-modules     Clean compiled modules (.pyd/.so) and generated C files in src path.
  collect-dependencies  Collect and display dependencies for one or more packages.
  collect-pyd-modules   Collect and display compiled/source submodules from a virtual environment.
  pyd2wheel             Create a Python wheel file from a compiled .pyd file.
  remove-tarballs       Remove tarball files from dist.
  rename-wheel-files    Rename wheel files in a distribution directory by applying custom tags.
```

---

### clean-pyd-modules

```text
Usage: python-build-utils clean-pyd-modules [OPTIONS]

  Clean all compiled modules and generated C files in the given src path.

  Removes:
    • Windows: *.pyd
    • Linux/Unix: *.so
    • Generated C sources: *.c

Options:
  --src-path TEXT   Path to the src folder to scan. Defaults to 'src' in the current folder.
  -r, --regex TEXT  Optional regular expression to filter files by name (matched against relative paths).
  --help            Show this message and exit.
```

Examples:

```shell
# Clean every compiled artifact under ./src
python-build-utils clean-pyd-modules

# Clean only modules that match 'dave' anywhere in their relative path
python-build-utils clean-pyd-modules --regex dave

# Clean in a different source root
python-build-utils clean-pyd-modules --src-path packages/core/src
```

---

### collect-dependencies

```text
Usage: python-build-utils collect-dependencies [OPTIONS]

  Collect and display dependencies for one or more Python packages.

Options:
  -p, --package TEXT  Name of the Python package to collect dependencies for.
                      Can be given multiple times. If omitted, dependencies
                      for the entire environment are collected.
  -r, --regex TEXT    Optional regular expression to filter modules by name.
  -o, --output PATH   Optional file path to write the list of dependencies to.
  --help              Show this message and exit.
```

---

### collect-pyd-modules

```text
Usage: python-build-utils collect-pyd-modules [OPTIONS]

  Collect and display compiled (.pyd/.so) or source (.py) submodules from a virtual environment.

Options:
  --venv-path TEXT   Path to the virtual environment to scan. Defaults to the current environment.
  -r, --regex TEXT   Optional regular expression to filter module names.
  --collect-py       Deprecated: collect only .py files (equivalent to --ext=py).
  --ext [pyd|so|py|compiled|all]
                    Which file types to collect:
                      pyd (.pyd), so (.so), py (.py),
                      compiled (.pyd + .so), or all (compiled + .py).
                    [default: pyd]
  -o, --output PATH  Optional file path to write the list of found modules.
  --help             Show this message and exit.
```

Examples:

```shell
# Default behavior: collect .pyd modules (Windows-style builds)
python-build-utils collect-pyd-modules --venv-path .venv

# Collect Linux/Unix extension modules
python-build-utils collect-pyd-modules --venv-path .venv --ext=so

# Collect all compiled modules (both .pyd and .so)
python-build-utils collect-pyd-modules --venv-path .venv --ext=compiled

# Collect only .py modules (deprecated flag is still supported)
python-build-utils collect-pyd-modules --venv-path .venv --collect-py

# Write output to a file
python-build-utils collect-pyd-modules --ext=compiled -o modules.txt
```

---

### rename-wheel-files

```text
Usage: python-build-utils rename-wheel-files [OPTIONS]

  Rename wheel files in a distribution directory by replacing the default
  'py3-none-any' tag with a custom one.

Options:
  --dist-dir TEXT            Directory containing wheel files. Defaults to
                             'dist'.
  --python-version-tag TEXT  Python version tag to include in the new file
                             name (e.g., cp310). Defaults to
                             'cp{major}{minor}' of the current Python.
  --platform-tag TEXT        Platform tag to include in the new file name.
                             Defaults to the current platform value from
                             sysconfig.
  --wheel-tag TEXT           Full custom wheel tag to replace 'py3-none-any'.
                             If provided, this is used directly, ignoring the
                             other tag options. Default format is:
                             {python_version_tag}-{python_version_tag}-{platform_tag}
  --help                     Show this message and exit.
```

---

### remove-tarballs

```text
Usage: python-build-utils remove-tarballs [OPTIONS]

  Remove tarball files from dist.

Options:
  --dist_dir TEXT  Directory containing the files. Default is 'dist'
  --help           Show this message and exit.
```

---

### pyd2wheel

```text
Usage: python-build-utils pyd2wheel [OPTIONS] PYD_FILE

  Create a Python wheel file from a compiled .pyd file.

Options:
  --package-version TEXT  Version of the package. If not provided, the version
                          is extracted from the file name.
  --abi-tag TEXT          ABI tag for the wheel. Defaults to 'none'.
  --help                  Show this message and exit.
```

---

## Developers

We use **Prettier** as part of the pre-commit hooks to ensure consistent formatting.

The initial setup (done once when introducing Prettier) was:

```shell
npm init -y
npm install --save-dev prettier
```

This created a `package.json` that pins the Prettier version used in this project.

For other developers who clone the repository, simply run:

```shell
npm install --no-audit --no-fund
```

This installs the same Prettier version defined in `package.json`, ensuring consistent formatting across all environments.
