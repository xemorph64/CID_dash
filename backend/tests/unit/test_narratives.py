import os
import random
import subprocess
import sys

import pytest

from cid.pipeline.generate.narratives import (
    FAMILY_SECTIONS,
    FAMILY_SPLIT,
    HELDOUT_FAMILIES,
    TRAIN_FAMILIES,
    render_fir,
)

ALL_FAMILIES = tuple(FAMILY_SPLIT)

BASE_SLOTS = {
    "accused_1": "Ravi Kumar",
    "accused_2": "Amit",
    "victim_1": "Sita Devi",
    "witness_1": "Mohan",
    "location_1": "MG Road",
    "date_1": "12-Jan-2024",
    "vehicle_1": "MH12AB1234",
    "phone_1": "9876543210",
    "account_1": "1234",
    "org_1": "ABC Traders",
    "amount_1": "6,00,000",
    "alias_1": "Guddu",
}

# Same surface string used for two different slots — the case a str.find()
# implementation would get wrong for at least one of the two spans.
REPEATED_NAME_SLOTS = dict(BASE_SLOTS, accused_2="Ravi Kumar")


def test_offset_integrity_exhaustive():
    for family in ALL_FAMILIES:
        for language in ("en", "hi_rom"):
            for seed in range(200):
                n = render_fir(family, BASE_SLOTS, random.Random(seed), language=language)
                assert n.spans, (family, language, seed)
                for s in n.spans:
                    assert n.text[s.start : s.end] == s.surface, (family, language, seed, s)


def test_offset_integrity_with_repeated_surface():
    n = render_fir("fraud", REPEATED_NAME_SLOTS, random.Random(3), language="en")
    accused_1 = next(s for s in n.spans if s.slot == "accused_1")
    accused_2 = next(s for s in n.spans if s.slot == "accused_2")
    assert accused_1.surface == accused_2.surface == "Ravi Kumar"
    assert (accused_1.start, accused_1.end) != (accused_2.start, accused_2.end)
    assert n.text[accused_1.start : accused_1.end] == "Ravi Kumar"
    assert n.text[accused_2.start : accused_2.end] == "Ravi Kumar"


def test_both_offence_systems_appear():
    systems = {
        render_fir("complaint", BASE_SLOTS, random.Random(seed)).offence_code_system
        for seed in range(50)
    }
    assert systems == {"IPC", "BNS"}


def test_both_languages_appear():
    languages = {render_fir("complaint", BASE_SLOTS, random.Random(seed)).language for seed in range(50)}
    assert languages == {"en", "hi_rom"}


def test_train_heldout_split_disjoint_and_stable():
    assert set(TRAIN_FAMILIES) & set(HELDOUT_FAMILIES) == set()
    assert TRAIN_FAMILIES
    assert HELDOUT_FAMILIES
    assert TRAIN_FAMILIES == tuple(sorted(f for f, s in FAMILY_SPLIT.items() if s == "train"))
    assert HELDOUT_FAMILIES == tuple(sorted(f for f, s in FAMILY_SPLIT.items() if s == "heldout"))


def test_sections_stay_within_each_familys_pool():
    for family in ALL_FAMILIES:
        pool = set(FAMILY_SECTIONS[family]["IPC"]) | set(FAMILY_SECTIONS[family]["BNS"])
        for seed in range(100):
            n = render_fir(family, BASE_SLOTS, random.Random(seed))
            assert n.offence_section in FAMILY_SECTIONS[family][n.offence_code_system]
            assert n.offence_section in pool


def test_amount_renders_with_exactly_one_currency_prefix():
    for family in ("fraud", "cheating", "extortion"):
        for seed in range(30):
            for language in ("en", "hi_rom"):
                n = render_fir(family, BASE_SLOTS, random.Random(seed), language=language)
                assert n.text.count(BASE_SLOTS["amount_1"]) == 1
                # exactly one currency marker directly preceding the bare amount
                prefixed = n.text.count(f"Rs {BASE_SLOTS['amount_1']}") + n.text.count(
                    f"₹{BASE_SLOTS['amount_1']}"
                )
                assert prefixed == 1
                assert f"Rs Rs {BASE_SLOTS['amount_1']}" not in n.text
                assert f"₹Rs {BASE_SLOTS['amount_1']}" not in n.text


_HI_ROM_MARKERS = ("ke", "ne", "bheje", "gaye", "paise", "kiya", "hui")


def test_no_hi_rom_markers_leak_into_english():
    for family in ALL_FAMILIES:
        for seed in range(60):
            n = render_fir(family, BASE_SLOTS, random.Random(seed), language="en")
            words = {w.strip(".,;:!?").lower() for w in n.text.split()}
            leaked = words & set(_HI_ROM_MARKERS)
            assert not leaked, (family, seed, n.text)


def test_through_account_emits_mentioned_with_not_owns():
    for seed in range(20):
        n = render_fir("fraud", BASE_SLOTS, random.Random(seed))
        account_rels = [r for r in n.relations if r.tail_slot == "account_1"]
        assert account_rels == [
            r for r in account_rels if r.rel_type == "MENTIONED_WITH"
        ]
        assert not any(r.rel_type == "OWNS" and r.tail_slot == "account_1" for r in n.relations)
        assert any(
            r.head_slot == "accused_2" and r.tail_slot == "account_1" and r.rel_type == "MENTIONED_WITH"
            for r in n.relations
        )


def test_determinism_same_seed_same_output():
    n1 = render_fir("complaint", BASE_SLOTS, random.Random(7))
    n2 = render_fir("complaint", BASE_SLOTS, random.Random(7))
    assert n1 == n2


def test_determinism_across_pythonhashseed():
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    script = (
        f"import random, sys; sys.path.insert(0, {backend_dir!r}); "
        "from cid.pipeline.generate.narratives import render_fir; "
        f"n = render_fir('fraud', {BASE_SLOTS!r}, random.Random(7)); "
        "print(n.text)"
    )

    def run(hashseed: str) -> str:
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True
        )
        return result.stdout

    assert run("0") == run("1")


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_unknown_slot_family_smoke(family):
    n = render_fir(family, BASE_SLOTS, random.Random(0))
    assert n.family == family
    assert n.split == FAMILY_SPLIT[family]
