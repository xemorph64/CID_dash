"""Ingest loader (architecture §6.2). Run with `python -m cid.pipeline.ingest.load`.

Every record in `data/world/*.jsonl` becomes a `source_records` row, unless it
has no `legal_basis` — that goes to `ingest_rejects` instead and is never
stored (architecture §6.2: "reject any record without legal_basis"). Structured
sources (everything but FIRs) also produce `mentions` and `relation_mentions`
directly, at confidence 1.0 (architecture §6.3) — FIR narratives are M3a's job,
so a FIR here only gets its `source_records` row.

Towers are reference data, not source records (no `source_record_id`/
`record_type`/`legal_basis`), and are not loaded here.
"""

from __future__ import annotations

import json
from pathlib import Path

from psycopg.types.json import Jsonb

from cid.core.config import REPO_ROOT, get_settings
from cid.core.db_pg import get_connection
from cid.core.hashing import hmac_id, record_hash
from cid.pipeline.normalize.addresses import address_key
from cid.pipeline.normalize.dates import to_utc
from cid.pipeline.normalize.names import normalize_name
from cid.pipeline.normalize.offences import normalize_offence
from cid.pipeline.normalize.phones import normalize_msisdn

WORLD_DIR = REPO_ROOT / "data" / "world"

# The world generator emits naive local wall-clock timestamps for this fictional
# district; there is only one timezone in play (architecture §6.2, normalize/dates.py).
SOURCE_TZ = "Asia/Kolkata"

# architecture §6.2: telecom and financial sources are highly sensitive.
AUTH_TIER = {
    "fir": "sensitive",
    "company": "sensitive",
    "vehicle": "sensitive",
    "cdr": "highly_sensitive",
    "phone_reg": "highly_sensitive",
    "txn": "highly_sensitive",
    "kyc": "highly_sensitive",
}

# (record_type, filename) in load order — kyc/phone_reg first so their
# id -> raw-value maps are ready before cdr/txn need them.
SOURCES: list[tuple[str, str]] = [
    ("kyc", "accounts.jsonl"),
    ("phone_reg", "phone_regs.jsonl"),
    ("company", "companies.jsonl"),
    ("vehicle", "vehicles.jsonl"),
    ("fir", "firs.jsonl"),
    ("cdr", "cdr.jsonl"),
    ("txn", "txns.jsonl"),
]

_DEVANAGARI = range(0x0900, 0x0980)
_BENGALI = range(0x0980, 0x0A00)
_TAMIL = range(0x0B80, 0x0C00)


def _detect_script(text: str) -> str:
    """Script of a name surface, by Unicode block of its first non-Latin char.

    Structured records don't carry a `script` tag for every name field (only
    `companies.jsonl`'s `directors` list does); this is a light heuristic
    good enough to fill `mentions.script`, not a general script classifier.
    """
    for ch in text:
        cp = ord(ch)
        if cp in _DEVANAGARI:
            return "Deva"
        if cp in _BENGALI:
            return "Beng"
        if cp in _TAMIL:
            return "Taml"
    return "Latn"


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _load_phone_msisdn_map() -> dict[str, str]:
    return {r["phone_id"]: r["msisdn"] for r in _iter_jsonl(WORLD_DIR / "phone_regs.jsonl")}


def _load_account_no_map() -> dict[str, str]:
    return {r["account_id"]: r["account_no"] for r in _iter_jsonl(WORLD_DIR / "accounts.jsonl")}


def _mention_id(source_record_id: str, suffix: str) -> str:
    return f"MEN_{source_record_id}_{suffix}"


def _relation_id(source_record_id: str, suffix: str) -> str:
    return f"REL_{source_record_id}_{suffix}"


def _reject(cur, rec: dict, record_type: str, reason: str) -> None:
    cur.execute(
        """
        INSERT INTO ingest_rejects (source_record_id, record_type, reason)
        VALUES (%s, %s, %s)
        ON CONFLICT (source_record_id) DO NOTHING
        """,
        (rec["source_record_id"], record_type, reason),
    )


