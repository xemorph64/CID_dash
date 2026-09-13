"""Assembles `truth.json` — the ground truth everything downstream (M2-M9)
is scored against. Pure data assembly: no randomness, no I/O (world.py writes
the result). Every set-derived value is sorted before it lands here, so the
JSON is stable across `PYTHONHASHSEED` (world.py's determinism requirement).
"""

from __future__ import annotations

from typing import Any

from cid.pipeline.generate.names import TruePerson
from cid.pipeline.generate.specs import WorldOutput


def _iso(d: Any) -> Any:
    return d.isoformat() if hasattr(d, "isoformat") else d


def build_truth(
    output: WorldOutput,
    *,
    seed: int,
    all_people: list[TruePerson],
    person_surfaces: dict[str, set[tuple[str, str]]],
    fir_truth: dict[str, dict],
    missing_legal_basis_ids: list[str],
    demo_case: dict,
) -> dict:
    true_identities: dict[str, dict] = {}
    for person in all_people:
        surfaces = sorted(person_surfaces.get(person.person_id, set()))
        true_identities[person.person_id] = {
            "canonical_name": person.canonical_name,
            "dob": _iso(person.dob),
            "home_town": person.home_town,
            "surfaces": [{"surface": s, "script": sc} for s, sc in surfaces],
        }

    networks = [
        {
            "structure_id": s.structure_id,
            "kind": s.kind,
            "typologies": list(s.typologies),
            "role": s.role,
            "is_criminal": s.is_criminal,
            "note": s.note,
            "person_ids": list(s.person_ids),
            "account_ids": list(s.account_ids),
            "org_ids": list(s.org_ids),
            "phone_ids": list(s.phone_ids),
        }
        for s in output.structures
    ]

    mentions = [
        {
            "source_record_id": m.source_record_id,
            "field": m.field,
            "surface": m.surface,
            "script": m.script,
            "person_id": m.person_id,
        }
        for m in output.mentions
    ]

    return {
        "seed": seed,
        "true_identities": true_identities,
        "mentions": mentions,
        "networks": networks,
        "firs": fir_truth,
        "missing_legal_basis_ids": sorted(missing_legal_basis_ids),
        "demo_case": demo_case,
    }
