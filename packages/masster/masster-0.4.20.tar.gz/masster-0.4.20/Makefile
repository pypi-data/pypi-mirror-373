.PHONY: help install install-dev test test-cov lint format type-check clean build publish publish-test security pre-commit

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package for production
	uv sync

install-dev:  ## Install package with development dependencies
	uv sync --all-extras --dev

test:  ## Run tests
	uv run pytest tests/ -v

test-cov:  ## Run tests with coverage report
	uv run pytest tests/ -v --cov=masster --cov-report=term-missing --cov-report=html

test-integration:  ## Run integration tests only
	uv run pytest tests/test_integration.py -v

lint:  ## Run linting checks
	uv run flake8 src/masster tests
	uv run black --check src/masster tests

format:  ## Format code with black
	uv run black src/masster tests

type-check:  ## Run type checking with mypy
	uv run mypy src/masster --ignore-missing-imports

security:  ## Run security checks
	uv run safety check
	uv run bandit -r src/masster

pre-commit:  ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	uv build

check-build:  ## Check built package
	uv run twine check dist/*

publish-test:  ## Publish to Test PyPI
	uv run twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	uv run twine upload dist/*

version-bump-patch:  ## Bump patch version
	@echo "Current version: $$(grep 'version = ' pyproject.toml | cut -d'"' -f2)"
	@read -p "Enter new patch version (x.y.Z): " version && \
	sed -i 's/version = "[0-9]*\.[0-9]*\.[0-9]*"/version = "'$$version'"/' pyproject.toml && \
	sed -i 's/__version__ = "[0-9]*\.[0-9]*\.[0-9]*"/__version__ = "'$$version'"/' src/masster/_version.py
	@echo "Updated to version: $$(grep 'version = ' pyproject.toml | cut -d'"' -f2)"

# Development workflow shortcuts
dev-setup: install-dev pre-commit  ## Complete development setup
	@echo "Development environment ready!"

test-all: lint type-check security test-cov  ## Run all checks and tests

ci-test: test-all build check-build  ## Run CI-like tests locally

release-check: clean test-all build check-build  ## Pre-release checks
