"""Synthetic FIR narrative generator with ground-truth spans and relations.

Templates place caller-supplied surface strings (names, phones, accounts, ...)
into short FIR-style narratives and record the exact offset each one lands at
as it is written — never by searching the finished text (see module tests).

Slot contract for `amount_1`: pass the **bare** number, e.g. "6,00,000" —
never a value that already carries a currency symbol/word ("Rs 6,00,000" or
"₹6,00,000"). Templates supply the currency prefix themselves; a slot value
that also carries one would double it.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class GoldSpan:
    slot: str
    start: int
    end: int
    surface: str
    entity_type: str


@dataclass(frozen=True)
class GoldRelation:
    head_slot: str
    tail_slot: str
    rel_type: str


@dataclass(frozen=True)
class Narrative:
    text: str
    family: str
    split: str
    language: str
    offence_code_system: str
    offence_section: str
    spans: list[GoldSpan]
    relations: list[GoldRelation]


# Family -> split. Fixed and disjoint; M3a scores on the heldout families only.
FAMILY_SPLIT: dict[str, str] = {
    "complaint": "train",
    "seizure": "train",
    "recovery": "train",
    "fraud": "train",
    "cheating": "heldout",
    "extortion": "heldout",
}

TRAIN_FAMILIES = tuple(sorted(f for f, s in FAMILY_SPLIT.items() if s == "train"))
HELDOUT_FAMILIES = tuple(sorted(f for f, s in FAMILY_SPLIT.items() if s == "heldout"))

# Section pool per family so a record's charge matches its scenario (a vehicle
# seizure is never filed under the cheating section, etc). Kept small and
# plausible, not exhaustive.
FAMILY_SECTIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "complaint": {"IPC": ("503", "506"), "BNS": ("351", "351(2)")},
    "seizure": {"IPC": ("379", "411"), "BNS": ("303", "317")},
    "recovery": {"IPC": ("379",), "BNS": ("303",)},
    "fraud": {"IPC": ("420", "406"), "BNS": ("318", "316")},
    "cheating": {"IPC": ("420", "406"), "BNS": ("318", "316")},
    "extortion": {"IPC": ("384", "506"), "BNS": ("308", "351")},
}


class _Builder:
    """Accumulates narrative text and records each placed slot's true offset."""

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._length = 0
        self.spans: list[GoldSpan] = []

    def text(self, literal: str) -> _Builder:
        self._parts.append(literal)
        self._length += len(literal)
        return self

    def slot(self, slot: str, surface: str, entity_type: str) -> _Builder:
        start = self._length
        self._parts.append(surface)
        self._length += len(surface)
        self.spans.append(
            GoldSpan(slot=slot, start=start, end=self._length, surface=surface, entity_type=entity_type)
        )
        return self

    def build(self) -> str:
        return "".join(self._parts)


def _offence(rng: random.Random, family: str) -> tuple[str, str]:
    system = "BNS" if rng.random() < 0.6 else "IPC"
    return system, rng.choice(FAMILY_SECTIONS[family][system])


_COMPLAINT_OPENERS = {
    "en": ("Complainant states that the accused ", "As per the complaint, accused "),
    "hi_rom": ("Shikayatkarta ne bataya ki accused ", "Complaint ke anusar accused "),
}
_COMPLAINT_CLOSERS = {
    "en": (" saw the incident. Case registered under section {s}.", " witnessed the whole event. FIR filed under section {s}."),
    "hi_rom": (" ne yeh dekha. Section {s} ke tehat case darj hua.", " ne poori ghatna dekhi. FIR section {s} mein darj hui."),
}


