# CLAUDE.md — how Claude works in this repo

Copied from `docs/implementation.md` §0. If this file and `docs/implementation.md` ever drift, `docs/implementation.md` is the source for this section — fix this copy.

**Source of truth order:** `docs/CID_Master_Project_Document_v2.0.md` (the master) wins over everything. `docs/prd.md` and `docs/architecture.md` turn the master into a buildable prototype. `docs/implementation.md` sequences the build. If any two of these disagree, the master wins — never resolve the conflict silently: write it in `docs/NOTES.md` under "Open questions for the team" and ask.

**Read order at the start of every session:** `docs/NOTES.md` → the current milestone in `docs/implementation.md` → the prd/architecture sections it cites. Consult the master only for the sections a task names, plus master §19 (evidence vs inference) and §04.7 (AI boundaries), which always apply.

## Working rules

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

## `docs/NOTES.md` sections (created at M0, kept updated)

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

## Human checkpoints

Some milestones end with a checkpoint. At a checkpoint, stop and give the human a short summary of what was built, how to see it, and the "what this milestone taught" note, then wait for "continue".
