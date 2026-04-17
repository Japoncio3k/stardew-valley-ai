sources = data_ingestion app
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
setup-python:
	@if pyenv versions --bare | grep -q "$$(cat .python-version)"; then \
		echo "Python version $$(cat .python-version) is already installed."; \
	else \
		pyenv install -v "$$(cat .python-version)"; \
	fi
	@pyenv local "$$(cat .python-version)"

.PHONY: install
install:
	@echo ">>> Updating poetry.lock based on pyproject.toml..."
	@poetry lock
	@echo ">>> Synchronizing virtual environment with the updated lock file..."
	@if [ "$(REQUIREMENTS)" = "production" ]; then \
		poetry sync --only main; \
	else \
		poetry sync; \
	fi

.PHONY: clean-install
clean-install:
	@rm -rf .venv
	@poetry cache clear --all pypi
	@$(MAKE) install REQUIREMENTS=$(REQUIREMENTS)

.PHONY: update
update:
	@poetry update $(args)

.PHONY: update-dependency
update-dependency:
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

.PHONY: lint-check
lint-check: 
	@echo "Starting ruff check:"
	@poetry run ruff check $(sources)
	@echo "Starting mypy check:"
	@poetry run mypy $(sources)

.PHONY: test
test: ## Run tests
	@poetry run pytest

.PHONY: run-api
run-api: ## Run the API server (set PORT to specify port, default is 8080)
ifdef PORT
	@bash -c 'poetry run uvicorn app.api.main:app --reload --host 0.0.0.0 --port $(PORT)'
else
	@bash -c 'poetry run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8080'
endif