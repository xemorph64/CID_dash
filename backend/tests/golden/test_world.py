"""M1 acceptance tests (implementation.md M1) — run against a small but
complete world: every demo/background network, every look-alike and every
identity trap present, sized down only on FIR/CDR/txn volume for speed.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from cid.pipeline.generate.world import WorldProfile, generate_world

BACKEND_DIR = Path(__file__).resolve().parents[2]

SMALL_PROFILE = WorldProfile(
    seed=20260310,
    people=2100,
    firs=150,
    cdr_rows=600,
    txns=600,
    towers=10,
    accounts=1500,
    phone_regs=600,
    companies=40,
    vehicles=40,
    background_networks=30,
    synthetic_threshold_inr=50_000,
    start_date=datetime.date(2025, 1, 1),
    end_date=datetime.date(2026, 5, 15),
    history_days=1000,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_dir(d: Path) -> dict[str, str]:
    return {p.name: _sha256(p) for p in sorted(d.iterdir()) if p.is_file()}


def _generate(tmp_path: Path, name: str) -> Path:
    out_dir = tmp_path / name
    generate_world(out_dir, SMALL_PROFILE)
    return out_dir


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


# Every source record type's single free-text name field, keyed by
# source_record_id prefix. A KYC/phone_reg/company record holds exactly one
# name in this field — the field the ground truth must agree with.
_NAME_FIELD_BY_PREFIX = {
    "KYC_": "holder_name",
    "PHONEREG_": "subscriber_name",
    # COMPANY_ has no single name field (directors is a list); handled separately.
}


def test_byte_identical_regeneration(tmp_path):
    dir_a = _generate(tmp_path, "a")
    dir_b = _generate(tmp_path, "b")
    hashes_a = _hash_dir(dir_a)
    hashes_b = _hash_dir(dir_b)
    assert hashes_a == hashes_b
    assert hashes_a  # not empty


def test_byte_identical_across_pythonhashseed(tmp_path):
    script = (
        f"import sys; sys.path.insert(0, {str(BACKEND_DIR)!r}); "
        "import datetime; from pathlib import Path; "
        "from cid.pipeline.generate.world import WorldProfile, generate_world; "
        "profile = WorldProfile(seed=20260310, people=2100, firs=150, cdr_rows=600, txns=600, towers=10, "
        "accounts=1500, phone_regs=600, companies=40, vehicles=40, background_networks=30, "
        "synthetic_threshold_inr=50000, start_date=datetime.date(2025,1,1), end_date=datetime.date(2026,5,15), "
        "history_days=1000); "
        "generate_world(Path(sys.argv[1]), profile)"
    )

    def run(hashseed: str, out_name: str) -> dict[str, str]:
        out_dir = tmp_path / out_name
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        subprocess.run([sys.executable, "-c", script, str(out_dir)], env=env, check=True, cwd=BACKEND_DIR)
        return _hash_dir(out_dir)

    hashes_0 = run("0", "hashseed0")
    hashes_1 = run("1", "hashseed1")
    assert hashes_0 == hashes_1
    assert hashes_0


def test_truth_has_demo_and_background_networks_with_typologies(tmp_path):
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    by_id = {n["structure_id"]: n for n in truth["networks"]}

    for sid in ("N1", "N2", "N3"):
        assert sid in by_id
        assert by_id[sid]["typologies"], f"{sid} must carry a typology label"

    background = [n for n in truth["networks"] if n["role"] == "background"]
    assert len(background) >= 30
    for n in background:
        assert n["typologies"], f"{n['structure_id']} must carry a typology label"


def test_mohammad_ali_four_surfaces_four_sources(tmp_path):
    """Ground truth that disagrees with the record it describes is worse
    than no ground truth — so this checks the four surfaces are what the
    emitted record itself says, not just what truth.json claims."""
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    ma_id = "PERSON_900001"
    assert truth["true_identities"][ma_id]["canonical_name"] == "Mohammad Ali"

    firs = {f["source_record_id"]: f for f in _read_jsonl(out_dir / "firs.jsonl")}
    accounts = {a["source_record_id"]: a for a in _read_jsonl(out_dir / "accounts.jsonl")}
    phones = {p["source_record_id"]: p for p in _read_jsonl(out_dir / "phone_regs.jsonl")}
    companies = {c["source_record_id"]: c for c in _read_jsonl(out_dir / "companies.jsonl")}

    ma_mentions = [m for m in truth["mentions"] if m["person_id"] == ma_id]
    by_surface = {m["surface"]: m for m in ma_mentions}
    expected = {"Mohammad Ali", "Mohd Ali", "Md. Ali", "मोहम्मद अली"}
    assert expected == set(by_surface)

    fir_id = next(rid for rid in firs if rid in {m["source_record_id"] for m in ma_mentions})
    assert by_surface["Mohammad Ali"]["source_record_id"] == fir_id
    text = firs[fir_id]["text"]
    span = next(
        s for s in truth["firs"][fir_id]["spans"] if s["surface"] == "Mohammad Ali"
    )
    assert text[span["start"] : span["end"]] == "Mohammad Ali"

    kyc_id = by_surface["Mohd Ali"]["source_record_id"]
    assert accounts[kyc_id]["holder_name"] == "Mohd Ali"

    phone_id = by_surface["Md. Ali"]["source_record_id"]
    assert phones[phone_id]["subscriber_name"] == "Md. Ali"

    company_id = by_surface["मोहम्मद अली"]["source_record_id"]
    director_surfaces = {d["surface"] for d in companies[company_id]["directors"]}
    assert "मोहम्मद अली" in director_surfaces

    # And no (record, field) pair is holding more than one mention for him.
    assert len({m["source_record_id"] for m in ma_mentions}) == len(ma_mentions)


def test_raj_kumars_differ_in_dob_and_phone(tmp_path):
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    rk1 = truth["true_identities"]["PERSON_900002"]
    rk2 = truth["true_identities"]["PERSON_900003"]
    assert rk1["dob"] != rk2["dob"]

    phone_regs = [
        json.loads(line) for line in (out_dir / "phone_regs.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    rk1_msisdns = {
        p["msisdn"]
        for p in phone_regs
        if any(m["person_id"] == "PERSON_900002" and m["source_record_id"] == p["source_record_id"] for m in truth["mentions"])
    }
    rk2_msisdns = {
        p["msisdn"]
        for p in phone_regs
        if any(m["person_id"] == "PERSON_900003" and m["source_record_id"] == p["source_record_id"] for m in truth["mentions"])
    }
    assert rk1_msisdns and rk2_msisdns
    assert rk1_msisdns.isdisjoint(rk2_msisdns)


def test_devanagari_share_and_ipc_bns_mix(tmp_path):
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    mentions = truth["mentions"]
    assert mentions
    deva_count = sum(1 for m in mentions if m["script"] == "Deva")
    assert deva_count / len(mentions) >= 0.10

    firs = [json.loads(line) for line in (out_dir / "firs.jsonl").read_text(encoding="utf-8").splitlines()]
    systems = {f["offence_code_system"] for f in firs}
    assert systems == {"IPC", "BNS"}


def test_every_gold_span_matches_fir_text(tmp_path):
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    firs_by_id = {
        f["source_record_id"]: f
        for f in (json.loads(line) for line in (out_dir / "firs.jsonl").read_text(encoding="utf-8").splitlines())
    }

    checked = 0
    for source_record_id, fir_truth in truth["firs"].items():
        text = firs_by_id[source_record_id]["text"]
        for span in fir_truth["spans"]:
            assert text[span["start"] : span["end"]] == span["surface"]
            checked += 1
    assert checked > 0


def test_demo_case_anchor_names_an_n1_member(tmp_path):
    """prd §5.5's caption and §4 beat 1's top lead only work if the case
    graph (built by walking 2 hops from FIR 224/2025) actually reaches N1 —
    so the FIR's accused must be an N1 member, not an unrelated person."""
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))

    n1 = next(n for n in truth["networks"] if n["structure_id"] == "N1")
    person_c_id = truth["demo_case"]["person_c_id"]
    assert person_c_id in n1["person_ids"]

    demo_fir_id = truth["demo_case"]["anchor_record_id"]
    demo_mentions = [m for m in truth["mentions"] if m["source_record_id"] == demo_fir_id]
    assert any(m["person_id"] == person_c_id for m in demo_mentions)


