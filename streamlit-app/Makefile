# Makefile for Streamlit App Testing

.PHONY: help install test test-unit test-integration test-ui test-security test-all coverage clean lint format type-check

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip

# Pytest options
PYTEST := pytest
PYTEST_OPTS := -v --tb=short
COVERAGE_OPTS := --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml

help: ## Show this help message
	@echo "Streamlit App Test Suite"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r tests/requirements-test.txt

test: ## Run all tests
	$(PYTEST) $(PYTEST_OPTS)

test-unit: ## Run unit tests only
	$(PYTEST) $(PYTEST_OPTS) -m unit

test-integration: ## Run integration tests only
	$(PYTEST) $(PYTEST_OPTS) -m integration

test-ui: ## Run UI tests only
	$(PYTEST) $(PYTEST_OPTS) -m ui

test-security: ## Run security tests only
	$(PYTEST) $(PYTEST_OPTS) -m security

test-performance: ## Run performance tests only
	$(PYTEST) $(PYTEST_OPTS) -m performance

test-edge: ## Run edge case tests only
	$(PYTEST) $(PYTEST_OPTS) -m edge_case

test-fast: ## Run all tests except slow ones
	$(PYTEST) $(PYTEST_OPTS) -m "not slow"

test-parallel: ## Run tests in parallel
	$(PYTEST) $(PYTEST_OPTS) -n auto

coverage: ## Run tests with coverage
	$(PYTEST) $(PYTEST_OPTS) $(COVERAGE_OPTS)

coverage-html: coverage ## Generate HTML coverage report
	@echo ""
	@echo "Coverage report generated: htmlcov/index.html"
	@echo "Open in browser with: open htmlcov/index.html (Mac) or xdg-open htmlcov/index.html (Linux)"

coverage-report: ## Show coverage report in terminal
	$(PYTEST) --cov=. --cov-report=term-missing

test-validators: ## Run validator tests only
	$(PYTEST) $(PYTEST_OPTS) tests/test_validators.py

test-generators: ## Run generator tests only
	$(PYTEST) $(PYTEST_OPTS) tests/test_generators.py

test-components: ## Run component tests only
	$(PYTEST) $(PYTEST_OPTS) tests/test_components.py

test-all: coverage ## Run all tests with coverage
	@echo ""
	@echo "All tests completed with coverage!"

clean: ## Clean test artifacts and cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf tests/__pycache__
	rm -rf tests/.pytest_cache
	rm -f tests/test_run.log
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code with black and isort
	black .
	isort .

format-check: ## Check code formatting
	black --check .
	isort --check-only .

type-check: ## Run type checking with mypy
	mypy . --ignore-missing-imports

qa: lint format-check type-check ## Run all quality checks

ci: install test-all lint ## Run CI pipeline (install, test, lint)

watch: ## Run tests in watch mode (requires pytest-watch)
	ptw -- $(PYTEST_OPTS)

debug: ## Run tests with debugging output
	$(PYTEST) -vv -s --tb=long

benchmark: ## Run performance benchmarks
	$(PYTEST) --benchmark-only

test-verbose: ## Run tests with maximum verbosity
	$(PYTEST) -vvv --tb=long

quick: ## Quick test run (unit tests only, no coverage)
	$(PYTEST) -m unit --tb=short

init: install ## Initialize development environment
	@echo "Development environment ready!"

verify: ## Verify test suite is working
	$(PYTEST) --collect-only
	@echo ""
	@echo "Test collection successful!"

count-tests: ## Count number of tests
	@echo "Total tests:"
	@$(PYTEST) --collect-only -q | tail -n 1
	@echo ""
	@echo "By category:"
	@echo -n "  Unit: "
	@$(PYTEST) --collect-only -q -m unit 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"
	@echo -n "  Integration: "
	@$(PYTEST) --collect-only -q -m integration 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"
	@echo -n "  UI: "
	@$(PYTEST) --collect-only -q -m ui 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"
	@echo -n "  Security: "
	@$(PYTEST) --collect-only -q -m security 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"
	@echo -n "  Performance: "
	@$(PYTEST) --collect-only -q -m performance 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"
	@echo -n "  Edge case: "
	@$(PYTEST) --collect-only -q -m edge_case 2>/dev/null | tail -n 1 | awk '{print $$1}' || echo "0"

.PHONY: pre-commit
pre-commit: format-check lint test-fast ## Pre-commit checks (fast tests, format, lint)
	@echo ""
	@echo "Pre-commit checks passed! ✓"
