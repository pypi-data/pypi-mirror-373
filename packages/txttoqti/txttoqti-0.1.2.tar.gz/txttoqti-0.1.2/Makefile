# Makefile for txttoqti development

.PHONY: help install install-dev test test-fast lint format clean build docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install in development mode with dev dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  test-fast    - Run tests without coverage"
	@echo "  lint         - Run linting tools (flake8, mypy)"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts and cache files"
	@echo "  build        - Build package for distribution"
	@echo "  docs         - Generate documentation"

# Installation
install:
	pip install .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	python -m pytest --cov=src/txttoqti --cov-report=term-missing --cov-report=html

test-fast:
	python -m pytest

# Code quality
lint:
	python -m flake8 src tests
	python -m mypy src

format:
	python -m black src tests scripts

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
	rm -rf dist build *.egg-info

# Build
build: clean
	python -m build

# Documentation (placeholder)
docs:
	@echo "Documentation generation not yet implemented"

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete"

# Quick development cycle
dev: format lint test-fast
	@echo "Development cycle complete"

# Release preparation
release-check: format lint test build
	@echo "Release checks complete"