.PHONY: up down models world pipeline dev test test-fast reset verify-offline types lint

# Frontend deps, installed on demand so a clean clone needs no setup step.
# (`uv run` already does the equivalent for the backend.) Re-runs only when
# package-lock.json changes.
frontend/node_modules: frontend/package-lock.json
	cd frontend && npm ci
	@touch frontend/node_modules

# --- M0: real targets ---

up:
	docker compose up -d --wait
	@echo "Applying Neo4j schema..."
	@bash -c 'set -a; [ -f .env ] && . ./.env; set +a; \
	docker compose exec -T neo4j cypher-shell -u "$${NEO4J_USER:-neo4j}" -p "$${NEO4J_PASSWORD:-cidlocaldev}" < backend/cid/pipeline/graph_build/schema.cypher'
	@echo "Running Postgres migrations..."
	cd backend && uv run python -m cid.core.migrations.runner

down:
	docker compose down

dev: frontend/node_modules
	@trap 'kill 0' EXIT INT TERM; \
	(cd backend && uv run uvicorn cid.api.main:app --reload --port 8000) & \
	(cd frontend && npm run dev) & \
	wait

test: frontend/node_modules
	cd backend && uv run pytest
	cd frontend && npm run test -- --run
	cd frontend && npm run typecheck

test-fast:
	cd backend && uv run pytest tests/unit -q

types: frontend/node_modules
	(cd backend && uv run python -c "import json, cid.api.main as m; print(json.dumps(m.app.openapi()))") > frontend/openapi.json
	cd frontend && npm run generate:types

lint: frontend/node_modules
	cd backend && uv run ruff check .
	cd frontend && npm run lint

# --- Not built yet: land in the milestones named below (docs/implementation.md) ---

models:
	@echo "make models: lands in M1 (downloads MuRIL + multilingual Sentence-BERT into models/hf/)."; exit 1

world:
	@echo "make world: lands in M1 (synthetic world generator)."; exit 1

pipeline:
	@echo "make pipeline: lands starting M2 (ingest) through M9 (ML stages)."; exit 1

reset:
	@echo "make reset: needs world + pipeline; lands once M2 is done."; exit 1

verify-offline:
	@echo "make verify-offline: lands in M11 (demo hardening)."; exit 1
