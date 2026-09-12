# C.I.D. Prototype — Implementation Plan (`implementation.md`)

> **Read first:** `docs/prd.md` (what and why), `docs/architecture.md` (how). Source of truth: `docs/CID_Master_Project_Document_v2.0.md`.
> This plan is ordered so that something demoable exists as early as possible, and every milestone ends in tests that prove it works. It is written to cut debugging time: small vertical slices, typed contracts, one-command resets, and a rule to stop and write things down instead of looping.

---

## 0. How Claude works in this repo (copy into `CLAUDE.md` at M0)

**Read order at the start of every session:** `docs/NOTES.md` → the current milestone in this file → the prd/architecture sections it cites. Consult the master only for the sections a task names, plus master §19 (evidence vs inference) and §04.7 (AI boundaries), which always apply.

**Working rules**

1. **One milestone at a time.** Do not start milestone N+1 until milestone N's acceptance checks pass and the human has cleared any checkpoint.
2. **Plan before code.** At the start of a milestone, write in `NOTES.md`: the files you will create or change, the tests you will write, and anything unclear. Keep it short.
3. **Tests with the code.** Write each milestone's acceptance tests alongside the code, not after. A milestone is done only when `make test` and the milestone's acceptance commands pass.
4. **Smallest vertical slice first.** Make one record flow through a stage end to end before handling every record type.
5. **Stop after two failed attempts.** If the same error survives two fixes, stop. Write the error, what you tried, and your hypotheses in `NOTES.md` under "Stuck", and ask the human. Do not keep guessing.
6. **Never change silently:** thresholds (0.95 / 0.75), evidence classes, UI vocabulary (prd §5.8), the colour tokens, the P-decisions, or the master's schema names. If you think one is wrong, write it under "Open questions for the team".
7. **The AI writes in pencil only.** ML code may create only `AI_SUGGESTED` relationships and scores. Never write DOCUMENTED or DERIVED edges from ML code.
8. **No network at runtime.** Never add a CDN, remote font, telemetry, or an API call to an external service.
9. **No new dependencies without a note.** Prefer what `architecture.md` §3 lists. If you must add one, record it and why in `NOTES.md` under "Dependencies".
10. **Tune data, never the rules.** If a demo beat does not happen (e.g., the Raj Kumar pair is not in the review band), change the *generator's scenario* and document it. Never move thresholds or hard-code results to make the demo work.
11. **Honest labels.** Metrics are "on synthetic data". Rule-based extraction is labelled as rules. Uncalibrated risk is labelled uncalibrated.
12. **Commit per milestone** (`M4: entity resolution with review queue`), plus smaller commits within it.

**`docs/NOTES.md` sections** (create at M0, keep updated):

```
## Current milestone
## Decisions made during build        (small, local decisions with one-line reasons)
## Deviations from master/prd/arch     (what, why, who approved)
## Stuck                               (error, attempts, hypotheses)
## Open questions for the team
## Gotchas                             (things that bit us; versions; commands that work)
## Dependencies added
## What this milestone taught          (5 lines for the human, per milestone)
```

**Human checkpoints.** Some milestones end with a checkpoint. At a checkpoint, stop and give the human a short summary of what was built, how to see it, and the "what this taught" note, then wait for "continue".

---

## 1. Environment

Team machine: Pop!_OS 24.04, NVIDIA GPU, Docker, Node, Python 3.12.

| Item | Setup |
|---|---|
| GPU check | `nvidia-smi` shows the driver; note the CUDA version it supports in NOTES.md |
| Python | `uv venv --python 3.12` in `backend/`; install PyTorch with the CUDA wheel that matches the driver (e.g., `--index-url https://download.pytorch.org/whl/cu124`), then `torch_geometric`. Verify `torch.cuda.is_available()` and that `from torch_geometric.nn import HGTConv` imports. Record exact versions. |
| Node | Node 20+; `npm ci` in `frontend/` |
| Databases | `make up` (Docker Compose: Neo4j 5 Community, Postgres 16) |
| Models (once, with network) | `make models` downloads `google/muril-base-cased` and the multilingual Sentence-BERT model into `models/hf/`. After this, runtime sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. |
| Secrets | Copy `.env.example` → `.env`; generate HMAC and JWT secrets locally |