def test_every_mention_surface_occurs_in_its_own_source_record(tmp_path):
    """Ground truth that disagrees with the data it describes is worse than
    no ground truth. For FIRs, the surface must match at the recorded gold
    span's offsets (already covered above, repeated here for structured
    records too); for KYC/phone_reg, it must be the record's own name field.
    """
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    firs = {f["source_record_id"]: f for f in _read_jsonl(out_dir / "firs.jsonl")}
    accounts = {a["source_record_id"]: a for a in _read_jsonl(out_dir / "accounts.jsonl")}
    phones = {p["source_record_id"]: p for p in _read_jsonl(out_dir / "phone_regs.jsonl")}
    companies = {c["source_record_id"]: c for c in _read_jsonl(out_dir / "companies.jsonl")}

    checked = 0
    for m in truth["mentions"]:
        rid = m["source_record_id"]
        if rid in firs:
            span = next(s for s in truth["firs"][rid]["spans"] if s["slot"] == m["field"])
            assert firs[rid]["text"][span["start"] : span["end"]] == m["surface"], rid
        elif rid in accounts:
            assert accounts[rid]["holder_name"] == m["surface"], rid
        elif rid in phones:
            assert phones[rid]["subscriber_name"] == m["surface"], rid
        elif rid in companies:
            director_surfaces = {d["surface"] for d in companies[rid]["directors"]}
            assert m["surface"] in director_surfaces, rid
        else:
            raise AssertionError(f"mention references unknown record {rid}")
        checked += 1
    assert checked == len(truth["mentions"]) > 0


