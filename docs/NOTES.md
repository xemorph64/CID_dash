## Current milestone

M1 — Synthetic world. Started 2026-09-12 (human cleared the M0 checkpoint and asked for the four open questions to be resolved; see "Resolved questions" below).

**Plan.** Files under `backend/cid/pipeline/generate/`: `names.py` (name corpus + variant rendering + the four identity traps), `narratives.py` (FIR template families with gold spans/relations at character offsets), `networks.py` (N1–N3 + ~30 background), `lookalikes.py` (4 honest false-positive shapes), `world.py` (orchestrates, emits `data/world/*.jsonl`), `truth.py` (assembles `truth.json`), `report.py` (`make world-report`). Tests in `backend/tests/unit/` (per-module) and `backend/tests/golden/` (world-level acceptance).

**Determinism discipline** (the fragile part — one seed must give byte-identical output):
- Every function that needs randomness takes an explicit `rng: random.Random`; no module-level `random.*`, no global state. `world.py` derives per-stage child RNGs from `config.seed` deterministically.
- Faker is seeded per-instance (`fake.seed_instance(n)`), never via the global `Faker.seed`.
- Never use builtin `hash()` for IDs or ordering — it is salted per process (`PYTHONHASHSEED`). Use `hashlib` instead.
- No `datetime.now()` / `uuid4()` anywhere in generation; all dates derive from `world.start_date`/`world.end_date` in config.
- Sort before writing anything derived from a set; JSON written with `ensure_ascii=False, sort_keys=True, separators=(",", ":")`, UTF-8, `\n` newlines.

**Gotcha found up front:** raw ITRANS transliteration of "mohammad ali" yields `मोहम्मद् अलि`, not the `मोहम्मद अली` that prd demo beat 2 requires. So the demo-critical identity traps use **curated** script forms; transliteration is only for bulk background names where exact orthography doesn't matter.

Acceptance tests to write (from implementation.md M1): byte-identical re-run on the same seed; `truth.json` carries N1–N3 plus ≥30 background networks each with a typology label; all four Mohammad Ali surface forms across four different sources; the two Raj Kumars differ in DOB and phone; ≥10% of person mentions in Devanagari and both IPC and BNS codes present; every gold span satisfies `text[start:end] == surface`.

---

M0 — Foundations. **Complete**, checkpoint cleared by the human 2026-09-12.

Acceptance (all three checks from implementation.md M0, verified, not assumed):
- `make up && make test` from a clean clone (fresh `git clone`, no `node_modules`, no `.venv`, volumes wiped): passes, exit 0 — backend 6 tests, frontend 1 test, typecheck clean. First attempt failed with `vitest: not found`; fixed at root (Makefile now installs frontend deps on demand) rather than by pre-installing by hand.
- `curl localhost:8000/api/health` → `{"postgres":"ok","neo4j":"ok"}`, from the clean clone.
- Shell renders in both font families in a real browser (Anek for interface text, Tiro for the record voice, Devanagari with no tofu), console clean, 32 resources loaded and **zero external** — the offline claim is measured.

Next: M1 (synthetic world) — do not start until the human clears this checkpoint.

---

Original plan for M0 (kept for reference):

Files to create:
- Root: `Makefile`, `docker-compose.yml`, `.env.example`, `config/cid.yaml`, `.gitignore` (written directly, not delegated — they define the contract both backend and frontend build against)
- `backend/pyproject.toml`, `backend/cid/core/{config.py,db_pg.py,db_neo4j.py,ids.py,hashing.py,logging.py,runs.py}`, `backend/cid/core/migrations/0001_init.sql` + a small runner, `backend/cid/pipeline/graph_build/schema.cypher`, `backend/cid/api/main.py` (`GET /api/health`), `backend/tests/unit/{test_config.py,test_migrations.py,test_health.py}` — delegated to one `implementer` agent
- `frontend/{package.json,vite.config.ts,index.html}`, `frontend/src/design/{tokens.css,fonts.ts,global.css}`, shell placeholders (`CaseStrip.tsx`, `QuestionRail.tsx`, `Legend.tsx`, `TimeStrip.tsx` — no `Caption.tsx` yet, that's M6's pure `caption.ts` function over real counts), a component rendering "Mohammad Ali / मोहम्मद अली" in both font families, `frontend/src/api/types.ts` (generated), lint config + a test failing on any hex colour outside `tokens.css` — delegated to a second `implementer` agent, run after the backend agent since `make types` needs the backend's OpenAPI schema