**Make targets** (built at M0, extended per milestone): `up`, `down`, `models`, `world`, `pipeline`, `dev`, `test`, `test-fast`, `reset` (drop DBs → world → pipeline → seed users/cases), `verify-offline`, `types` (regenerate TS types from OpenAPI), `lint`.

---

## 2. Milestone map

The **demo-critical path** is marked ★. If time runs short, finish every ★ milestone before any other.

| # | Milestone | Demo beats unlocked (prd §4) | Checkpoint |
|---|---|---|---|
| M0 ★ | Foundations | — | ✓ |
| M1 ★ | Synthetic world | — | ✓ |
| M2 ★ | Ingest, normalise, record store | — | |
| M3a ★ | Extraction v1 (rules) | — | |
| M4 ★ | Entity resolution + review queue data | 2, 3 (data) | ✓ |
| M5 ★ | Graph build, governed read API, audit chain | 5 (data) | |
| M6 ★ | The Case Board v1 | 2, 5, 9 (court view) | ✓ design review |
| M7 ★ | Key players and Cut | 7 | |
| M8 | Space, time and money lenses | 4, 8 | |
| M9 ★ | Anomaly model, AI suggestions, explanations, leads | 1, 5, 6 | ✓ |
| M10 ★ | Review, stamps, case packet, audit and metrics pages | 3, 9 | |
| M3b | Joint MuRIL extractor | (credibility) | |
| M11 ★ | Demo hardening | all | ✓ final |

M3b is required before the final demo but is off the critical path; it can run after M5 whenever there is GPU time.

---

## 3. Milestones

Each milestone lists: goal, build, acceptance, and (where relevant) what the human should understand.

### M0 ★ Foundations

**Goal:** an empty but real skeleton that starts with one command.

**Build**
- Repository layout exactly as `architecture.md` §4; `CLAUDE.md` from §0 above; `docs/NOTES.md`.
- `docker-compose.yml` (Neo4j, Postgres, named volumes, health checks).
- `cid/core/config.py` loads `config/cid.yaml` + `.env` into a typed settings object.
- SQL migrations as numbered files in `backend/cid/core/migrations/` with a tiny runner; all tables from architecture §5.1.
- Neo4j `schema.cypher` applied by `make up`.
- FastAPI app with `GET /api/health` reporting both databases.
- Frontend: Vite + React + TS; `tokens.css` with the prd §5.4 palette and type scale; fonts from `@fontsource` (Anek Latin/Devanagari/Tamil/Bangla, Tiro Devanagari Hindi); an empty shell with the case strip, question rail, legend and time strip placeholders; a text sample rendering "Mohammad Ali / मोहम्मद अली" in both families.
- OpenAPI → TypeScript types (`make types`, using `openapi-typescript`), so frontend and backend never drift.
- Lint config; a test that fails if any hex colour outside `tokens.css` appears in `frontend/src`.

**Acceptance**
- `make up && make test` passes from a clean clone.
- `curl localhost:8000/api/health` → both databases `ok`.
- The shell renders in the right fonts with networking disabled in the browser devtools.

**Human checkpoint:** why there are two databases (graph for relationships, Postgres for records, audit and workflow), and how config and secrets flow.

### M1 ★ Synthetic world

**Goal:** a seeded, fictional district with known answers (prd §7).

**Build**
- `generate/names.py`: people with variant renderings (spelling, abbreviation, Devanagari via reverse transliteration, a few Tamil/Bengali forms, formal-surname swaps).
- `generate/networks.py`: N1 shell chain around Person A, N2 mule fan-out, N3 burner tree + night ring, plus ~30 background networks of the same kinds with varied sizes and timing.
- `generate/lookalikes.py`: payroll fan-out, shared family phone, daytime co-workers, legitimate holding company.
- `generate/narratives.py`: FIR narratives from template families (English + Romanised Hindi; IPC and BNS sections), recording gold spans and relations with character offsets. Mark families as train or held-out.
- Identity traps: Mohammad Ali in four sources and scripts; two different Raj Kumars (same name key, similar context, different DOB and phone); Chatterjee / Chaterjee / Chattopadhyay; Azhagiri / Alagiri.
- Demo case: Case 0231 anchored on FIR 224/2025 naming Person C; demo users from prd §3.
- `truth.json`: true identities, mention → identity map, network memberships, gold spans/relations, look-alike labels.
- `make world-report` prints counts, script mix, IPC/BNS mix, and network summary.