def _insert_source_record(cur, rec: dict, record_type: str, text: str | None, normalized: dict) -> None:
    """Upsert on `source_record_id`; `ingested_at` is left alone on conflict —
    it is when C.I.D. first learned the record (master §12.6), which a re-run
    must not change. `record_hash` is over `rec` only, so it is identical
    across re-runs regardless of when `ingested_at` says we loaded it.
    """
    cur.execute(
        """
        INSERT INTO source_records
            (source_record_id, source_system, record_type, legal_basis, auth_tier, raw, text, record_hash, normalized)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_record_id) DO UPDATE SET
            source_system = EXCLUDED.source_system,
            record_type   = EXCLUDED.record_type,
            legal_basis   = EXCLUDED.legal_basis,
            auth_tier     = EXCLUDED.auth_tier,
            raw           = EXCLUDED.raw,
            text          = EXCLUDED.text,
            record_hash   = EXCLUDED.record_hash,
            normalized    = EXCLUDED.normalized
        """,
        (
            rec["source_record_id"],
            rec["source_system"],
            record_type,
            rec["legal_basis"],
            AUTH_TIER[record_type],
            Jsonb(rec),
            text,
            record_hash(rec),
            Jsonb(normalized),
        ),
    )


def _insert_mention(cur, mention_id: str, source_record_id: str, entity_type: str, surface: str, script: str | None) -> None:
    cur.execute(
        """
        INSERT INTO mentions
            (mention_id, source_record_id, entity_type, surface, script, start, "end", extraction_confidence, resolved_entity_id)
        VALUES (%s, %s, %s, %s, %s, NULL, NULL, 1.0, NULL)
        ON CONFLICT (mention_id) DO NOTHING
        """,
        (mention_id, source_record_id, entity_type, surface, script),
    )


def _insert_relation(cur, relation_id: str, source_record_id: str, head_mention_id: str, tail_mention_id: str, rel_type: str) -> None:
    cur.execute(
        """
        INSERT INTO relation_mentions
            (id, source_record_id, head_mention_id, tail_mention_id, rel_type, start, "end", extraction_confidence)
        VALUES (%s, %s, %s, %s, %s, NULL, NULL, 1.0)
        ON CONFLICT (id) DO NOTHING
        """,
        (relation_id, source_record_id, head_mention_id, tail_mention_id, rel_type),
    )


def _ts_normalized(ts: str) -> dict:
    return {"utc": to_utc(ts, SOURCE_TZ).isoformat(), "source_tz": SOURCE_TZ}


def _ingest_fir(cur, rec: dict) -> None:
    normalized = {"offence": normalize_offence(rec["offence_code_system"], rec["offence_section"])}
    _insert_source_record(cur, rec, "fir", rec["text"], normalized)
    # No mentions/relations here — the rule-based extractor (M3a) reads
    # `source_records.text` and writes them from the narrative itself.


def _ingest_kyc(cur, rec: dict, hmac_key: str) -> None:
    account_hash = hmac_id(rec["account_no"], hmac_key)
    normalized = {
        "account_hash": account_hash,
        "holder_name_normalized": normalize_name(rec["holder_name"]),
    }
    _insert_source_record(cur, rec, "kyc", None, normalized)

    rid = rec["source_record_id"]
    account_mention = _mention_id(rid, "account")
    holder_mention = _mention_id(rid, "holder")
    _insert_mention(cur, account_mention, rid, "Account", account_hash, None)
    _insert_mention(cur, holder_mention, rid, "Person", rec["holder_name"], _detect_script(rec["holder_name"]))
    _insert_relation(cur, _relation_id(rid, "owns"), rid, holder_mention, account_mention, "OWNS")


def _ingest_phone_reg(cur, rec: dict, hmac_key: str) -> None:
    msisdn = normalize_msisdn(rec["msisdn"])
    msisdn_hash = hmac_id(msisdn, hmac_key)
    normalized = {
        "msisdn_hash": msisdn_hash,
        "subscriber_name_normalized": normalize_name(rec["subscriber_name"]),
    }
    _insert_source_record(cur, rec, "phone_reg", None, normalized)

    rid = rec["source_record_id"]
    phone_mention = _mention_id(rid, "phone")
    subscriber_mention = _mention_id(rid, "subscriber")
    _insert_mention(cur, phone_mention, rid, "Phone", msisdn_hash, None)
    _insert_mention(
        cur, subscriber_mention, rid, "Person", rec["subscriber_name"], _detect_script(rec["subscriber_name"])
    )
    _insert_relation(cur, _relation_id(rid, "registered_to"), rid, phone_mention, subscriber_mention, "REGISTERED_TO")


