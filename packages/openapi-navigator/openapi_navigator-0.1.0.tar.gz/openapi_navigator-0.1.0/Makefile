.PHONY: help test test-unit test-integration test-cov test-fast clean format lint

help:  ## Show this help message
	@echo "OpenAPI Navigator - Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	uv run pytest

test-unit:  ## Run only unit tests (fast)
	uv run pytest tests/unit/ -v

test-integration:  ## Run only integration tests
	uv run pytest tests/integration/ -v

test-cov:  ## Run tests with coverage report
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

test-fast:  ## Run fast tests (exclude slow markers)
	uv run pytest -m "not slow"

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/openapi_mcp/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf tests/unit/__pycache__/
	rm -rf tests/integration/__pycache__/

format:  ## Format code with black
	uv run black src/ tests/

lint:  ## Lint code with ruff
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

install-dev:  ## Install development dependencies
	uv sync

build:  ## Build the package
	uv build

install:  ## Install the package in development mode
	uv sync

run:  ## Run the OpenAPI Navigator server
	uv run openapi-navigator
