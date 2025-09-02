.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@uv sync --group dev
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .


sort: sort-imports fix-all-sorts

sort-imports:
	pre-commit run ruff --all-files --hook-stage manual

fix-all-sorts:
	ruff check src tests --select=RUF022 --fix


.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv sync --group dev
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml --cov-report=html --cov-report=json --cov-report=term-missing --junitxml=junit.xml -o junit_family=legacy

.PHONY: tox
tox: ## Test the code with tox
	@echo "🚀 Testing code: Running tox"
	@uv sync --group dev
	@uv run tox

.PHONY: tox-parallel
tox-parallel: ## Test the code with tox in parallel
	@echo "🚀 Testing code: Running tox"
	@uv sync --group dev
	@uv run tox run-parallel -p 10

.PHONY: all_tests
all_tests: check test tox-parallel ## Test the code using all the testts

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing."
	@uvx twine upload dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

coverage-upload:
	@echo "🚀 Uploading coverage report to Codecov"
	codecov --token=$(CODECOV_TOKEN)

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: docs-deploy
docs-deploy: ## Build and serve the documentation
	@uv run mkdocs gh-deploy --force --remote-branch gh-pages

.PHONY: examples
examples: ## Run the examples
	@echo "🚀 Example 1: converting dummy-0.1.1.py310-win_amd64.pyd"
	pyd2wheel examples/dummy-0.1.1.py310-win_amd64.pyd
	@echo
	@echo "🚀 Example 2: converting DAVEcore.cp310-win_amd64.pyd"
	pyd2wheel examples/DAVEcore.cp310-win_amd64.pyd --package_version 1.2.3

.PHONY: clean_examples
clean_examples: ## Clean the examples directory
	@echo "🚀 Cleaning whl files in examples directory."
	@uv run rm -v examples/*.whl

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
