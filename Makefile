.DEFAULT_GOAL := help

BACKEND_DIR := backend
FRONTEND_DIR := frontend
COMPOSE := docker compose
UV := uv run
PNPM := pnpm
ALEMBIC := cd $(BACKEND_DIR) && $(UV) alembic
CLI := cd $(BACKEND_DIR) && $(UV) python cli.py

.PHONY: help env install setup dev backend frontend db-up migrate migration reset-migrate up down build logs ps collect analyze generate-digest send-digest run-daily typecheck lint-backend format lint-web lint build-web check clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ── Setup ────────────────────────────────────────────────────────────────────
env: ## Create .env files from examples (root, backend, frontend)
	[ -f .env ] || cp .env.example .env
	[ -f $(BACKEND_DIR)/.env ] || cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env
	[ -f $(FRONTEND_DIR)/.env.local ] || cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env.local

install: ## Install backend (uv) and frontend (pnpm) dependencies
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && $(PNPM) install

setup: env install db-up migrate ## Full first-time setup: env + install + db + migrations

# ── Local dev ────────────────────────────────────────────────────────────────
dev: ## Run backend :7101 + frontend :3200 together
	@trap 'kill 0' EXIT; \
	(cd $(BACKEND_DIR) && $(UV) uvicorn main:app --reload --port 7101) & \
	(cd $(FRONTEND_DIR) && $(PNPM) dev)

backend: ## Run backend only (uvicorn --reload, :7101)
	cd $(BACKEND_DIR) && $(UV) uvicorn main:app --reload --port 7101

frontend: ## Run frontend only (next dev, :3200)
	cd $(FRONTEND_DIR) && $(PNPM) dev

# ── Database ─────────────────────────────────────────────────────────────────
db-up: ## Start Postgres + Redis in Docker
	$(COMPOSE) up -d postgres redis

migrate: ## Apply migrations (alembic upgrade head)
	$(ALEMBIC) upgrade head

migration: ## Autogenerate a migration: make migration m="add runs table"
	$(ALEMBIC) upgrade head
	$(ALEMBIC) revision --autogenerate -m "$(m)"

reset-migrate: ## Drop and recreate the public schema, then re-apply migrations
	$(COMPOSE) up -d postgres
	@sleep 2
	$(COMPOSE) exec -T postgres sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"'
	$(ALEMBIC) upgrade head

# ── Pipeline (CLI) ───────────────────────────────────────────────────────────
collect: ## Run one ingestion pass across all enabled sources
	$(CLI) collect

analyze: ## Analyze pending content items with the AI provider
	$(CLI) analyze

generate-digest: ## Generate today's digest
	$(CLI) generate-digest

send-digest: ## Send today's digest to Telegram
	$(CLI) send-digest

run-daily: ## Run the full daily pipeline end to end
	$(CLI) run-daily

# ── Docker ───────────────────────────────────────────────────────────────────
up: ## Build and start all services in Docker
	$(COMPOSE) up --build -d

down: ## Stop all services
	$(COMPOSE) down

build: ## Build Docker images
	$(COMPOSE) build

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

ps: ## Show service status
	$(COMPOSE) ps

# ── Quality ──────────────────────────────────────────────────────────────────
typecheck: ## Type-check backend (pyright)
	cd $(BACKEND_DIR) && $(UV) pyright

lint-backend: ## Lint backend (ruff)
	cd $(BACKEND_DIR) && $(UV) ruff check .

format: ## Format backend (ruff format + autofix)
	cd $(BACKEND_DIR) && $(UV) ruff format . && $(UV) ruff check --fix .

lint-web: ## Lint frontend (oxlint + eslint + prettier)
	cd $(FRONTEND_DIR) && $(PNPM) lint

lint: lint-backend lint-web ## Lint everything

build-web: ## Production build of the frontend
	cd $(FRONTEND_DIR) && $(PNPM) build

check: typecheck lint build-web ## All quality gates: typecheck + lint + build

# ── Cleanup ──────────────────────────────────────────────────────────────────
clean: ## Stop services and remove volumes (destroys DB data)
	$(COMPOSE) down -v
