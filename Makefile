COMPOSE := docker compose -f infra/docker/compose.yaml
API := cd services/api &&

.PHONY: help dev down logs test lint typecheck fmt

help:          ## Show targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

dev:           ## Start api, db and redis
	$(COMPOSE) up --build

down:          ## Stop the stack
	$(COMPOSE) down

logs:          ## Tail logs
	$(COMPOSE) logs -f

test:          ## Run backend tests (needs db: make db)
	$(API) uv run pytest

typecheck:     ## mypy strict on the backend
	$(API) uv run mypy app

lint:          ## All pre-commit hooks on all files
	pre-commit run --all-files

fmt:           ## Format Python
	$(API) uv run black . && uv run ruff check --fix .
