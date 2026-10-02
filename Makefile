.DEFAULT_GOAL := help
.PHONY: help install lint format typecheck test cov check run eval docker-build docker-run clean

IMAGE ?= docent:dev
PORT  ?= 8000

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Sync locked deps + install git hooks
	uv sync --locked
	uv run pre-commit install

lint: ## Ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-fix lint + format
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## mypy strict
	uv run mypy

test: ## Unit tests (no external services)
	uv run pytest -m "not integration"

cov: ## Unit tests with coverage gate
	uv run pytest -m "not integration" --cov --cov-report=term-missing

check: lint typecheck cov ## Everything CI runs

run: ## Dev server with reload
	uv run uvicorn docent.api.main:app --reload --port $(PORT)

eval: ## Eval harness (lands Day 4)
	@echo "eval harness not implemented yet (Issue: Day 4)"; exit 1

docker-build: ## Build image
	docker build -t $(IMAGE) .

docker-run: ## Run image on localhost:$(PORT)
	docker run --rm -p $(PORT):8080 -e APP_ENV=dev $(IMAGE)

clean: ## Remove caches
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist
