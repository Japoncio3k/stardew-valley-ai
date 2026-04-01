sources = data_ingestion
pypath = .
test_db_containers = test-db
all_db_containers = db graph-db $(test_db_containers)

.PHONY: help
# Show this help message
help:
	@echo "Usage: make [target]"
	@echo
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo

	@echo "  PORT              Set the port for running the API server, defaults to 8080."

.PHONY: setup-python
setup-python: ## Set up Python environment using pyenv
	@if pyenv versions --bare | grep -q "$$(cat .python-version)"; then \
		echo "Python version $$(cat .python-version) is already installed."; \
	else \
		pyenv install -v "$$(cat .python-version)"; \
	fi
	@pyenv local "$$(cat .python-version)"

.PHONY: install
install: ## Install the project dependencies (set REQUIREMENTS to 'production' for only production dependencies)
	@echo ">>> Updating poetry.lock based on pyproject.toml..."
	@poetry lock
	@echo ">>> Synchronizing virtual environment with the updated lock file..."
	@if [ "$(REQUIREMENTS)" = "production" ]; then \
		poetry sync --only main; \
	else \
		poetry sync; \
	fi

.PHONY: clean-install
clean-install: ## Clean up the project dependencies and recreate the virtual environment
	@rm -rf .venv
	@poetry cache clear --all pypi
	@$(MAKE) install REQUIREMENTS=$(REQUIREMENTS)

.PHONY: update
update: ## Update all dependencies without fixed version in pyproject.toml
	@poetry update $(args)

.PHONY: update-dependency
update-dependency: ## Update a specific dependency in pyproject.toml. Set 'package' argument to specify the package name. The 'force' will update the package to the latest version regardless of it having a fixed version in pyproject.toml.
	@if [ -z "$(package)" ]; then \
		echo "package is required"; \
	else \
		if [ "$(force)" == "true" ]; then \
			poetry add $(package)@latest; \
		else \
			poetry update $(package); \
		fi \
	fi

.PHONY: run-chunking-pipeline
run-chunking-pipeline:
	@poetry run python -m data_ingestion.pipelines.chunking_pipeline

.PHONY: run-ingestion-pipeline
run-ingestion-pipeline:
	@poetry run python -m data_ingestion.pipelines.ingestion_pipeline