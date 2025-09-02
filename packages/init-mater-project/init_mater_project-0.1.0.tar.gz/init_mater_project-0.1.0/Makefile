.PHONY: help install test-cli 

# Default target - auto-generate help from comments
help: ## Show available commands
	@echo "📋 Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  make %-10s - %s\n", $$1, $$2}'
	

install: ## Install init_mater_project package in editable mode
	uv pip install -e .

test-cli: ## Test CLI command to generate a MATER sample project locally 
	@rm -rf test-local
	uv run init-mater-project test-local
	@echo "\n✓ CLI test completed\n"