def _template_complaint(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    closer = rng.choice(_COMPLAINT_CLOSERS[language]).format(s=section)
    if language == "en":
        b.text(rng.choice(_COMPLAINT_OPENERS["en"]))
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" came to the ")
        b.slot("location_1", slots["location_1"], "Location")
        b.text(" residence on ")
        b.slot("date_1", slots["date_1"], "DateTime")
        b.text(" and threatened the victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(". Witness ")
        b.slot("witness_1", slots["witness_1"], "Witness")
        b.text(closer)
    else:
        b.text(rng.choice(_COMPLAINT_OPENERS["hi_rom"]))
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" ne ")
        b.slot("location_1", slots["location_1"], "Location")
        b.text(" mein ")
        b.slot("date_1", slots["date_1"], "DateTime")
        b.text(" ko victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" ko dhamki di. Gawah ")
        b.slot("witness_1", slots["witness_1"], "Witness")
        b.text(closer)
    return [
        GoldRelation("accused_1", "complaint", "ACCUSED_IN"),
        GoldRelation("victim_1", "complaint", "VICTIM_IN"),
        GoldRelation("witness_1", "complaint", "WITNESS_IN"),
    ]


_SEIZURE_CLOSERS = {
    "en": (". Offence under section {s} is made out.", ". Vehicle seizure recorded under section {s}."),
    "hi_rom": (" ke naam registered hai. Section {s} lagaya gaya.", " ke naam par hai. Section {s} ke tehat karyawahi hui."),
}


def _template_seizure(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    closer = rng.choice(_SEIZURE_CLOSERS[language]).format(s=section)
    if language == "en":
        b.text("During search of the ")
        b.slot("location_1", slots["location_1"], "Location")
        b.text(" premises, police seized a vehicle bearing number ")
        b.slot("vehicle_1", slots["vehicle_1"], "Vehicle")
        b.text(" registered to accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(closer)
    else:
        b.text("Talashi ke dauran ")
        b.slot("location_1", slots["location_1"], "Location")
        b.text(" se ek vehicle number ")
        b.slot("vehicle_1", slots["vehicle_1"], "Vehicle")
        b.text(" jabt kiya gaya jo accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(closer)
    return [
        GoldRelation("accused_1", "seizure", "ACCUSED_IN"),
        GoldRelation("accused_1", "vehicle_1", "OWNS"),
    ]


_RECOVERY_CONNECTORS = {
    "en": ((" at ", " under section {s}."), (" on ", ", offence registered under section {s}.")),
    "hi_rom": ((" se ", " ko baramad hua. Section {s} ke tehat."), (" se ", " ko milla. Section {s} lagaya gaya.")),
}


def _template_recovery(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    lead_in, tail = rng.choice(_RECOVERY_CONNECTORS[language])
    tail = tail.format(s=section)
    if language == "en":
        b.text("Stolen phone with number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(" belonging to victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" was recovered from accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(lead_in)
        b.slot("date_1", slots["date_1"], "DateTime")
        b.text(tail)
    else:
        b.text("Victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" ka chori hua phone number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(" accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(lead_in)
        b.slot("date_1", slots["date_1"], "DateTime")
        b.text(tail)
    return [
        GoldRelation("accused_1", "recovery", "ACCUSED_IN"),
        GoldRelation("victim_1", "recovery", "VICTIM_IN"),
        GoldRelation("victim_1", "phone_1", "OWNS"),
    ]


_FRAUD_CLOSERS = {
    "en": (" Section {s} applied.", " Case registered under section {s}."),
    "hi_rom": (" bheje gaye. Section {s} lagaya gaya.", " bheje gaye. Section {s} ke tehat FIR darj hui."),
}


def _template_fraud(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    # The "through account" construction (master §10.4 / architecture §6.3):
    # the text only says money moved via the person's account, never that the
    # person owns it — so the gold relation is MENTIONED_WITH, never OWNS.
    closer = rng.choice(_FRAUD_CLOSERS[language]).format(s=section)
    if language == "en":
        b.text("Victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" reported that accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" of ")
        b.slot("org_1", slots["org_1"], "Organization")
        b.text(" cheated the complainant of Rs ")
        b.text(slots["amount_1"])
        b.text("; the money was routed through account ")
        b.slot("account_1", slots["account_1"], "Account")
        b.text(" linked to ")
        b.slot("accused_2", slots["accused_2"], "Person")
        b.text(".")
        b.text(closer)
    else:
        b.text("Shikayatkarta ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" ne bataya ki accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" ne, jo ")
        b.slot("org_1", slots["org_1"], "Organization")
        b.text(" se hai, unse ₹")
        b.text(slots["amount_1"])
        b.text(" le liye, paise ")
        b.slot("accused_2", slots["accused_2"], "Person")
        b.text(" ke through account ")
        b.slot("account_1", slots["account_1"], "Account")
        b.text(closer)
    return [
        GoldRelation("accused_1", "fraud", "ACCUSED_IN"),
        GoldRelation("victim_1", "fraud", "VICTIM_IN"),
        GoldRelation("accused_1", "org_1", "DIRECTOR_OF"),
        GoldRelation("accused_2", "account_1", "MENTIONED_WITH"),
    ]


_CHEATING_CLOSERS = {
    "en": (" and never delivered. Section {s} is invoked.", " and absconded. Case registered under section {s}."),
    "hi_rom": (" liye aur kabhi kaam nahi diya. Section {s} lagaya gaya.", " liye aur farar ho gaya. Section {s} ke tehat FIR hui."),
}


def _template_cheating(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    closer = rng.choice(_CHEATING_CLOSERS[language]).format(s=section)
    if language == "en":
        b.text("Complainant ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" states that accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(", also known as ")
        b.slot("alias_1", slots["alias_1"], "Alias")
        b.text(", promised a job and took Rs ")
        b.text(slots["amount_1"])
        b.text(" via phone number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(closer)
    else:
        b.text("Complainant ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" ne bataya ki accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(", jise ")
        b.slot("alias_1", slots["alias_1"], "Alias")
        b.text(" ke naam se bhi jaana jaata hai, ne naukri ka vaada karke phone number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(" se Rs ")
        b.text(slots["amount_1"])
        b.text(closer)
    return [
        GoldRelation("accused_1", "cheating", "ACCUSED_IN"),
        GoldRelation("victim_1", "cheating", "VICTIM_IN"),
        GoldRelation("accused_1", "alias_1", "ASSOCIATED_WITH"),
    ]


_EXTORTION_CLOSERS = {
    "en": (" would be harmed. Section {s} applied.", " would suffer if the victim refused. Case registered under section {s}."),
    "hi_rom": (
        " ko nuksan pahunchane ki dhamki di. Section {s} lagaya gaya.",
        " ko takleef hogi agar paise nahi diye. Section {s} ke tehat FIR hui.",
    ),
}


def _template_extortion(
    b: _Builder, slots: dict[str, str], language: str, section: str, rng: random.Random
) -> list[GoldRelation]:
    closer = rng.choice(_EXTORTION_CLOSERS[language]).format(s=section)
    if language == "en":
        b.text("Victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" states that accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" called from number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(" and demanded Rs ")
        b.text(slots["amount_1"])
        b.text(", threatening associate ")
        b.slot("accused_2", slots["accused_2"], "Accused")
        b.text(closer)
    else:
        b.text("Victim ")
        b.slot("victim_1", slots["victim_1"], "Victim")
        b.text(" ne bataya ki accused ")
        b.slot("accused_1", slots["accused_1"], "Accused")
        b.text(" ne number ")
        b.slot("phone_1", slots["phone_1"], "Phone")
        b.text(" se call karke Rs ")
        b.text(slots["amount_1"])
        b.text(" maange aur associate ")
        b.slot("accused_2", slots["accused_2"], "Accused")
        b.text(closer)
    return [
        GoldRelation("accused_1", "extortion", "ACCUSED_IN"),
        GoldRelation("victim_1", "extortion", "VICTIM_IN"),
        GoldRelation("accused_2", "extortion", "ACCUSED_IN"),
        GoldRelation("accused_1", "accused_2", "ASSOCIATED_WITH"),
    ]


_TEMPLATES = {
    "complaint": _template_complaint,
    "seizure": _template_seizure,
    "recovery": _template_recovery,
    "fraud": _template_fraud,
    "cheating": _template_cheating,
    "extortion": _template_extortion,
}


def render_fir(
    family: str, slots: dict[str, str], rng: random.Random, *, language: str | None = None
) -> Narrative:
    """Render one FIR narrative for `family`, placing `slots` and recording gold spans.

    `slots["amount_1"]` (families that use it) must be a bare number, e.g.
    "6,00,000" — the template supplies the currency prefix.
    """
    if family not in _TEMPLATES:
        raise ValueError(f"unknown narrative family: {family!r}")
    lang = language if language is not None else rng.choice(("en", "hi_rom"))
    system, section = _offence(rng, family)
    b = _Builder()
    relations = _TEMPLATES[family](b, slots, lang, section, rng)
    return Narrative(
        text=b.build(),
        family=family,
        split=FAMILY_SPLIT[family],
        language=lang,
        offence_code_system=system,
        offence_section=section,
        spans=b.spans,
        relations=relations,
    )
