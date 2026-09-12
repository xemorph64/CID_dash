import hashlib
import os
import random
import subprocess
import sys

from cid.pipeline.generate.names import (
    IDENTITY_TRAPS,
    _curated_script_form,
    make_people,
    transliterate_name,
    variants_for,
)

# Devanagari virama, Tamil pulli, Bengali virama — a word ending in one of
# these is the naive-transliteration artifact this module must not emit.
_TRAILING_VIRAMAS = "्்্"


def test_mohammad_ali_trap_merges_across_four_sources():
    trap = IDENTITY_TRAPS["mohammad_ali"]
    surfaces = trap["surfaces"]
    assert len(surfaces) == 4
    assert {s.source_type for s in surfaces} == {
        "fir",
        "bank_kyc",
        "phone_registration",
        "company_register",
    }
    forms = {s.variant.surface for s in surfaces}
    assert forms == {"Mohammad Ali", "Mohd Ali", "Md. Ali", "मोहम्मद अली"}


def test_raj_kumar_trap_must_not_merge():
    trap = IDENTITY_TRAPS["raj_kumar"]
    persons = trap["persons"]
    assert len(persons) == 2
    assert persons[0].person_id != persons[1].person_id
    assert persons[0].dob != persons[1].dob

    forms = {v.surface for v in trap["surfaces"]}
    assert forms == {"Raj Kumar", "Rajkumar", "Raj Kumaar", "राज कुमार"}


def test_chatterjee_trap_formal_surname_equivalence():
    forms = {v.surface for v in IDENTITY_TRAPS["chatterjee"]["surfaces"]}
    assert forms == {
        "Debashish Chatterjee",
        "Debashish Chaterjee",
        "Debashish Chattopadhyay",
    }


def test_azhagiri_trap_zh_to_l_fold():
    forms = {v.surface for v in IDENTITY_TRAPS["azhagiri"]["surfaces"]}
    assert forms == {"Karthik Azhagiri", "Karthik Alagiri"}


def test_make_people_is_deterministic():
    a = make_people(50, random.Random(7))
    b = make_people(50, random.Random(7))
    assert a == b


def test_variants_for_is_deterministic():
    person = make_people(1, random.Random(7))[0]
    a = variants_for(person, random.Random(7), 4)
    b = variants_for(person, random.Random(7), 4)
    assert a == b


def _digest_of_generation(seed: int) -> str:
    people = make_people(20, random.Random(seed))
    variants = variants_for(people[0], random.Random(seed), 4)
    payload = repr(people) + repr(variants)
    return hashlib.sha256(payload.encode()).hexdigest()


def test_determinism_survives_pythonhashseed_salting():
    script = (
        "from tests.unit.test_names import _digest_of_generation; "
        "print(_digest_of_generation(42))"
    )
    digests = []
    for hashseed in ("0", "1"):
        env = dict(os.environ, PYTHONHASHSEED=hashseed, PYTHONPATH="tests/..")
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=f"{os.path.dirname(__file__)}/../..",
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        digests.append(result.stdout.strip())
    assert digests[0] == digests[1]
    assert digests[0]


def test_variants_for_produces_the_needed_script_mix():
    people = make_people(300, random.Random(11))
    rng = random.Random(11)
    scripts = [
        v.script
        for p in people
        for v in variants_for(p, rng, 5)
        if v.kind == "transliteration"
    ]
    assert scripts.count("Deva") > 0
    assert scripts.count("Taml") >= 1
    assert scripts.count("Beng") >= 1


def test_transliterate_name_has_no_stray_word_final_virama():
    # transliterate_name() no longer feeds variants_for() (every non-Latin
    # world surface must be curated) but stays as a utility for M4's
    # indic_key.py, so its own cleanup still needs to hold on its own.
    for name in ("Arjun Mukherjee", "Pooja Sharma", "Vijayan Roy", "Priya Verma"):
        for script in ("Deva", "Taml", "Beng"):
            surface = transliterate_name(name, script)
            for word in surface.split():
                assert word[-1] not in _TRAILING_VIRAMAS, surface


def test_every_non_latin_variant_is_curated():
    # variants_for() must never emit a non-Latin surface via
    # transliterate_name() — only curated pairs. Equivalently: every
    # non-Latin surface reproduces exactly what _curated_script_form()
    # (curated data only) would compose for that name and script.
    people = make_people(300, random.Random(11))
    rng = random.Random(11)
    non_latin_seen = 0
    for p in people:
        for v in variants_for(p, rng, 5):
            if v.script == "Latn":
                continue
            non_latin_seen += 1
            assert _curated_script_form(p.canonical_name, v.script) == v.surface
    assert non_latin_seen > 0  # sanity: script variants still occur


def test_known_names_round_trip_to_curated_devanagari():
    assert _curated_script_form("Pooja Sharma", "Deva") == "पूजा शर्मा"
    assert _curated_script_form("Vijayan Roy", "Deva") == "विजयन रॉय"
    assert _curated_script_form("Arjun Mukherjee", "Taml") is None  # no Tamil pair for Mukherjee