**Acceptance (tests)**
- Two runs with the same seed produce byte-identical files (hash comparison).
- `truth.json` has N1–N3 and ≥ 30 background networks; each has a typology label.
- All four Mohammad Ali surface forms exist, in four different sources.
- The two Raj Kumars have different DOBs and phones.
- At least 10% of person mentions are in Devanagari; both IPC and BNS codes appear.
- Every gold span satisfies `text[start:end] == surface`.

**Human checkpoint:** read `world-report`; skim 5 FIRs; confirm the scenarios look believable and are clearly fictional.

### M2 ★ Ingest, normalise, record store

**Build:** loaders for every source → `source_records` (with `legal_basis`, `auth_tier`, `ingested_at`, `record_hash`); normalisers (phones → E.164 → HMAC; dates → UTC + source tz; offence codes → ontology IDs; addresses → `address_key`); structured sources produce mentions and relations directly.

**Acceptance**
- Unit tests for each normaliser (phone formats +91 / 0 / 10-digit; mixed IPC/BNS sample; time zones).
- Row counts match the world report.
- Re-ingesting gives identical `record_hash` values.
- A record without legal basis is rejected and counted.
- No raw phone or account number appears anywhere in the graph-bound tables (test scans them).

### M3a ★ Extraction v1 (rules)

**Build:** the `Extractor` interface; `rules.py` (gazetteers + patterns) for FIR narratives; writes `mentions` and `relation_mentions` with offsets and confidence; "through account X" → `MENTIONED_WITH`, never `OWNS` (architecture §6.3); `metrics/nlp.py` computes entity and relation F1 on **held-out template families**.

**Acceptance**
- Offsets valid for 100% of mentions.
- Metrics written to `runs/<run_id>/metrics.json`, labelled `extractor: rules`.
- The Amit example from master §10.4 produces a transfer relation and a `MENTIONED_WITH`, not ownership.

### M4 ★ Entity resolution

**Build:** `indic_key.py` with the unit tests listed in architecture §6.4; `candidates.py` (including SBERT context embeddings); `splink_model.py` (blocking, comparisons, EM, predict); `decide.py` (three tiers, union-find, conflict check); `er_pairs` rows for the review band; golden entity output (master §11.10 contract); `metrics/er.py` (pairwise precision, recall, F1, false-merge count vs truth).

**Acceptance**
- `indic_key` tests pass for all four trap families.
- The four Mohammad Ali mentions resolve to one entity with `resolution_confidence ≥ 0.95` and evidence in words ("same phone", "sounds alike", "same birth date").
- The two Raj Kumars are **not** merged. For demo beat 3 they should appear as a review-band pair; if they don't, adjust the generator scenario (rule 10), never the thresholds.
- No cluster violates the conflict check.
- ER precision, recall and false merges are reported. Master target for precision is > 0.98; report the actual number either way.

**Human checkpoint:** walk through one auto-merge and one review pair; understand blocking, Fellegi-Sunter weights, and why false merges are worse than false splits (master §11.9).

### M5 ★ Graph build, governed read API, audit chain

**Build**
- `graph_build/writer.py` with the provenance guard; person-level derivations; `ASSOCIATED_WITH` basis rules.
- Governance first: `auth.py` (demo users, JWT), `policy.py`, `middleware.py`, `audit_chain.py` (hash chain + seals + verify). Every route goes through it from day one.
- Routes: `/auth/login`, `/cases`, `/graph/case`, `/graph/expand`, `/entities/{id}`, `/records/{id}`, `/why` (documented and derived sections for now), `/audit/verify`.
- Graph payload per architecture §7.3, including tooltips (template sentences), bundling, `CALLED` aggregation for display.

