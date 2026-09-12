## Current milestone

M0 — Foundations. Human said "go" on 2026-09-12.

Files to create:
- Root: `Makefile`, `docker-compose.yml`, `.env.example`, `config/cid.yaml`, `.gitignore` (written directly, not delegated — they define the contract both backend and frontend build against)
- `backend/pyproject.toml`, `backend/cid/core/{config.py,db_pg.py,db_neo4j.py,ids.py,hashing.py,logging.py,runs.py}`, `backend/cid/core/migrations/0001_init.sql` + a small runner, `backend/cid/pipeline/graph_build/schema.cypher`, `backend/cid/api/main.py` (`GET /api/health`), `backend/tests/unit/{test_config.py,test_migrations.py,test_health.py}` — delegated to one `implementer` agent
- `frontend/{package.json,vite.config.ts,index.html}`, `frontend/src/design/{tokens.css,fonts.ts,global.css}`, shell placeholders (`CaseStrip.tsx`, `Caption.tsx`, `QuestionRail.tsx`, `Legend.tsx`, `TimeStrip.tsx`), a component rendering "Mohammad Ali / मोहम्मद अली" in both font families, `frontend/src/api/types.ts` (generated), lint config + a test failing on any hex colour outside `tokens.css` — delegated to a second `implementer` agent, run after the backend agent since `make types` needs the backend's OpenAPI schema

Tests: backend pytest unit tests (config load, migrations apply cleanly twice, `/api/health` reports both DBs `ok`); frontend Vitest test that fails on stray hex colours; manual check of the shell in a browser with devtools networking disabled.

Unclear/flagged before starting: the three items already under "Open questions for the team" (Leiden vs Louvain, PRESENT_AT/CALLED storage ambiguity, P-13 merge-edge mechanism, N2 typology coverage) don't block M0 — none of them touch foundations work. Revisit before M4/M5/M7/M9 respectively.

## Decisions made during build

## Deviations from master/prd/arch

## Stuck

## Open questions for the team

- prd.md §10 P-05 says community grouping for leads uses "Leiden communities," but architecture.md §6.7 specifies `nx.community.louvain_communities` (Louvain). These are different algorithms with different outputs. Need a call on which one is actually built; architecture.md's own note ("master allows Louvain/Leiden") suggests Louvain was the intended implementation choice and P-05's "why" text wasn't updated to match. Not resolving silently — see reply to human.
- architecture.md is internally ambiguous about person-level `CALLED` and `PRESENT_AT`: §5.2's schema table lists them as graph relationship types (DOCUMENTED for phone, DERIVED for person), implying they are stored Neo4j relationships. But §6.5 (Graph build) says "Person-level `CALLED` and `PRESENT_AT` are not duplicated in the graph; the API derives them through `REGISTERED_TO` when needed and labels them DERIVED" — implying they are computed at query time, not stored. This affects whether `ml/hetero_data.py` (§6.8, which says it uses "edge types from §5.2... documented + derived only") needs to synthesize these edges itself or can read them from Neo4j directly. Needs a decision before M5/M9.
- prd.md P-13 answers master Q-AIM-05 (open: "class of merged identities") with "Merges are DERIVED... with resolution_confidence." But architecture.md's Neo4j schema (§5.2) has no relationship type representing a merge (no `SAME_AS`/`MERGED_WITH` edge) — entity resolution instead consolidates `mentions.resolved_entity_id` in Postgres and produces one `entities` row with `resolution_confidence` directly on it. So there is no edge for "merges are DERIVED" to attach an `evidence_class` to. Need to confirm this P-13 answer is describing the *entity's* resolution_confidence provenance in the abstract (not a literal graph edge), or whether a merge-edge is expected to exist.
- prd.md §7 says N2 (mule fan-out) is built to satisfy both T-02 (fan-out) and T-03 (structuring: ≥5 transfers below the synthetic threshold within 72h). The N2 description given ("hub account splits funds to 12 recently opened accounts below a synthetic threshold") only clearly describes the T-02 fan-out shape; it doesn't say the hub also makes ≥5 sub-threshold transfers within a 72h window from one account, which is what T-03's query idea (architecture §6.9) requires. Flagging so `generate/networks.py` (M1) is built to actually satisfy both typology queries, not just one.

## Gotchas

- Repo was not a git repository at session start; ran `git init` as the first M0 step.
- Team machine versions recorded 2026-09-12: Docker 29.7.2 (Compose v5.1.0), Node v24.18.0, Python 3.12.3, `uv` 0.10.12, NVIDIA driver 580.173.02 supporting CUDA 13.0. PyTorch CUDA wheel should target a cu12x build compatible with driver-reported CUDA 13.0 (pick this at M1's environment setup, not M0 — M0 has no GPU-dependent code).

## Dependencies added

## What this milestone taught