def _ingest_company(cur, rec: dict) -> None:
    normalized = {"address_key": address_key(rec["address_key"])}
    _insert_source_record(cur, rec, "company", None, normalized)

    rid = rec["source_record_id"]
    org_mention = _mention_id(rid, "org")
    _insert_mention(cur, org_mention, rid, "Organization", rec["name"], _detect_script(rec["name"]))
    for i, director in enumerate(rec["directors"]):
        director_mention = _mention_id(rid, f"director_{i}")
        _insert_mention(cur, director_mention, rid, "Person", director["surface"], director["script"])
        _insert_relation(cur, _relation_id(rid, f"director_{i}"), rid, director_mention, org_mention, "DIRECTOR_OF")


def _ingest_vehicle(cur, rec: dict) -> None:
    _insert_source_record(cur, rec, "vehicle", None, {})
    rid = rec["source_record_id"]
    _insert_mention(cur, _mention_id(rid, "vehicle"), rid, "Vehicle", rec["registration"], None)
    # No owner mention: the record states `owner_person_id`, an internal id,
    # never an owner name — there is no stated surface to build a
    # REGISTERED_TO relation from (unlike phone_reg/company, which do state one).


def _ingest_cdr(cur, rec: dict, hmac_key: str, phone_msisdn: dict[str, str]) -> None:
    calling_hash = hmac_id(normalize_msisdn(phone_msisdn[rec["calling_phone_id"]]), hmac_key)
    called_hash = hmac_id(normalize_msisdn(phone_msisdn[rec["called_phone_id"]]), hmac_key)
    normalized = {
        "ts": _ts_normalized(rec["ts"]),
        "calling_msisdn_hash": calling_hash,
        "called_msisdn_hash": called_hash,
    }
    _insert_source_record(cur, rec, "cdr", None, normalized)

    rid = rec["source_record_id"]
    calling_mention = _mention_id(rid, "calling")
    called_mention = _mention_id(rid, "called")
    _insert_mention(cur, calling_mention, rid, "Phone", calling_hash, None)
    _insert_mention(cur, called_mention, rid, "Phone", called_hash, None)
    _insert_relation(cur, _relation_id(rid, "called"), rid, calling_mention, called_mention, "CALLED")


def _ingest_txn(cur, rec: dict, hmac_key: str, account_no: dict[str, str]) -> None:
    from_hash = hmac_id(account_no[rec["from_account_id"]], hmac_key)
    to_hash = hmac_id(account_no[rec["to_account_id"]], hmac_key)
    normalized = {
        "ts": _ts_normalized(rec["ts"]),
        "from_account_hash": from_hash,
        "to_account_hash": to_hash,
    }
    _insert_source_record(cur, rec, "txn", None, normalized)

    rid = rec["source_record_id"]
    from_mention = _mention_id(rid, "from")
    to_mention = _mention_id(rid, "to")
    _insert_mention(cur, from_mention, rid, "Account", from_hash, None)
    _insert_mention(cur, to_mention, rid, "Account", to_hash, None)
    _insert_relation(
        cur, _relation_id(rid, "transferred_funds_to"), rid, from_mention, to_mention, "TRANSFERRED_FUNDS_TO"
    )


def load() -> dict[str, int]:
    """Ingest every `data/world/*.jsonl` source. Returns counts per `record_type`,
    plus `"rejected"` for the total across all types. Safe to call twice."""
    settings = get_settings()
    phone_msisdn = _load_phone_msisdn_map()
    account_no = _load_account_no_map()

    counts: dict[str, int] = {record_type: 0 for record_type, _ in SOURCES}
    rejected = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for record_type, filename in SOURCES:
                for rec in _iter_jsonl(WORLD_DIR / filename):
                    if not rec.get("legal_basis"):
                        _reject(cur, rec, record_type, "missing_legal_basis")
                        rejected += 1
                        continue

                    if record_type == "fir":
                        _ingest_fir(cur, rec)
                    elif record_type == "kyc":
                        _ingest_kyc(cur, rec, settings.hmac_key)
                    elif record_type == "phone_reg":
                        _ingest_phone_reg(cur, rec, settings.hmac_key)
                    elif record_type == "company":
                        _ingest_company(cur, rec)
                    elif record_type == "vehicle":
                        _ingest_vehicle(cur, rec)
                    elif record_type == "cdr":
                        _ingest_cdr(cur, rec, settings.hmac_key, phone_msisdn)
                    elif record_type == "txn":
                        _ingest_txn(cur, rec, settings.hmac_key, account_no)

                    counts[record_type] += 1
        conn.commit()

    counts["rejected"] = rejected
    return counts


def main() -> None:
    counts = load()
    print("Ingest summary:")
    for record_type, n in counts.items():
        print(f"  {record_type}: {n}")


if __name__ == "__main__":
    main()
