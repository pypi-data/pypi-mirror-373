# PPIO Sandbox SDK - Test Management Makefile

.PHONY: help test test-* build clean

# Default target
help:
	@echo "PPIO Sandbox SDK Test Management"
	@echo "================================"
	@echo "Test Commands:"
	@echo "  test-core         Run all core module tests"
	@echo "  test-code-interpreter  Run code interpreter tests"
	@echo "  test-desktop      Run desktop automation tests"
	@echo "  clean             Clean build artifacts and cache files"

# Tests
test-core:
	poetry run python -m pytest -v --tb=long src/ppio_sandbox/core/tests/

test-code-interpreter:
	poetry run python -m pytest -v --tb=long src/ppio_sandbox/code_interpreter/tests/

test-desktop:
	poetry run python -m pytest -v --tb=long src/ppio_sandbox/desktop/tests/

test:
	make test-core
	make test-code-interpreter
	make test-desktop

build:
	poetry install
	poetry check
	poetry build

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	@echo "Cleanup completed!"
