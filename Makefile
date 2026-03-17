.PHONY: help install dev-install test test-cov lint format clean run

help:
	@echo "Lumina - Makefile Commands"
	@echo ""
	@echo "  make install      - Install production dependencies"
	@echo "  make dev-install  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make run          - Run Lumina in interactive mode"
	@echo ""

install:
	pip install -r requirements.txt

dev-install:
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=lumina --cov-report=html --cov-report=term

lint:
	@echo "Running pylint..."
	@pylint lumina/ || true
	@echo "Checking with flake8..."
	@flake8 lumina/ --max-line-length=100 || true

format:
	black lumina/ tests/ examples/

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

run:
	python -m lumina.cli

run-verbose:
	python -m lumina.cli --verbose

example:
	python examples/basic_usage.py
