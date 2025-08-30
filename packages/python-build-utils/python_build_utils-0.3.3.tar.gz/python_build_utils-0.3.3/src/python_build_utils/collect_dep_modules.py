"""Collect dependencies of a package using pipdeptree."""

import importlib.util
import json
import logging
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import Any, cast

import click


logger = logging.getLogger(__name__)


@click.command(name="collect-dependencies", help="Collect and display dependencies for Python packages.")
@click.option(
    "--package",
    "-p",
    multiple=True,
    help=(
        "Name of the Python package to collect dependencies for. "
        "Can be given multiple times. If omitted, dependencies for the entire environment are collected."
    ),
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter modules by name.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    help="Optional file path to write the list of dependencies to.",
)
def collect_dependencies(
    package: tuple[str, ...] | None,
    output: str | None,
    regex: str | None = None,
) -> list[str] | None:
    """Collect dependencies for specified packages or the entire environment."""
    logger.info("Python Build Utilities — Dependency Collector starting up.")

    deps = collect_package_dependencies(package, regex)

    if not deps:
        logger.info("No dependencies found.")
        return None

    if output:
        output_path = Path(output)
        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(deps))
        logger.info("Dependencies written to %s", output_path)
    else:
        for dep in deps:
            click.echo(dep)

    return deps


def collect_package_dependencies(package: str | tuple[str, ...] | None, regex: str | None = None) -> list[str]:
    """Collect the dependencies of given packages in the current environment."""
    if not package or package == "":
        package_tuple: tuple[str, ...] | None = None
    elif isinstance(package, str):
        package_tuple = (package,)
    else:
        package_tuple = package

    dep_tree = _get_dependency_tree()
    package_nodes = _find_package_node(dep_tree, package_tuple)
    if not package_nodes:
        logger.warning("Package(s) %s not found in the environment.", package)
        return []

    all_dependencies: list[str] = []
    package_tree = ""

    for package_node in package_nodes:
        package_dependencies = package_node.get("dependencies", [])
        deps = _collect_dependency_names(package_dependencies)
        all_dependencies.extend(deps)
        package_tree = _get_deps_tree(package_dependencies, deps_tree=package_tree)

    if regex:
        pattern = re.compile(regex, re.IGNORECASE)
        all_dependencies = [p for p in all_dependencies if pattern.search(p)]

    logger.debug("Dependency tree:\n%s", package_tree)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_dependencies: list[str] = []

    for dep in all_dependencies:
        if dep not in seen:
            seen.add(dep)
            unique_dependencies.append(dep)

    return unique_dependencies


def _get_import_names(dist_name: str) -> list[str]:
    """Get top-level import names for a given installed distribution."""
    try:
        dist = distribution(dist_name)
        top_level_text = dist.read_text("top_level.txt")
        if top_level_text:
            return [line.strip() for line in top_level_text.splitlines() if line.strip()]
    except (PackageNotFoundError, FileNotFoundError):
        pass
    return [dist_name]


def _get_deps_tree(deps: list[dict[str, Any]], level: int = 1, deps_tree: str = "") -> str:
    """Return a formatted tree of dependencies."""
    for dep in deps:
        dep_name = dep["key"]
        dep_version = dep["installed_version"]
        deps_tree += "  " * level + f"- {dep_name} ({dep_version})\n"
        deps_tree = _get_deps_tree(dep.get("dependencies", []), level + 1, deps_tree)
    return deps_tree


def _run_safe_subprocess(command: list[str]) -> str:
    """Run a subprocess and return stdout, exit if it fails."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)  # nosec B603
    except subprocess.CalledProcessError as e:
        logger.warning("Subprocess failed: %s", e)
        sys.exit(1)
    return result.stdout


def _get_dependency_tree() -> list[dict[str, Any]]:
    """Use pipdeptree to get the full dependency tree in JSON format."""
    if importlib.util.find_spec("pipdeptree") is None:
        logger.exception(
            "pipdeptree is not installed. Please install it to use this tool.\n"
            "Run: pip install pipdeptree or python-build-utils[all]",
        )
        sys.exit(1)

    command = [sys.executable, "-m", "pipdeptree", "--json-tree"]
    stdout = _run_safe_subprocess(command)
    return cast(list[dict[str, Any]], json.loads(stdout))


def _find_package_node(
    dep_tree: list[dict[str, Any]],
    package: str | tuple[str, ...] | None,
) -> list[dict[str, Any]]:
    """Find the package node(s) in the dependency tree."""
    if not package:
        return dep_tree

    if isinstance(package, str):
        package = (package,)

    return [node for node in dep_tree if node["key"].lower() in {pkg.lower() for pkg in package}]


def _collect_dependency_names(
    dependencies: list[dict[str, Any]],
    collected: set[str] | None = None,
) -> list[str]:
    """Recursively collect all import names from dependency nodes."""
    if collected is None:
        collected = set()

    for dep in dependencies:
        dist_name = dep["package_name"]
        import_names = _get_import_names(dist_name)
        collected.update(import_names)
        _collect_dependency_names(dep.get("dependencies", []), collected)

    return sorted(collected)
