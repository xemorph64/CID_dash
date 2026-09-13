"""Human-readable summary of a generated world. Runnable as
`python -m cid.pipeline.generate.report` (this is `make world-report`).

Reads `data/world/*` and prints counts per source, the script mix of person
mentions, the IPC/BNS mix, and a network summary — plain text for a human to
skim at the M1 checkpoint (implementation.md M1).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from cid.core.config import REPO_ROOT

JSONL_SOURCES = [
    "firs.jsonl",
    "cdr.jsonl",
    "txns.jsonl",
    "accounts.jsonl",
    "phone_regs.jsonl",
    "companies.jsonl",
    "vehicles.jsonl",
    "towers.jsonl",
]


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _read_json(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_report(world_dir: Path) -> str:
    lines: list[str] = []
    lines.append(f"World report: {world_dir}")
    lines.append("")

    lines.append("Counts per source")
    for name in JSONL_SOURCES:
        records = _read_jsonl(world_dir / name)
        lines.append(f"  {name:<20} {len(records)}")
    cases = _read_json(world_dir / "cases.json") or []
    users = _read_json(world_dir / "users.json") or []
    lines.append(f"  {'cases.json':<20} {len(cases)}")
    lines.append(f"  {'users.json':<20} {len(users)}")
    lines.append("")

    truth = _read_json(world_dir / "truth.json") or {}

    mentions = truth.get("mentions", [])
    script_counts = Counter(m["script"] for m in mentions)
    total_mentions = sum(script_counts.values())
    lines.append(f"Script mix of person mentions ({total_mentions} total)")
    for script, count in sorted(script_counts.items()):
        pct = 100 * count / total_mentions if total_mentions else 0.0
        lines.append(f"  {script:<6} {count:>6}  ({pct:.1f}%)")
    lines.append("")

    firs = _read_jsonl(world_dir / "firs.jsonl")
    code_counts = Counter(f["offence_code_system"] for f in firs)
    total_firs = sum(code_counts.values())
    lines.append(f"IPC/BNS mix ({total_firs} FIRs)")
    for system, count in sorted(code_counts.items()):
        pct = 100 * count / total_firs if total_firs else 0.0
        lines.append(f"  {system:<4} {count:>6}  ({pct:.1f}%)")
    lines.append("")

    networks = truth.get("networks", [])
    lines.append(f"Network summary ({len(networks)} structures)")
    for n in networks:
        size = len(n["person_ids"]) + len(n["account_ids"]) + len(n["org_ids"]) + len(n["phone_ids"])
        typ = ",".join(n["typologies"]) if n["typologies"] else "-"
        lines.append(f"  {n['structure_id']:<18} {n['kind']:<18} typologies={typ:<10} role={n['role']:<11} size={size}")
    lines.append("")

    missing = truth.get("missing_legal_basis_ids", [])
    lines.append(f"Records with no legal_basis (deliberate): {len(missing)}")
    for rid in missing:
        lines.append(f"  {rid}")

    return "\n".join(lines)


def main() -> None:
    print(build_report(REPO_ROOT / "data" / "world"))


if __name__ == "__main__":
    main()
