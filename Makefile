.PHONY: up down models world world-report pipeline dev test test-fast reset verify-offline types lint

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

world:
	cd backend && uv run python -m cid.pipeline.generate.world

world-report:
	cd backend && uv run python -m cid.pipeline.generate.report

types: frontend/node_modules
	(cd backend && uv run python -c "import json, cid.api.main as m; print(json.dumps(m.app.openapi()))") > frontend/openapi.json
	cd frontend && npm run generate:types

lint: frontend/node_modules
	cd backend && uv run ruff check .
	cd frontend && npm run lint

# --- Not built yet: land in the milestones named below (docs/implementation.md) ---

models:
	@echo "make models: lands in M1 (downloads MuRIL + multilingual Sentence-BERT into models/hf/)."; exit 1

pipeline:
	@echo "make pipeline: lands starting M2 (ingest) through M9 (ML stages)."; exit 1

# Drop both stores, rebuild the world, reload it. The record store keys on
# source_record_id, so a regenerated world leaves orphaned rows behind unless
# the store is dropped first — reset is the supported way to change the world.
# Grows a pipeline step per milestone (extract, resolve, graph...).
reset:
	@bash -c 'set -a; [ -f .env ] && . ./.env; set +a; \
	docker compose exec -T postgres psql -U "$${POSTGRES_USER:-cid}" -d "$${POSTGRES_DB:-cid}" \
	  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" >/dev/null; \
	docker compose exec -T neo4j cypher-shell -u "$${NEO4J_USER:-neo4j}" -p "$${NEO4J_PASSWORD:-cidlocaldev}" \
	  "MATCH (n) DETACH DELETE n" >/dev/null'
	@echo "Stores dropped."
	$(MAKE) up
	$(MAKE) world
	cd backend && uv run python -m cid.pipeline.ingest.load

verify-offline:
	@echo "make verify-offline: lands in M11 (demo hardening)."; exit 1
