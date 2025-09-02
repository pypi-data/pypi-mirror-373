# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.5] - 2025-09-01

- Added support for building .so libraries under Linux as well
- The clean_pyd_modules now also cleans .so libraries if available

## [0.3.2] - 2025-04-30

- Fullfiled codecov requirements to exceed 90% of coverage

## [0.3.1] - 2025-04-30

- Increased coverage to 80% and obeyed mypy
- Release for new makefiles

## [0.2.7] - 2025-04-30

- Coverage reporting now via codecov

## [0.2.5] - 2025-04-30

- Added regular expression option for collect-dependencies module
- Added more unit tests to increase coverage

## [0.2.4] - 2025-04-24

- collect package import name in stead of distribution names

## [0.2.3] - 2025-04-22

- new function for cythonizing your python code

## [0.2.0] - 2025-04-17

- Added logging functionality
- Added function api for external use
- collect-pyd module can now also include py modules:w
- Changed api of collect_package_dependies to allow argument to be a string

## [0.1.5] - 2025-04-15

- Added new command line utility collect-dependencies in order to generate a list of all package dependencies
- Added new command line utility collect-pyd-modules in order to generate a list of cythonized pyd dependencies
- Added new command line utility clean-pyd-modules in order to remove all cythonized files in a venv
- Updated README.md with new tool examples

## [0.1.2] - 2025-02-22

- MPL-2.0 license
- Code coverage published on [coveralls](https://coveralls.io/github/dave-Lab-and-Engineering/python-build-utils/)
- Improved readme and coupled badges to link pypi and build status

## [0.1.1] - 2025-02-21

- New tool `pyd2wheel` in order to pack wheel files based on \*.pyd files
- Improved API
- Improved unit tests for all modules

## [0.0.2] - 2025-02-10

- Initial release of `python-build-utils`.
- Added CLI tools for renaming wheel files and removing tarballs.
- Included support for custom Python version tags, platform tags, and wheel tags.
- Added documentation and examples for using the CLI tools.
- Added unit tests
