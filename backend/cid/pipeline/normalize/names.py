"""Name surface normalisation (architecture §6.2).

Light-touch only: whitespace, honorifics, stray punctuation. No phonetic
folding or transliteration — that belongs to `resolve/indic_key.py` (M4).
Duplicating that logic here is how the two would silently diverge, so this
module stops well short of it and preserves the original script.
"""

from __future__ import annotations

import re

# Honorifics to strip, Latin and Devanagari forms (architecture §6.4 lists
# the same set for indic_key; kept in sync by naming, not by import, since
# this module must not depend on resolve/*).
_HONORIFICS = {
    "shri",
    "smt",
    "sh",
    "mr",
    "mrs",
    "dr",
    "kumari",
    "late",
    "श्री",
    "श्रीमती",
}

_TOKEN_PUNCT_RE = re.compile(r"^[.,;:]+|[.,;:]+$")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_name(raw: str) -> str:
    """Collapse whitespace and strip honorifics/stray punctuation, preserving script."""
    tokens = raw.split()
    kept = []
    for token in tokens:
        stripped = _TOKEN_PUNCT_RE.sub("", token)
        if stripped.lower() in _HONORIFICS:
            continue
        kept.append(stripped)
    return _WHITESPACE_RE.sub(" ", " ".join(kept)).strip()