Tests: backend pytest unit tests (config load, migrations apply cleanly twice, `/api/health` reports both DBs `ok`); frontend Vitest test that fails on stray hex colours; manual check of the shell in a browser with devtools networking disabled.

Unclear/flagged before starting: the three items already under "Open questions for the team" (Leiden vs Louvain, PRESENT_AT/CALLED storage ambiguity, P-13 merge-edge mechanism, N2 typology coverage) don't block M0 — none of them touch foundations work. Revisit before M4/M5/M7/M9 respectively.

## Decisions made during build

- M0: pinned React 18.3.1 / Vite 5.4.21 / TypeScript 5.6.3 / Vitest 2.1.9 / ESLint 9 / `@vitejs/plugin-react` 4.7.0 rather than accepting `npm create vite@latest`'s current defaults (React 19 + Vite 8 + oxlint) — architecture.md §3 decides React 18 and eslint, and §3 says pin versions at M0 and don't upgrade mid-build.
- M0: shell components use CSS Modules for scoped styles (architecture.md §3 already chose "plain CSS with CSS variables and CSS Modules"); built into Vite, no new dependency.
- M0: no `react-router-dom`, Zustand, TanStack Query or Cytoscape yet — one static page needs none of them; they arrive with the screens that need them (M6+).
- M0: `Caption.tsx` deliberately not built — prd's caption is a pure function over real counts (`lib/caption.ts`, unit-tested), which is M6 work once there is a graph payload to count.

## Deviations from master/prd/arch

- architecture.md §5.2 describes "an index on relationship `edge_id`" as one index. Neo4j 5 has no wildcard-relationship-type index syntax (confirmed against the live container: `FOR ()-[r]-()` is rejected). `schema.cypher` instead creates one `edge_id` index per relationship type listed in §5.2 (13 total). Same intent, different syntax — approved as the only way to satisfy the requirement.

## Stuck

## Open questions for the team

_None open. The four raised before M0 were resolved on 2026-09-12 (human asked for resolutions rather than answering each); the decisions are recorded below under "Resolved questions". Raise anything new here._

### Resolved questions (2026-09-12, decided by Claude at the human's request)

**R-1 — Communities: Louvain, not Leiden.** prd §10 P-05's wording said "Leiden"; architecture.md §6.7 specifies `nx.community.louvain_communities(G, seed=seed)`. Resolved in favour of **Louvain**, because: master §13.2 explicitly allows either, so neither choice conflicts with the master; NetworkX ships Louvain with a `seed` argument, which the determinism requirement (same seed ⇒ same leads, prd §8) needs, at zero new dependencies; Leiden would require adding `leidenalg` + `igraph` (CLAUDE.md rule 9) to gain an advantage — Leiden's guarantee against badly-connected communities — that only matters at a scale far above the ≤2,000-node case subgraphs of architecture §6.7. P-05's substance (case-scoped network, two steps out, communities used to group leads) is unchanged; only the algorithm name was wrong. prd §10 P-05 annotated in place so the two documents no longer contradict.

**R-2 — Person-level `CALLED` / `PRESENT_AT` are NOT stored in Neo4j.** architecture.md §5.2's table and §6.5 appeared to disagree. Resolved in favour of **§6.5**: the graph stores phone-level `CALLED` (one edge per call, P-04) and phone-level `PRESENT_AT` only; person-level versions are derived through `REGISTERED_TO` at query time by the API and labelled DERIVED. Reasons: §6.5 is the specific operational instruction about what the writer does, and it prevents a second, driftable copy of the same fact; materialising person-level duplicates would roughly double edge count for no query we can't serve with a join. §5.2's "DOCUMENTED (phone), DERIVED (person)" is read as *the class the edge carries wherever it appears*, including when the API synthesises it — not a promise that person-level rows exist in the store.
  - Consequence for M9 `ml/hetero_data.py`: it does **not** need to synthesise person-level edges. `PhoneNumber` is already a node type with its own features (§6.8) and `REGISTERED_TO` connects phone→person, so the HGT propagates person→phone→phone→person natively. Feeding it a synthesised person-level `CALLED` on top would double-count the same evidence.
  - General rule adopted from this: **derive cheap joins at query time; materialise only expensive computations.** That is why `CO_LOCATED_WITH` *is* materialised (§6.6) — it is a DBSCAN result, not a join.

