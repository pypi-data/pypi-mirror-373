.PHONY: help install install-dev test test-cov lint format type-check clean build upload upload-test docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in development mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=gymix --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 gymix tests

format:  ## Format code with black
	black gymix tests example.py

format-check:  ## Check if code is formatted
	black --check gymix tests example.py

type-check:  ## Run type checking
	mypy gymix

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

upload-test:  ## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

check-all: format-check lint type-check test  ## Run all checks

dev-setup:  ## Set up development environment
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source venv/bin/activate  # On Linux/Mac"
	@echo "venv\\Scripts\\activate     # On Windows"
	@echo "Then run: make install-dev"

release-check: clean check-all build  ## Prepare for release
	@echo "Package ready for release!"
	@echo "Run 'make upload-test' to test on TestPyPI"
	@echo "Run 'make upload' to publish to PyPI"
