"""Phone number normalisation (architecture §6.2).

`normalize_msisdn` only extracts a canonical E.164-with-`+` form; it does
not hash. The caller HMACs the result with `core.hashing.hmac_id` to get
`msisdn_hash` — never store or compare the raw digits past this point.
"""

from __future__ import annotations

import re

# Indian mobile numbers: 10 digits, first digit 6-9 (TRAI numbering plan).
_MOBILE_RE = re.compile(r"^[6-9]\d{9}$")


def normalize_msisdn(raw: str) -> str | None:
    """Return `+91XXXXXXXXXX`, or None if `raw` isn't a plausible Indian mobile.

    Accepts `+91 98200 11234`, `09820011234`, `9820011234`, and variants
    with spaces, hyphens or brackets. Returns None rather than guessing on
    anything else — a wrong normalisation here silently merges two
    different people at M4.
    """
    if not raw:
        return None
    digits = re.sub(r"[^\d+]", "", raw)

    if digits.startswith("+91"):
        digits = digits[3:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    elif digits.startswith("+"):
        # some other country code, or malformed — not ours to guess at.
        return None

    if not _MOBILE_RE.match(digits):
        return None
    return "+91" + digits