**Acceptance (tests)**
- Every DOCUMENTED edge has a `source_record_id` found in Postgres (Cypher + SQL check).
- A case-scoped request without `X-Case-Id` or with the wrong legal basis → 403 with the prd message, and an audit entry with `outcome=refused`.
- `io.patil` cannot read another case.
- `/audit/verify` passes; editing one `audit_log` row in SQL makes it fail at that `seq`.
- Case graph p95 < 1 s over 50 requests on the full world.

### M6 ★ The Case Board v1

**Goal:** the experience in prd §5 with the data available so far. This is where the prototype starts to look like C.I.D.

**Build**
- Login; Today's leads page (shows the empty state until M9: "No leads yet. Run the pipeline to generate leads." plus a link to open Case 0231 directly).
- Case page: case strip, caption (pure `caption.ts` with tests), question rail (network lens active; others disabled with "Coming soon" tooltips until M7/M8), legend, time strip placeholder.
- Board: one Cytoscape instance, `applyGraph` diffing, full `styles.ts` mapping (ink, dotted, pencil styles ready even if no pencil data yet), entity shapes, crowd bundles, selection dimming, hover tooltips, floating verbs (*Show who else*, *Why?*, *Cut* disabled until M7).
- *Why?* drawer with the three sections, Tiro excerpts and highlighter spans, *Open record* sheet.
- Identity stack (ghost edges, "4 records") and the fan-out with match chips; identity collapse animation on first open.
- Court view toggle (client hides non-documented edges; the prosecutor's API filtering comes in M10).
- Keyboard map from prd §5.9; reduced-motion handling.

**Acceptance**
- Vitest: `caption.ts`, `wobble.ts` (stable per ID), style selector coverage (each evidence class maps to a distinct `line-style`).
- Manual checklist (write it in NOTES.md and tick it): demo beats 2 and 5 work; Court view hides dotted and pencil lines; no colour outside tokens; Devanagari names render in both families; focus ring visible everywhere.
- Screenshots of the board, drawer and identity fan saved to `docs/screens/M6/`.

**Human checkpoint — design review.** Look at the screenshots against prd §5. Is the ink / dotted / pencil / stamp language instantly readable? Does anything look like a generic dashboard? Adjust before building more UI on top of it.

### M7 ★ Key players and Cut

**Build:** `analytics/subgraph.py`, `centrality.py`, `communities.py`, `kpp.py` (greedy + swap), `cut.py`; `/analytics/keyplayers`, `/analytics/cut`; key-player lens; the Cut flow in prd §5.6.5 (preview marks, confirm, drift into islands, island labels, result sentence, fixed caveat, undo).

**Acceptance**
- On N1, Person A is in the KPP-1 top 2 but not in the top 5 by degree (test).
- Cut results are deterministic for the same input and seed.
- The result sentence and the caveat always appear together.
- Demo beat 7 works end to end.

### M8 Space, time and money lenses

**Build:** `spatiotemporal/copresence.py` (P-14) writing DERIVED `CO_LOCATED_WITH` with `derived_from` and `method`; `direct_calls` per pair; `/graph/at?date=`; lenses: money (with `keptShare`), time (swim-lanes), place (tower circles, no base map); replay strip with activity trace and play.

**Acceptance**
- The N3 night ring produces `CO_LOCATED_WITH` edges with frequency ≥ 4 and night share ≥ 0.6 and zero direct calls.
- The daytime co-worker look-alike does not match T-05 (night share below threshold).
- Money lens shows N1's chain left to right with kept shares < 10%.
- Replay at an early date shows fewer entities than at the end (test on `/graph/at`).
- Demo beats 4 and 8 work.

### M9 ★ Anomaly model, AI suggestions, explanations, leads

**Build**
- `ml/features.py`, `hetero_data.py` (documented + derived edges only; `edge_id` arrays), `hgt.py`, `train_hgt.py` (split by network; N1–N3 in test), `registry.py`.
- `linkpred.py` (Hits@10, MRR; suggestions → `AI_SUGGESTED`, max 5 per case).
- `explain.py` (GNNExplainer; occlusion fallback; fidelity before/after).
- `detect/typologies.py` (T-01, T-02/T-03, T-04, T-05, T-08), `risk.py` (P-07), `leads.py` + `templates.py` (titles, why-sentences, fixed "does not show" lists), supervisor pending state (P-06).
- API: `/leads`, `/leads/{id}/decision`, `/suggestions/{id}/erase`, `/suggestions/{id}/pin`; `/why` gains AI and fidelity sections.
- UI: real Today's leads with evidence tallies; pencil lines on the board; *Pin a record* (record picker limited to the case's records) and *Erase* (reason) with stamps; "Show erased".

