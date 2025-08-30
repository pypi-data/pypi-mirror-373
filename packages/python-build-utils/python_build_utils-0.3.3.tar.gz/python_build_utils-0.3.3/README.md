# python-build-utils

[![GitHub Release](https://img.shields.io/github/v/release/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/releases/tag/0.1.1)
[![PyPI Version](https://img.shields.io/pypi/v/python-build-utils)](https://pypi.org/project/python-build-utils/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/dave-Lab-and-Engineering/python-build-utils/main.yml?branch=main)](https://github.com/dave-Lab-and-Engineering/python-build-utils/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/dave-Lab-and-Engineering/python-build-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/dave-Lab-and-Engineering/python-build-utils)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/commits/main)
[![License](https://img.shields.io/github/license/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/blob/main/LICENSE)

Small collection of command line utilities to assist with building your Python wheels.

- GitHub repository: <https://github.com/dave-Lab-and-Engineering/python-build-utils>
- Documentation: <https://dave-lab-and-engineering.github.io/python-build-utils/>

---

## Installation

Install via PyPI:

```shell
pip install python-build-utils[all]
```

The optional `[all]` extra installs additional dependencies like `pipdeptree`, used by tools like `collect-dependencies`.

---

## Description

A collection of CLI tools for managing Python build artifacts, dependencies, and wheel files.

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
  clean-pyd-modules     Clean all .pyd/.c build modules in src path.
  collect-dependencies  Collect and display dependencies for one or more...
  collect-pyd-modules   Collect and display .pyd submodules from a...
  pyd2wheel             Create a Python wheel file from a compiled .pyd...
  remove-tarballs       Remove tarball files from dist.
  rename-wheel-files    Rename wheel files in a distribution directory by...
```

---

### clean-pyd-modules

```text
Usage: python-build-utils clean-pyd-modules [OPTIONS]

  Clean all .pyd/.c build modules in src path.

Options:
  --src-path TEXT   Path to the src folder to scan for .pyd modules. Defaults
                    to 'src' in the current folder.
  -r, --regex TEXT  Optional regular expression to filter .pyd modules by
                    name.
  --help            Show this message and exit.
```

Example:

```shell
python-build-utils clean-pyd-modules --regex dave
```

Removes .pyd and .c files from the src/ folder filtered by name.

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

  Collect and display .pyd submodules from a virtual environment.

Options:
  --venv-path TEXT   Path to the virtual environment to scan for .pyd modules.
                     Defaults to the current environment.
  -r, --regex TEXT   Optional regular expression to filter .pyd modules by
                     name.
  --collect-py       If set, collect .py files instead of .pyd files.
  -o, --output PATH  Optional file path to write the list of found .pyd
                     modules.
  --help             Show this message and exit.
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
                             other tag options. Default format is: {python_ver
                             sion_tag}-{python_version_tag}-{platform_tag}
  --help                     Show this message and exit.
```

---

### remove-tarballs

```text
Usage: python-build-utils remove-tarballs [OPTIONS]

  Remove tarball files from dist.

  This function removes tarball files from the given distribution directory.

  Args:     dist_dir (str): The directory containing the tarball files to be removed.

  Returns:     None

  Example:     remove_tarballs("dist")

Options:
  --dist_dir TEXT  Directory containing wheel the files. Default is 'dist'
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
