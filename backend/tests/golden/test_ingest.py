"""M2 acceptance tests (implementation.md M2). Runs against the live Postgres
(`make up`) and the generated `data/world/` (`make world`).
"""

from __future__ import annotations

import json

import pytest

from cid.core.db_pg import get_connection
from cid.pipeline.ingest.load import SOURCES, WORLD_DIR, _iter_jsonl, load


def _read_jsonl(filename: str) -> list[dict]:
    return list(_iter_jsonl(WORLD_DIR / filename))


def _truth() -> dict:
    return json.loads((WORLD_DIR / "truth.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def loaded() -> dict[str, int]:
    return load()


def test_row_counts_match_world_report(loaded):
    with get_connection() as conn, conn.cursor() as cur:
        for record_type, filename in SOURCES:
            rows = _read_jsonl(filename)
            expected = sum(1 for r in rows if r.get("legal_basis"))
            cur.execute("SELECT count(*) FROM source_records WHERE record_type = %s", (record_type,))
            actual = cur.fetchone()[0]
            assert actual == expected == loaded[record_type], record_type


def test_reingest_gives_identical_hashes_and_no_duplicates(loaded):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT source_record_id, record_hash FROM source_records")
        before = dict(cur.fetchall())

    load()

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT source_record_id, record_hash FROM source_records")
        after = dict(cur.fetchall())

        cur.execute(
            "SELECT source_record_id, count(*) FROM source_records GROUP BY source_record_id HAVING count(*) > 1"
        )
        assert cur.fetchall() == []

        cur.execute("SELECT mention_id, count(*) FROM mentions GROUP BY mention_id HAVING count(*) > 1")
        assert cur.fetchall() == []

        cur.execute("SELECT id, count(*) FROM relation_mentions GROUP BY id HAVING count(*) > 1")
        assert cur.fetchall() == []

    assert after == before
    assert after  # not empty


def test_missing_legal_basis_records_rejected_and_counted(loaded):
    truth = _truth()
    missing_ids = truth["missing_legal_basis_ids"]
    assert missing_ids  # the world generator promises 5

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT source_record_id FROM source_records WHERE source_record_id = ANY(%s)", (missing_ids,)
        )
        assert cur.fetchall() == []

        cur.execute(
            "SELECT source_record_id FROM ingest_rejects WHERE source_record_id = ANY(%s)", (missing_ids,)
        )
        rejected_ids = {row[0] for row in cur.fetchall()}
        assert rejected_ids == set(missing_ids)


def test_no_raw_phone_or_account_number_in_graph_bound_tables(loaded):
    raw_msisdns = {r["msisdn"] for r in _read_jsonl("phone_regs.jsonl")}
    raw_account_nos = {r["account_no"] for r in _read_jsonl("accounts.jsonl")}
    raw_values = raw_msisdns | raw_account_nos
    assert raw_values  # the adversarial set must be non-empty to mean anything

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT surface FROM mentions")
        mention_surfaces = {row[0] for row in cur.fetchall()}

        cur.execute("SELECT rel_type FROM relation_mentions")
        relation_values = {row[0] for row in cur.fetchall()}  # no text/surface column exists to leak into

        cur.execute("SELECT canonical_name FROM entities")
        entity_names = {row[0] for row in cur.fetchall()}

    assert mention_surfaces.isdisjoint(raw_values)
    assert relation_values.isdisjoint(raw_values)
    assert entity_names.isdisjoint(raw_values)


def test_normalizers_exercised_through_real_records(loaded):
    truth = _truth()
    with get_connection() as conn, conn.cursor() as cur:
        # phones.py + hashing.hmac_id, via a real phone_reg record.
        phone_reg = next(iter(_read_jsonl("phone_regs.jsonl")))
        cur.execute(
            "SELECT normalized FROM source_records WHERE source_record_id = %s", (phone_reg["source_record_id"],)
        )
        normalized = cur.fetchone()[0]
        assert normalized["msisdn_hash"]
        assert normalized["subscriber_name_normalized"]  # names.py

        # dates.py, via a real CDR record.
        cdr = next(iter(_read_jsonl("cdr.jsonl")))
        cur.execute("SELECT normalized FROM source_records WHERE source_record_id = %s", (cdr["source_record_id"],))
        normalized = cur.fetchone()[0]
        assert normalized["ts"]["source_tz"] == "Asia/Kolkata"
        assert normalized["ts"]["utc"]

        # offences.py, via the demo FIR (IPC 406 -> criminal_breach_of_trust).
        cur.execute("SELECT normalized FROM source_records WHERE source_record_id = %s", ("FIR_DEMO_0224",))
        normalized = cur.fetchone()[0]
        assert normalized["offence"] == {
            "code_system": "IPC",
            "section": "406",
            "ontology_id": "criminal_breach_of_trust",
        }

        # addresses.py, via a real company record.
        company = next(iter(_read_jsonl("companies.jsonl")))
        cur.execute(
            "SELECT normalized FROM source_records WHERE source_record_id = %s", (company["source_record_id"],)
        )
        normalized = cur.fetchone()[0]
        assert normalized["address_key"]

    assert truth  # sanity: truth.json loaded fine alongside the DB checks above