**R-3 — P-13 means no `SAME_AS` edge exists; ER merges live in Postgres.** Master §19.4 rule 8 leaves open "the class of edges that *depend on* entity-resolution merges" (Q-AIM-05) — it does not ask for a merge edge. Resolved: entity resolution stays a Postgres-side consolidation (`mentions.resolved_entity_id` → one `entities` row carrying `resolution_confidence`); **no `SAME_AS`/`MERGED_WITH` relationship is ever written to Neo4j.** P-13's "merges are DERIVED" is about the *identity conclusion*, not an edge class: an edge whose endpoint identity came out of ER keeps its own class (DOCUMENTED when a record states the relationship) while carrying `resolution_confidence` in the common set, and `confidence = min(extraction_confidence, resolution_confidence)` (§5.2) is exactly how the merge's uncertainty propagates onto every edge that depends on it. The officer sees the identity is assembled through the identity stack and match chips (prd §5.6.4), not through an edge. The mechanism P-13 needs therefore already exists in the schema.

**R-4 — N2 must satisfy T-02 and T-03 simultaneously; the generator supplies the missing timing.** prd §7 assigns N2 both typologies but describes only the fan-out shape. Resolved per CLAUDE.md rule 10 (tune the data, never the rules): `generate/networks.py` builds N2 so both architecture §6.9 queries fire on it, adding timing specificity that prd §7 leaves unstated without contradicting anything it does say — 12 mule accounts each opened 10–50 days before they receive (T-02 needs ≥8 opened <60 days prior); each mule forwards on within 6–36 h so median holding time is <48 h (T-02); all 12 transfers below the ₹50,000 synthetic threshold, with ≥5 of them falling inside one 72-hour window (T-03 needs ≥5 sub-threshold from one account within 72 h). Thresholds themselves are untouched.

## Gotchas

- Repo was not a git repository at session start; ran `git init` as the first M0 step.
- `make` recipes run each line in one shell, so `cd backend && cmd > frontend/out.json` resolves the redirect *after* the `cd` and writes to `backend/frontend/`. Fixed in the `types` target by scoping the `cd` to a subshell: `(cd backend && cmd) > frontend/openapi.json`. Watch for this in every future target that redirects output across directories.
- Team machine versions recorded 2026-09-12: Docker 29.7.2 (Compose v5.1.0), Node v24.18.0, Python 3.12.3, `uv` 0.10.12, NVIDIA driver 580.173.02 supporting CUDA 13.0. PyTorch CUDA wheel should target a cu12x build compatible with driver-reported CUDA 13.0 (pick this at M1's environment setup, not M0 — M0 has no GPU-dependent code).

## Dependencies added

- `httpx` (backend dev dependency) — required by `fastapi.testclient.TestClient`, used in `test_health.py`. Not pulled in transitively by `fastapi`/`uvicorn[standard]`.
- M1: `faker` — prd §7 names it as the source of person/address filler ("Faker `en_IN` and `hi_IN` plus curated name lists"). `hi_IN` emits Devanagari names directly, which helps the ≥10%-Devanagari acceptance check.
- M1: `indic-transliteration` — already sanctioned by architecture.md §3 (listed under ER); used here for Devanagari/Tamil/Bengali renderings of background names, and at M4 for the Indic phonetic key.

## What this milestone taught

**M0 — Foundations.**
1. Two databases, two jobs: Neo4j holds *relationships* (who connects to whom, traversed cheaply many hops out); Postgres holds *records and workflow* (the original source records behind every edge, plus cases, users, leads, stamps and the audit chain). The graph stays small and fast because the bulky evidence lives in Postgres and edges only carry a `source_record_id` pointer to it (P-17, P-18).
2. Config flows one way: `config/cid.yaml` holds everything about *how the system behaves* (seed, thresholds, model names) and is committed; `.env` holds only *secrets and connection details* and is never committed. `cid/core/config.py` merges them with env vars winning, so a laptop can override a connection without touching a committed file, and no later stage can quietly hardcode a threshold that belongs in the yaml.
3. Provenance is enforced by schema shape from day one: the `source_records` table exists before anything can write an edge, so "every DOCUMENTED edge resolves to a record" is a constraint we can test rather than a promise.
4. The design system is guarded by a test, not by discipline: a Vitest scan fails the build if any hex colour appears outside `tokens.css`. Verified it actually fails when violated.
5. Offline is already provable: the shell loads 32 resources, zero of them external, with all three font files served locally — so "no external calls at runtime" is measured, not asserted.
