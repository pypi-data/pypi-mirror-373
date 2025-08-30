.PHONY: help install test test-unit test-integration coverage lint format check all clean

help:			## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:		## Install dependencies
	uv sync --extra dev

test:			## Run all tests (unit + integration with testcontainers)
	uv run pytest tests/ -v

test-unit:		## Run unit tests only (fast, no Docker required)
	uv run pytest tests/ -v -m "not integration"

test-integration:	## Run integration tests only (requires Docker)
	uv run pytest tests/integration/ -v

coverage:		## Run tests with coverage report
	uv run pytest tests/ --cov=morpheus --cov-report=term-missing --cov-report=html

lint:			## Run linting (check only)
	uv run ruff check morpheus tests

format:			## Format code
	uv run ruff format morpheus tests

check:			## Run linting and formatting check
	uv run ruff check morpheus tests
	uv run ruff format --check morpheus tests

typecheck:		## Run type checking with ty
	uv run ty check

fix:			## Fix linting issues automatically
	uv run ruff check --fix morpheus tests
	uv run ruff format morpheus tests

all: install lint test	## Install deps, lint, and test

clean:			## Clean build artifacts
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

dev-setup:		## Set up development environment
	uv sync --extra dev
	@echo "Development environment ready!"
	@echo "Run 'make help' to see available commands"

ci:			## Run CI checks (lint + typecheck + all tests)
	uv run ruff check morpheus tests
	uv run ruff format --check morpheus tests
	uv run ty check
	uv run pytest tests/ -v

demo:			## Run a quick demo
	@echo "Creating demo migration system..."
	@mkdir -p demo_temp && cd demo_temp
	@uv run morpheus init
	@uv run morpheus create initial_schema --tags schema
	@uv run morpheus status
	@uv run morpheus dag
	@echo "Demo complete! Check demo_temp/ directory"