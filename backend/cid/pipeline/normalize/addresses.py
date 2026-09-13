"""Address normalisation (architecture §6.2): a stable comparison key for M4's entity resolution.

`address_key` is deliberately crude — lowercase, de-punctuate, expand common
abbreviations — it only needs to make near-duplicate spellings of the same
address collapse for blocking/comparison, not to geocode anything.
"""

from __future__ import annotations

import re

# Longer keys first within a group so e.g. "extn" doesn't get half-matched
# by a shorter alternative before the fuller one is tried.
_ABBREVIATIONS: dict[str, str] = {
    r"\brd\b": "road",
    r"\bst\b": "street",
    r"\bnagar\b": "nagar",
    r"\bcolony\b": "colony",
    r"\bextn\b": "extension",
    r"\bext\b": "extension",
    r"\bapt\b": "apartment",
    r"\bbldg\b": "building",
    r"\bnr\b": "near",
}

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")


def address_key(raw: str) -> str:
    """Lowercase, de-punctuate, collapse whitespace, expand common abbreviations."""
    key = raw.lower()
    key = _PUNCT_RE.sub(" ", key)
    key = _WHITESPACE_RE.sub(" ", key).strip()

    for pattern, expansion in _ABBREVIATIONS.items():
        key = re.sub(pattern, expansion, key)

    key = _WHITESPACE_RE.sub(" ", key).strip()
    return key