**Acceptance (tests)**
- N1, N2 and N3 each produce a lead of the right typology; look-alikes do not produce top-5 leads (report if any do).
- Every GNN-based lead has an evidence subgraph and a fidelity pair.
- Cypher check: zero relationships with `evidence_class='INFERRED'` outside the `AI_SUGGESTED` type; zero `AI_SUGGESTED` edges in the HGT training data.
- Pin with a record that does not state the link → 422 with the prd message; pin with a stating record → a new DOCUMENTED edge, and the suggestion is kept as `pinned` history.
- Metrics written: precision@10, AUC-PR (anomaly), Hits@10, MRR (links), mean fidelity; the model version and run ID are on every lead.
- Demo beats 1, 5 (with fidelity) and 6 work.

**Human checkpoint:** understand what HGT learns from typed edges, why the split is by network, what fidelity does and does not mean (master C-19), and why suggestions can never become ink by clicking.

### M10 ★ Review, stamps, case packet, audit and metrics pages

**Build:** review queue page (supervisor; `S` / `D` keys); `/review/{pair_id}` updates entities and graph; `/entities/{id}/split`; stamps rendered on the board and in drawers; case file and *Build case packet* (three sections, hashes, model versions, audit excerpt, cover note); prosecutor role with server-side DOCUMENTED-only filtering and locked Court view; audit page with *Verify chain*; metrics page with the synthetic-data note.

**Acceptance (tests)**
- Review "Same person" merges and redraws; "Different people" keeps them apart; both stamp and audit.
- Split restores the pre-merge entities and their edges.
- Packet `manifest.json` hashes verify; the AI section is separate and labelled "investigative leads, not evidence".
- Every graph payload for `prosecutor.rao` contains zero DERIVED or INFERRED edges.
- Audit page shows "Verified"; after a manual SQL edit it shows the first broken entry.
- Demo beats 3 and 9 work.

### M3b Joint MuRIL extractor

**Build:** `muril_joint.py` (MuRIL encoder; BIO head; span-pair relation head; joint loss), `train_muril.py` (train on training families; early stopping on validation families; mixed precision on GPU); switch via `config.extract.backend: muril`; re-run the pipeline from extraction onward.

**Acceptance:** entity and relation F1 on held-out families reported next to the rules extractor, both labelled; the demo still passes with `backend: muril`. If the joint model underperforms the rules extractor on held-out families, keep it selectable and say so on the metrics page — do not hide either number.

### M11 ★ Demo hardening

**Build and check**
- `make reset` then the full demo story (prd §4) twice, timing each beat; fix anything that needs a terminal.
- `make verify-offline` passes.
- Reduced-motion pass; keyboard-only pass; 1280 px width pass.
- Performance: board interactions feel instant; case graph p95 < 1 s; pipeline < 20 min (report actual).
- Playwright test for the story (`STRETCH`).
- `README.md`: how to run the demo from a clean machine in under 10 commands.

**Final checkpoint:** the team runs the demo without Claude's help.

---

## 4. Testing strategy

| Layer | What | Where |
|---|---|---|
| Unit | Normalisers, `indic_key`, KPP fragmentation on toy graphs, risk/confidence rules, audit hashing, caption and wobble functions | `backend/tests/unit`, `frontend/src/**/*.test.ts` |
| Golden | Tiny fixture world (seed `7`, 60 people, one of each network) with expected ER clusters, typology hits and cut results committed as JSON | `backend/tests/golden` — runs in `make test-fast` (< 60 s) |
| Invariants | Must never break: provenance on DOCUMENTED edges; no INFERRED outside `AI_SUGGESTED`; prosecutor filtering; 403 without case; audit chain verifies; same seed ⇒ same leads | `backend/tests/invariants` — run on every `make test` |
| Contract | API responses validate against Pydantic models; TS types regenerated from OpenAPI (`make types`) and type-checked in CI | both |
| Metrics | Metrics are computed and within sane ranges (e.g., 0 ≤ F1 ≤ 1, counts > 0) — **not** asserted against master targets | `backend/tests/metrics` |
| End to end | Demo story (Playwright, `STRETCH`) | `frontend/e2e` |