def test_single_valued_fields_carry_one_mention_each(tmp_path):
    """A KYC/phone_reg record has exactly one holder/subscriber name field —
    it cannot say two things, so no (source_record_id, field) pair for those
    record types may appear more than once in truth.json's mentions."""
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))
    counts: dict[tuple[str, str], int] = {}
    for m in truth["mentions"]:
        prefix = next((p for p in _NAME_FIELD_BY_PREFIX if m["source_record_id"].startswith(p)), None)
        if prefix is None:
            continue
        key = (m["source_record_id"], m["field"])
        counts[key] = counts.get(key, 0) + 1
    dupes = {k: v for k, v in counts.items() if v > 1}
    assert dupes == {}


def test_no_bulk_person_collides_with_a_trap(tmp_path):
    """prd §4 beat 3 needs exactly two "Raj Kumar"s; a bulk-generated person
    who happens to share a trap's canonical name would also share its
    surfaces (variants_for() is a pure function of the name), giving a third
    entrant to a search meant to show only two."""
    out_dir = _generate(tmp_path, "world")
    truth = json.loads((out_dir / "truth.json").read_text(encoding="utf-8"))

    trap_ids = {"PERSON_900001", "PERSON_900002", "PERSON_900003", "PERSON_900004", "PERSON_900005"}
    trap_names = {truth["true_identities"][pid]["canonical_name"] for pid in trap_ids}
    trap_surfaces = {
        (s["surface"], s["script"])
        for pid in trap_ids
        for s in truth["true_identities"][pid]["surfaces"]
    }

    for person_id, identity in truth["true_identities"].items():
        if person_id in trap_ids:
            continue
        assert identity["canonical_name"] not in trap_names, person_id
        surfaces = {(s["surface"], s["script"]) for s in identity["surfaces"]}
        assert surfaces.isdisjoint(trap_surfaces), person_id
