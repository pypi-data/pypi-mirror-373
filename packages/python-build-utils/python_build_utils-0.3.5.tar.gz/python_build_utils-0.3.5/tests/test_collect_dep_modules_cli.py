"""Unit tests for internal and CLI-facing functionality in `collect_dep_modules`.

Includes:
- Recursive dependency collection
- Import name extraction
- Filtering via regex
- Error handling for subprocesses and imports
- Tree rendering and node searching
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

import python_build_utils.collect_dep_modules as mod
from python_build_utils.collect_dep_modules import (
    _collect_dependency_names,
    _find_package_node,
    _get_dependency_tree,
    _get_deps_tree,
    _get_import_names,
    collect_package_dependencies,
)


@pytest.fixture
def sample_dep_tree() -> list[dict[str, Any]]:
    """Provide a sample nested dependency tree for reuse in tests."""
    return [
        {
            "key": "mypackage",
            "package_name": "mypackage",
            "installed_version": "1.0",
            "dependencies": [
                {
                    "key": "dep1",
                    "package_name": "dep1",
                    "installed_version": "2.0",
                    "dependencies": [
                        {
                            "key": "dep2",
                            "package_name": "dep2",
                            "installed_version": "3.0",
                            "dependencies": [],
                        },
                    ],
                },
            ],
        },
    ]


@patch("python_build_utils.collect_dep_modules._get_dependency_tree")
@patch("python_build_utils.collect_dep_modules._get_import_names", side_effect=lambda name: [name])
def test_basic_dependency_collection(mock_imports: Any, mock_tree: Any, sample_dep_tree: list[dict[str, Any]]) -> None:
    """Test full dependency resolution using mocks."""
    mock_tree.return_value = sample_dep_tree
    deps = collect_package_dependencies("mypackage")
    assert "dep1" in deps
    assert "dep2" in deps


@patch("python_build_utils.collect_dep_modules._get_dependency_tree", return_value=[])
def test_package_not_found(mock_tree: Any) -> None:
    """Return empty list when the target package is not found."""
    deps = collect_package_dependencies("unknown")
    assert deps == []


@patch("python_build_utils.collect_dep_modules._get_dependency_tree")
@patch("python_build_utils.collect_dep_modules._get_import_names", return_value=["secure_crypto"])
def test_regex_filtering(mock_imports: Any, mock_tree: Any, sample_dep_tree: list[dict[str, Any]]) -> None:
    """Return only dependencies that match the given regex."""
    sample_dep_tree[0]["dependencies"][0]["package_name"] = "secure_crypto"
    mock_tree.return_value = sample_dep_tree
    deps = collect_package_dependencies("mypackage", regex="crypto")
    assert deps == ["secure_crypto"]


def test_deps_tree_rendering(sample_dep_tree: list[dict[str, Any]]) -> None:
    """Test pretty rendering of a nested dependency tree."""
    deps_tree = _get_deps_tree(sample_dep_tree[0]["dependencies"])
    assert "- dep1 (2.0)" in deps_tree
    assert "- dep2 (3.0)" in deps_tree


def test_find_package_node_case_insensitive(sample_dep_tree: list[dict[str, Any]]) -> None:
    """Support case-insensitive lookup for package keys."""
    nodes = _find_package_node(sample_dep_tree, ("MYPACKAGE",))
    assert nodes[0]["key"] == "mypackage"


def test_collect_dependency_names_flat() -> None:
    """Flatten one-level dependency tree to a list."""
    deps = [{"package_name": "a", "dependencies": [{"package_name": "b", "dependencies": []}]}]
    with patch("python_build_utils.collect_dep_modules._get_import_names", side_effect=lambda name: [name]):
        collected = _collect_dependency_names(deps)
    assert collected == ["a", "b"]


def test_get_import_names_fallback() -> None:
    """Return raw name if importlib fallback triggers."""
    with patch("importlib.metadata.distribution", side_effect=Exception()):
        assert _get_import_names("something") == ["something"]


@patch("python_build_utils.collect_dep_modules._run_safe_subprocess")
def test_get_dependency_tree(mock_subprocess: Any) -> None:
    """Parse pipdeptree output into a dependency tree."""
    mock_subprocess.return_value = json.dumps([
        {"key": "mypackage", "package_name": "mypackage", "installed_version": "1.0", "dependencies": []},
    ])
    dep_tree = _get_dependency_tree()
    assert isinstance(dep_tree, list)
    assert dep_tree[0]["key"] == "mypackage"


@patch("python_build_utils.collect_dep_modules._get_dependency_tree")
def test_collect_dependencies_no_packages(mock_tree: Any) -> None:
    """Handle None as package name (top-level fallback)."""
    mock_tree.return_value = []
    deps = collect_package_dependencies(None)
    assert deps == []


@patch("python_build_utils.collect_dep_modules._get_dependency_tree")
def test_collect_dependencies_with_regex(mock_tree: Any, sample_dep_tree: list[dict[str, Any]]) -> None:
    """Filter dependencies with a regex string."""
    mock_tree.return_value = sample_dep_tree
    deps = collect_package_dependencies("mypackage", regex="dep1")
    assert deps == ["dep1"]


def test_get_dependency_tree_import_error(monkeypatch: Any) -> None:
    """Exit if pipdeptree is not installed."""
    monkeypatch.setitem(sys.modules, "pipdeptree", None)
    with pytest.raises(SystemExit):
        mod._get_dependency_tree()


def test_get_dependency_tree_subprocess_error(monkeypatch: Any) -> None:
    """Exit on pipdeptree subprocess failure."""
    mock_run = MagicMock(side_effect=subprocess.CalledProcessError(1, "cmd"))
    monkeypatch.setattr("subprocess.run", mock_run)
    with (
        patch("importlib.metadata.distribution", return_value=MagicMock(read_text=lambda _: "x")),
        pytest.raises(SystemExit),
    ):
        mod._run_safe_subprocess(["fake"])


def test_find_package_node_with_string(sample_dep_tree: list[dict[str, Any]]) -> None:
    """Find package using string instead of tuple for key lookup."""
    node = mod._find_package_node(sample_dep_tree, "mypackage")
    assert isinstance(node, list)
    assert node[0]["key"] == "mypackage"


def test_collect_dependency_names_recursion_and_duplicates() -> None:
    """Avoid infinite loops and collect unique packages in recursion."""
    deps = [
        {
            "package_name": "a",
            "dependencies": [
                {
                    "package_name": "b",
                    "dependencies": [{"package_name": "a", "dependencies": []}],
                },
            ],
        },
    ]
    with patch("python_build_utils.collect_dep_modules._get_import_names", lambda name: [name]):
        result = mod._collect_dependency_names(deps)
    assert set(result) == {"a", "b"}


def test_get_import_names_top_level(monkeypatch: Any) -> None:
    """Read top-level module names from metadata."""
    dist_mock = MagicMock()
    dist_mock.read_text.return_value = "foo\nbar"
    monkeypatch.setattr("python_build_utils.collect_dep_modules.distribution", lambda _: dist_mock)
    result = mod._get_import_names("any")
    assert result == ["foo", "bar"]


def test_get_import_names_empty_top_level(monkeypatch: Any) -> None:
    """Fallback op distributienaam als top_level.txt leeg of ontbreekt is."""
    dist_mock = MagicMock()
    dist_mock.read_text.return_value = ""
    monkeypatch.setattr("python_build_utils.collect_dep_modules.distribution", lambda _: dist_mock)
    result = mod._get_import_names("somepackage")
    assert result == ["somepackage"]


def test_collect_dependencies_write_to_file(tmp_path: Path) -> None:
    """Write dependencies to File via -Output."""
    output_path = tmp_path / "deps.txt"

    with patch("python_build_utils.collect_dep_modules.collect_package_dependencies", return_value=["a", "b"]):
        runner = CliRunner()
        result = runner.invoke(mod.collect_dependencies, ["--output", str(output_path)])

    assert result.exit_code == 0

    content = output_path.read_text(encoding="utf-8")
    assert "a" in content
    assert "b" in content


def test_collect_dependencies_cli_echo() -> None:
    """Print dependencies to stdout if --output is not given."""
    with patch("python_build_utils.collect_dep_modules.collect_package_dependencies", return_value=["depA", "depB"]):
        runner = CliRunner()
        result = runner.invoke(mod.collect_dependencies, [])

    assert result.exit_code == 0
    assert "depA" in result.output
    assert "depB" in result.output
