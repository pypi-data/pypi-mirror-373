.PHONY: help install test lint format type-check clean build publish dev-install

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

dev-install:  ## Install with all development dependencies
	uv sync --all-extras
	uv run pre-commit install

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=simplespec --cov-report=html --cov-report=term-missing

lint:  ## Run linting
	uv run ruff check

lint-fix:  ## Run linting with auto-fix
	uv run ruff check --fix

format:  ## Format code
	uv run ruff format

format-check:  ## Check code formatting
	uv run ruff format --check

type-check:  ## Run type checking
	uv run mypy simplespec

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	uv build

publish:  ## Publish to PyPI (requires PYPI_API_TOKEN environment variable)
	@if [ -z "$$PYPI_API_TOKEN" ]; then \
		echo "❌ Error: PYPI_API_TOKEN environment variable is not set"; \
		echo "Set it in GitHub Codespaces secrets or run: export PYPI_API_TOKEN=your_token"; \
		exit 1; \
	fi
	uv build
	uv run twine upload dist/* --username __token__ --password $$PYPI_API_TOKEN

check-all: lint format-check type-check test  ## Run all checks

ci: check-all  ## Run CI pipeline locally