---

## 5. Practices that cut debugging time

1. **Generated types.** Never hand-write TS types for API payloads; regenerate from OpenAPI after any API change.
2. **One-command reset.** `make reset` rebuilds everything from the seed. Don't debug a half-migrated database; reset it.
3. **Small fixture world.** Develop and test against the seed-7 fixture world (seconds), then run the full world.
4. **Inspectable stage outputs.** Every pipeline stage writes a JSON summary to `runs/<run_id>/`; when something looks wrong on the board, check the stage summaries before reading code.
5. **Structured logs.** JSON logs with `run_id` and `request_id`; the API returns `request_id` in a header so a UI error can be traced to one log line.
6. **Pin versions once.** Especially PyTorch ↔ CUDA ↔ PyG and Cytoscape. Record them in NOTES.md "Gotchas".
7. **Treat Cytoscape style warnings as errors** in development (it logs invalid style properties to the console).
8. **Stop and write** (rule 5 in §0). Most long debugging loops are a wrong assumption that becomes obvious once written down.

---

## 6. Risks and fallbacks

| Risk | Early sign | Fallback (same output contract) |
|---|---|---|
| Heterogeneous GNNExplainer unsupported in the installed PyG version | Error on `Explainer(...)` with `HeteroData` | Occlusion explainer (architecture §6.8); note in NOTES.md |
| Splink 4 API friction | Blocking or EM errors not solved in two attempts | Hand-written Fellegi-Sunter + EM over the same comparison vectors |
| DuckDB `list_cosine_similarity` comparison fails in Splink | SQL error | Precompute bucketed context similarity for blocked pairs and feed it as a column |
| MuRIL joint training slow or unstable | Loss not falling after 2 epochs | Keep rules extractor as default; report both; reduce max length / freeze lower layers |
| Cytoscape lacks `underlay-*` / node `ghost` in the pinned version | Style warnings | Extra background node for highlight; duplicate offset node for stack |
| HGT overfits synthetic features | Perfect val scores | Remove generator-leaking features (anything computed from truth); report honestly |
| Too many leads from look-alikes | Look-alikes in top 5 | Improve features or typology conditions; never delete look-alikes from the world |
| Board too slow | Pan/zoom lag | Lower `max_nodes`, raise bundling, `textureOnViewport` |
| Font coverage gap (e.g., rare conjuncts) | Tofu boxes | Add the matching Anek script subset; keep Tiro only for Devanagari/Latin records |

---

## 7. Running the demo

**Before:** `make reset` → `make dev` → open `http://localhost:5173/login` at 100% zoom → log in once as each demo user to warm caches → log out → disconnect the network.

**During:** follow prd §4 beat by beat. One honest line per beat is enough, for example:
- Beat 2: "Four records, four spellings, two scripts — one person. The match reasons are shown; nothing is hidden."
- Beat 5: "Every line opens the record behind it."
- Beat 6: "The AI can only suggest in pencil. Only a record can make it ink."
- Beat 7: "This shows structure, not what the group would do next."
- Beat 9: "Court view shows only what is on record. The audit chain proves nothing was changed."

**Backup:** a screen recording of a full run, made at M11.

---

## 8. Definition of done

- Every ★ milestone's acceptance checks pass; M3b done or its status stated on the metrics page.
- The demo story runs twice in a row from `make reset`, offline.
- `NOTES.md` is current: deviations approved, no open "Stuck" items.
- The metrics page shows every metric with run ID and seed and the synthetic-data note.
- Nothing in the UI or packet uses the words the prd forbids (§12); a grep test checks the frontend copy for "proof", "guilty", "confirmed", "GPS", "100% offline", "tamper-proof".
