"""Identifier hashing (architecture §5.3).

Two distinct hashes with two distinct purposes — never interchange them:

- `record_hash`: unkeyed SHA-256 of a record's canonical JSON, for evidence
  integrity at ingest (P-17). Anyone can recompute it to check a record
  hasn't changed; it does not need to hide anything.
- `hmac_id`: keyed HMAC-SHA256, for values drawn from a small, guessable
  space (10-digit phone numbers, account numbers). An unkeyed hash over
  that space is brute-forceable in seconds, which is the whole reason
  P-08 requires a key.
"""

from __future__ import annotations

import hashlib
import hmac
import json


def record_hash(record: dict) -> str:
    """SHA-256 hex of the record's canonical JSON.

    Canonical = sorted keys, compact separators, UTF-8 (`ensure_ascii=False`
    so the digest doesn't depend on how a source's original script is
    escaped). Deterministic regardless of dict insertion order or
    PYTHONHASHSEED — `json.dumps(sort_keys=True)` never consults `hash()`.
    """
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hmac_id(value: str, key: str) -> str:
    """HMAC-SHA256(key, value) hex, per P-08.

    `value` should already be normalised by the caller (e.g. E.164 digits
    for a phone number) so the same real-world identifier always hashes
    the same way. The key is an explicit argument, not read from settings,
    so this stays a pure function.
    """
    return hmac.new(key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()
