"""Offence code normalisation (architecture §6.2).

The IPC↔BNS table below is a **synthetic subset** covering only the
sections the world generator emits — it is not a legal reference. The real
mapping source is master Q-DAT-05, still open; do not treat this table as
authoritative.

The point of `ontology_id` is that an offence charged under the old code
(IPC) and the new one (BNS) are the same offence and must compare equal,
regardless of which code system a given FIR happens to use.
"""

from __future__ import annotations

# ontology_id -> {code_system: section}. Equivalent IPC/BNS sections share
# one row, so both directions of the lookup below stay in sync by
# construction.
_EQUIVALENCES: dict[str, dict[str, tuple[str, ...]]] = {
    "cheating": {"IPC": ("420",), "BNS": ("318",)},
    "criminal_breach_of_trust": {"IPC": ("406",), "BNS": ("316",)},
    "theft": {"IPC": ("379",), "BNS": ("303",)},
    "dishonestly_receiving_stolen_property": {"IPC": ("411",), "BNS": ("317",)},
    "extortion": {"IPC": ("384",), "BNS": ("308",)},
    # One offence can span several sections: IPC 503 *defines* criminal
    # intimidation and 506 *punishes* it, and BNS 351 carries both (351(1)
    # defines, 351(2) punishes). They are the same offence, so they share an
    # ontology_id. (IPC 507 — intimidation by anonymous communication — is a
    # genuinely distinct offence, and is simply not in this synthetic subset.)
    "criminal_intimidation": {"IPC": ("503", "506"), "BNS": ("351", "351(2)")},
    "common_intention": {"IPC": ("34",), "BNS": ("3",)},
}

_LOOKUP: dict[tuple[str, str], str] = {
    (system, section): ontology_id
    for ontology_id, by_system in _EQUIVALENCES.items()
    for system, sections in by_system.items()
    for section in sections
}


def normalize_offence(code_system: str, section: str) -> dict:
    """Return `{code_system, section, ontology_id}` for a charged section.

    Raises KeyError for a (code_system, section) pair not in the synthetic
    table — silently inventing an ontology_id would defeat the point of
    having one.
    """
    code_system = code_system.upper()
    ontology_id = _LOOKUP[(code_system, section)]
    return {"code_system": code_system, "section": section, "ontology_id": ontology_id}
