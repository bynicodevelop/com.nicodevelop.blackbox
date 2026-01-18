# Makefile for Blackbox Trading Robot
# ====================================

.PHONY: help install install-dev test lint format run-api run-cli docs docs-build clean

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Blackbox Trading Robot - Available Commands$(NC)"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created at $(VENV)$(NC)"

install: venv ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	$(BIN)/pip install -e .
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: venv ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.txt
	$(BIN)/pip install -e .
	$(BIN)/pre-commit install
	@echo "$(GREEN)Development installation complete!$(NC)"

# =============================================================================
# Code Quality
# =============================================================================

test: ## Run tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	$(BIN)/pytest

test-fast: ## Run tests without coverage
	@echo "$(BLUE)Running tests (fast mode)...$(NC)"
	$(BIN)/pytest --no-cov -q

lint: ## Check code with ruff
	@echo "$(BLUE)Checking code with ruff...$(NC)"
	$(BIN)/ruff check src/ tests/
	$(BIN)/ruff format --check src/ tests/

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	$(BIN)/ruff check --fix src/ tests/
	$(BIN)/ruff format src/ tests/
	@echo "$(GREEN)Code formatted!$(NC)"

# =============================================================================
# Run Applications
# =============================================================================

run-api: ## Run the FastAPI server
	@echo "$(BLUE)Starting API server at http://localhost:8000$(NC)"
	$(BIN)/uvicorn blackbox.api.main:app --reload --host 0.0.0.0 --port 8000

run-cli: ## Run the CLI
	@echo "$(BLUE)Running CLI...$(NC)"
	$(BIN)/blackbox --help

# =============================================================================
# Documentation
# =============================================================================

docs: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server at http://localhost:8001$(NC)"
	$(BIN)/mkdocs serve -a localhost:8001

docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	$(BIN)/mkdocs build
	@echo "$(GREEN)Documentation built in site/$(NC)"

# =============================================================================
# Maintenance
# =============================================================================

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf site/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)Full clean complete!$(NC)"
