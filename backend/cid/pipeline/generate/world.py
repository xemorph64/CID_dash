"""Orchestrates synthetic world generation (M1). Runnable as
`python -m cid.pipeline.generate.world`.

Builds a population, injects the demo + background networks and the four
look-alikes over it (`networks.py`, `lookalikes.py`), places the four
identity traps (`names.py`), renders FIR narratives (`narratives.py`), and
writes everything under `data/world/` plus `truth.json` (`truth.py`).

Determinism (M1's hard acceptance criterion): one master `random.Random(seed)`
derives every child RNG used below, in a fixed order, via `getrandbits` — no
module-level `random.*`, no `hash()`, no wall-clock time. JSON is written
with `ensure_ascii=False, sort_keys=True, separators=(",", ":")`, UTF-8,
`\n` newlines, one object per line for the `.jsonl` files. Anything derived
from a `set` is sorted before it is written or fed to `rng.sample`, since
`set` iteration order is salted by `PYTHONHASHSEED`.
"""

from __future__ import annotations

import datetime
import json
import random
from dataclasses import dataclass
from pathlib import Path

from cid.core.config import REPO_ROOT, Settings, get_settings
from cid.pipeline.generate import truth as truth_mod
from cid.pipeline.generate.lookalikes import inject_lookalikes
from cid.pipeline.generate.names import (
    IDENTITY_TRAPS,
    TOWNS,
    NameVariant,
    TruePerson,
    make_people,
    variants_for,
)
from cid.pipeline.generate.narratives import render_fir
from cid.pipeline.generate.networks import (
    inject_background_networks,
    inject_demo_networks,
    shell_org_account,
)
from cid.pipeline.generate.specs import (
    ACCOUNT_ID,
    ORG_ID,
    PHONE_ID,
    VEHICLE_ID,
    Account,
    Company,
    GoldMention,
    Phone,
    Population,
    Tower,
    Vehicle,
    WorldOutput,
)

# --- World profile: everything the population/network builders need -------


@dataclass(frozen=True)
class WorldProfile:
    """Sizing knobs for one generation run. `from_settings` reads the real
    `config/cid.yaml` numbers (used by the CLI and `make world`); tests build
    a smaller profile directly so the golden suite stays fast, while still
    keeping every structure and trap present (implementation.md M1)."""

    seed: int
    people: int
    firs: int
    cdr_rows: int
    txns: int
    towers: int
    accounts: int
    phone_regs: int
    companies: int
    vehicles: int
    background_networks: int
    synthetic_threshold_inr: int
    start_date: datetime.date
    end_date: datetime.date
    # How far before start_date the oldest accounts/phones were opened.
    # networks.py's mule fan-out and lookalikes.py's payroll/holding-company
    # scenarios both need a body of accounts far older than the world span.
    history_days: int = 1000

    @classmethod
    def from_settings(cls, settings: Settings) -> WorldProfile:
        w = settings.world
        return cls(
            seed=settings.seed,
            people=w.people,
            firs=w.firs,
            cdr_rows=w.cdr_rows,
            txns=w.txns,
            towers=w.towers,
            accounts=w.accounts,
            phone_regs=w.phone_regs,
            companies=w.companies,
            vehicles=w.vehicles,
            background_networks=w.background_networks,
            synthetic_threshold_inr=w.synthetic_threshold_inr,
            start_date=w.start_date,
            end_date=w.end_date,
        )


# Demo users (prd §3). No password hashes — auth lands in M5.
DEMO_USERS = [
    {"user_id": "io.patil", "role": "investigating_officer", "display_name": "A. Patil"},
    {"user_id": "analyst.khan", "role": "crime_analyst", "display_name": "R. Khan"},
    {"user_id": "supervisor.desai", "role": "supervisor", "display_name": "S. Desai"},
    {"user_id": "prosecutor.rao", "role": "prosecutor", "display_name": "K. Rao"},
    {"user_id": "auditor.iyer", "role": "auditor", "display_name": "M. Iyer"},
]

DEMO_CASE_ID = "CASE_0231"
DEMO_FIR_NO = "224/2025"

# FIR narrative slot -> entity_type, exactly as narratives.py's per-family
# templates place them (architecture.md §6.3's entity type list).
REQUIRED_SLOTS: dict[str, dict[str, str]] = {
    "complaint": {
        "accused_1": "Accused",
        "date_1": "DateTime",
        "location_1": "Location",
        "victim_1": "Victim",
        "witness_1": "Witness",
    },
    "seizure": {"accused_1": "Accused", "location_1": "Location", "vehicle_1": "Vehicle"},
    "recovery": {
        "accused_1": "Accused",
        "date_1": "DateTime",
        "phone_1": "Phone",
        "victim_1": "Victim",
    },
    "fraud": {
        "account_1": "Account",
        "accused_1": "Accused",
        "accused_2": "Person",
        "amount_1": "Amount",
        "org_1": "Organization",
        "victim_1": "Victim",
    },
    "cheating": {
        "accused_1": "Accused",
        "alias_1": "Alias",
        "amount_1": "Amount",
        "phone_1": "Phone",
        "victim_1": "Victim",
    },
    "extortion": {
        "accused_1": "Accused",
        "accused_2": "Accused",
        "amount_1": "Amount",
        "phone_1": "Phone",
        "victim_1": "Victim",
    },
}
ALL_FAMILIES = tuple(sorted(REQUIRED_SLOTS))
PERSON_ENTITY_TYPES = {"Accused", "Victim", "Witness", "Alias", "Person"}

_ALIAS_WORDS = ["Bunty", "Guddu", "Pintu", "Chintu", "Bobby", "Munna", "Tinku", "Lucky"]
_BANK_NAMES = ["Demo Bank", "Sahakari Bank", "Grameen Sahyog Bank", "City Trust Bank"]
# One shared dealer-name pool for every phone (batch, long-term or trap) —
# a record's seller must never say "TrapSeller"/"LongTerm7": that announces
# the record's role in the test design rather than looking like a real shop.
_DEALER_NAMES = [
    "Sunrise Mobile Store", "Metro Telecom", "City Communications", "Star Mobile Shoppe",
    "Digital Point", "Cellular World", "New Age Mobiles", "Reliable Telecom",
    "Shree Mobile Center", "Prime Communications",
]
_ADDRESS_STREETS = ["Market Road", "Station Road", "Gandhi Marg", "Civil Lines", "Main Bazar", "Ring Road"]


# --- Small deterministic helpers --------------------------------------------


def _json_default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    raise TypeError(f"not JSON serializable: {o!r}")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=_json_default))
            f.write("\n")


def _write_json(path: Path, obj) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=_json_default))
        f.write("\n")


def _indian_grouping(n: int) -> str:
    s = str(n)
    last3, rest = s[-3:], s[:-3]
    parts: list[str] = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join([*parts, last3]) if parts else last3


def _indian_amount(rng: random.Random) -> str:
    n = rng.choice([100000, 200000, 300000, 500000, 600000, 800000, 1000000, 1500000, 2000000])
    return _indian_grouping(n)


def _random_date_str(rng: random.Random, profile: WorldProfile) -> str:
    days = max((profile.end_date - profile.start_date).days, 0)
    d = profile.start_date + datetime.timedelta(days=rng.randint(0, days))
    return d.strftime("%d %b %Y")


def _plausible_address(rng: random.Random) -> str:
    """A registered-address string that looks like a real one, not a token
    like `ADDR_NOISE_0000` — this is also what `normalize/addresses.py`'s
    `address_key()` is meant to have something real to normalise."""
    return f"{rng.randint(1, 200)}, {rng.choice(_ADDRESS_STREETS)}, {rng.choice(TOWNS)}"


def _pick_variant(person: TruePerson, rng: random.Random) -> NameVariant:
    variants = variants_for(person, rng, rng.randint(2, 5))
    return variants[rng.randrange(len(variants))]


# --- Population ---------------------------------------------------------


def _build_accounts(profile: WorldProfile, holders: list[TruePerson], rng: random.Random) -> list[Account]:
    """Networks only ever pick account-opening windows *inside* the world
    span (mule fan-outs, T-03's 72 h windows); a handful of much older
    accounts exist purely for lookalikes.py's payroll/holding-company
    scenarios, which need accounts opened >400 days before a transfer.
    Spreading every account uniformly across history+span (as a single
    cycle) starves the span, since history is ~3x longer than the span
    (implementation.md M1's density warning) — so the two pools are built
    separately: a small old pool cycling across `history_days`, and the
    rest cycling densely across the span itself, never one account per
    calendar day."""
    span_days = (profile.end_date - profile.start_date).days + 1
    n_old = min(len(holders), max(100, len(holders) // 20))
    accounts = []
    for i, holder in enumerate(holders):
        if i < n_old:
            day_offset = i % profile.history_days
            opened = profile.start_date - datetime.timedelta(days=profile.history_days) + datetime.timedelta(days=day_offset)
        else:
            day_offset = (i - n_old) % span_days
            opened = profile.start_date + datetime.timedelta(days=day_offset)
        accounts.append(
            Account(
                account_id=ACCOUNT_ID.format(i),
                account_no=str(100_000_000 + i),
                holder_person_id=holder.person_id,
                opened=opened,
                bank=rng.choice(_BANK_NAMES),
                kyc_status="verified",
            )
        )
    return accounts


def _build_phones(profile: WorldProfile, subs: list[TruePerson], rng: random.Random) -> list[Phone]:
    """Batch-activated short-lived phones (T-04's burner signal) followed by
    long-lived phones with distinct sellers for everyone else."""
    batch_size = 12
    n_batches = max(35, profile.background_networks + 5)
    span = (profile.end_date - profile.start_date).days
    usable_span = max(1, span - 60)
    spacing = max(1, usable_span // n_batches)

    phones: list[Phone] = []
    idx = 0
    for batch in range(n_batches):
        if idx + batch_size > len(subs):
            break
        batch_start = profile.start_date + datetime.timedelta(days=10 + spacing * batch)
        seller = rng.choice(_DEALER_NAMES)
        for _ in range(batch_size):
            holder = subs[idx]
            phones.append(
                Phone(
                    phone_id=PHONE_ID.format(idx),
                    msisdn=str(9_000_000_000 + idx),
                    subscriber_person_id=holder.person_id,
                    activated=batch_start,
                    deactivated=batch_start + datetime.timedelta(days=20),
                    imsi=f"IMSI{idx:09d}",
                    seller=seller,
                )
            )
            idx += 1

    for holder in subs[idx:]:
        phones.append(
            Phone(
                phone_id=PHONE_ID.format(idx),
                msisdn=str(9_000_000_000 + idx),
                subscriber_person_id=holder.person_id,
                activated=profile.start_date - datetime.timedelta(days=800),
                deactivated=None,
                imsi=f"IMSI{idx:09d}",
                seller=rng.choice(_DEALER_NAMES),
            )
        )
        idx += 1
    return phones


def _build_companies(profile: WorldProfile, people: list[TruePerson], rng: random.Random) -> list[Company]:
    companies = []
    n = len(people)
    for i in range(profile.companies):
        d1 = people[i % n].person_id
        d2 = people[(i * 7 + 3) % n].person_id
        directors = (d1,) if d1 == d2 else (d1, d2)
        org_id = ORG_ID.format(500_000 + i)
        incorporated = profile.start_date - datetime.timedelta(days=rng.randint(100, profile.history_days))
        companies.append(
            Company(
                org_id=org_id,
                reg_no=f"REG{500_000 + i:06d}",
                name=f"{rng.choice(TOWNS).split()[0]} {rng.choice(['Traders', 'Enterprises', 'Textiles', 'Logistics', 'Agro'])} Pvt Ltd",
                incorporated=incorporated,
                address_key=_plausible_address(rng),
                director_person_ids=directors,
            )
        )
    return companies


def _build_vehicles(profile: WorldProfile, people: list[TruePerson], rng: random.Random) -> list[Vehicle]:
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    n = len(people)
    vehicles = []
    for i in range(profile.vehicles):
        n_letters = len(letters)
        reg = f"DL{(i % 99) + 1:02d}{letters[i % n_letters]}{letters[(i // n_letters) % n_letters]}{1000 + i}"
        vehicles.append(
            Vehicle(vehicle_id=VEHICLE_ID.format(i), registration=reg, owner_person_id=people[i % n].person_id)
        )
    return vehicles


def _build_towers(profile: WorldProfile) -> list[Tower]:
    return [
        Tower(tower_id=f"TWR_{k:04d}", name=f"Tower {k}", lat=20.0 + k * 0.01, lon=78.0 + k * 0.01, footprint_m=500)
        for k in range(profile.towers)
    ]


def _build_population(
    profile: WorldProfile, rng: random.Random
) -> tuple[Population, list[TruePerson]]:
    """`generated` (people made for this run, excluding the fixed-ID identity
    traps) is returned alongside the `Population` because FIR filler slots
    and noise draw from it directly."""
    trap_people = [
        IDENTITY_TRAPS["mohammad_ali"]["person"],
        *IDENTITY_TRAPS["raj_kumar"]["persons"],
        IDENTITY_TRAPS["chatterjee"]["person"],
        IDENTITY_TRAPS["azhagiri"]["person"],
    ]
    trap_names = {p.canonical_name for p in trap_people}

    # A random FIRST_NAMES x SURNAMES draw can land exactly on a trap's name
    # (e.g. "Raj" + "Kumar"); variants_for() is a pure function of
    # canonical_name, so that collision would silently mint a third
    # "Raj Kumar" carrying the trap's own surfaces (prd §4 beat 3 needs
    # exactly two). Over-generate and drop matches rather than edit
    # names.py, which this module doesn't own.
    n_people = max(profile.accounts + profile.phone_regs, profile.people)
    raw = make_people(n_people + 50, rng, start_id=1)
    generated = [p for p in raw if p.canonical_name not in trap_names][:n_people]
    if len(generated) < n_people:
        raise ValueError("ran out of non-colliding generated people; raise the margin")

    account_holders = generated[: profile.accounts]
    phone_subs = generated[profile.accounts : profile.accounts + profile.phone_regs]

    accounts = _build_accounts(profile, account_holders, rng)
    phones = _build_phones(profile, phone_subs, rng)
    companies = _build_companies(profile, generated, rng)
    vehicles = _build_vehicles(profile, generated, rng)
    towers = _build_towers(profile)

    pop = Population(
        people=(*trap_people, *generated),
        accounts=tuple(accounts),
        phones=tuple(phones),
        companies=tuple(companies),
        vehicles=tuple(vehicles),
        towers=tuple(towers),
    )
    return pop, generated


# --- FIR rendering --------------------------------------------------------


@dataclass
class _FirCtx:
    profile: WorldProfile
    people_pool: list[TruePerson]
    pop: Population


def _build_fir_slots(
    family: str, rng: random.Random, ctx: _FirCtx
) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """Returns (slot -> surface text, slot -> (person_id, script)) for the
    slots whose entity_type is a person."""
    slots: dict[str, str] = {}
    person_map: dict[str, tuple[str, str]] = {}
    for slot_name, etype in REQUIRED_SLOTS[family].items():
        if etype in PERSON_ENTITY_TYPES:
            person = rng.choice(ctx.people_pool)
            variant = _pick_variant(person, rng)
            slots[slot_name] = variant.surface
            person_map[slot_name] = (person.person_id, variant.script)
        elif etype == "Location":
            slots[slot_name] = rng.choice(TOWNS)
        elif etype == "DateTime":
            slots[slot_name] = _random_date_str(rng, ctx.profile)
        elif etype == "Vehicle":
            slots[slot_name] = rng.choice(ctx.pop.vehicles).registration
        elif etype == "Phone":
            slots[slot_name] = rng.choice(ctx.pop.phones).msisdn
        elif etype == "Account":
            slots[slot_name] = rng.choice(ctx.pop.accounts).account_no
        elif etype == "Organization":
            slots[slot_name] = rng.choice(ctx.pop.companies).name
        elif etype == "Amount":
            slots[slot_name] = _indian_amount(rng)
        else:
            raise ValueError(f"unhandled entity_type {etype!r}")
    return slots, person_map


def _render_and_record(
    family: str,
    fir_no: str,
    fir_id: str,
    rng: random.Random,
    ctx: _FirCtx,
    legal_basis: str,
    mentions: list[GoldMention],
    fir_truth: dict[str, dict],
    forced_slots: dict[str, str] | None = None,
    forced_person_map: dict[str, tuple[str, str]] | None = None,
    language: str | None = None,
) -> dict:
    slots, person_map = _build_fir_slots(family, rng, ctx)
    if forced_slots:
        slots.update(forced_slots)
    if forced_person_map:
        person_map.update(forced_person_map)

    narrative = render_fir(family, slots, rng, language=language)

    for span in narrative.spans:
        if span.slot in person_map:
            person_id, script = person_map[span.slot]
            mentions.append(
                GoldMention(
                    source_record_id=fir_id, field=span.slot, surface=span.surface, script=script, person_id=person_id
                )
            )

    fir_truth[fir_id] = {
        "fir_no": fir_no,
        "family": narrative.family,
        "split": narrative.split,
        "language": narrative.language,
        "offence_code_system": narrative.offence_code_system,
        "offence_section": narrative.offence_section,
        "spans": [
            {"slot": s.slot, "start": s.start, "end": s.end, "surface": s.surface, "entity_type": s.entity_type}
            for s in narrative.spans
        ],
        "relations": [
            {"head_slot": r.head_slot, "tail_slot": r.tail_slot, "rel_type": r.rel_type} for r in narrative.relations
        ],
    }

    return {
        "source_record_id": fir_id,
        "source_system": "fir_system",
        "record_type": "fir",
        "legal_basis": legal_basis,
        "fir_no": fir_no,
        "text": narrative.text,
        "language": narrative.language,
        "family": narrative.family,
        "split": narrative.split,
        "offence_code_system": narrative.offence_code_system,
        "offence_section": narrative.offence_section,
    }


# --- Identity traps ---------------------------------------------------------


def _place_identity_traps(
    rng: random.Random,
    ctx: _FirCtx,
    mentions: list[GoldMention],
    fir_truth: dict[str, dict],
) -> tuple[list[dict], list[Account], list[Phone], list[Company]]:
    """Places the four identity traps (prd §4 beat 2/3, §7) in the exact
    sources their surfaces require. Returns the extra FIR records, plus the
    extra accounts/phones/companies minted to carry the KYC/registration/
    register surfaces."""
    firs: list[dict] = []
    accounts: list[Account] = []
    phones: list[Phone] = []
    companies: list[Company] = []

    # Trap-minted ids get ordinary architecture-§5.3-shaped ids in a small
    # reserved band (clear of every bulk range), never a "TRAP" token — a
    # record must not announce its own role in the test design.
    _TRAP_ID_BASE = 900_000
    fir_counter = 0
    account_counter = 0
    phone_counter = 0
    org_counter = 0

    def _next_fir_id() -> str:
        nonlocal fir_counter
        fir_counter += 1
        return f"FIR_{_TRAP_ID_BASE + fir_counter:06d}"

    def _next_account_id() -> str:
        nonlocal account_counter
        account_counter += 1
        return ACCOUNT_ID.format(_TRAP_ID_BASE + account_counter)

    def _next_phone_id() -> str:
        nonlocal phone_counter
        phone_counter += 1
        return PHONE_ID.format(_TRAP_ID_BASE + phone_counter)

    def _next_org_id() -> str:
        nonlocal org_counter
        org_counter += 1
        return ORG_ID.format(_TRAP_ID_BASE + org_counter)

    # --- Mohammad Ali: one surface, one source each, exactly as specified.
    ma_trap = IDENTITY_TRAPS["mohammad_ali"]
    ma_person = ma_trap["person"]
    for surf in ma_trap["surfaces"]:
        v = surf.variant
        if surf.source_type == "fir":
            fir_id = _next_fir_id()
            firs.append(
                _render_and_record(
                    "seizure",
                    f"10{fir_counter}/2025",
                    fir_id,
                    rng,
                    ctx,
                    "LB-GENERIC-001",
                    mentions,
                    fir_truth,
                    forced_slots={"accused_1": v.surface},
                    forced_person_map={"accused_1": (ma_person.person_id, v.script)},
                )
            )
        elif surf.source_type == "bank_kyc":
            account = Account(
                account_id=_next_account_id(),
                account_no=str(900_000_000 + account_counter),
                holder_person_id=ma_person.person_id,
                opened=ctx.profile.start_date - datetime.timedelta(days=200),
                bank="Demo Bank",
                kyc_status="verified",
            )
            accounts.append(account)
            mentions.append(
                GoldMention(
                    source_record_id=f"KYC_{account.account_id}",
                    field="holder_name",
                    surface=v.surface,
                    script=v.script,
                    person_id=ma_person.person_id,
                )
            )
        elif surf.source_type == "phone_registration":
            phone = Phone(
                phone_id=_next_phone_id(),
                msisdn="9999900001",
                subscriber_person_id=ma_person.person_id,
                activated=ctx.profile.start_date - datetime.timedelta(days=500),
                deactivated=None,
                imsi=f"IMSI{_TRAP_ID_BASE + phone_counter:09d}",
                seller=rng.choice(_DEALER_NAMES),
            )
            phones.append(phone)
            mentions.append(
                GoldMention(
                    source_record_id=f"PHONEREG_{phone.phone_id}",
                    field="subscriber_name",
                    surface=v.surface,
                    script=v.script,
                    person_id=ma_person.person_id,
                )
            )
        elif surf.source_type == "company_register":
            company = Company(
                org_id=_next_org_id(),
                reg_no=f"REG{_TRAP_ID_BASE + org_counter:06d}",
                name="Ali Traders Pvt Ltd",
                incorporated=ctx.profile.start_date - datetime.timedelta(days=300),
                address_key=_plausible_address(rng),
                director_person_ids=(ma_person.person_id,),
            )
            companies.append(company)
            mentions.append(
                GoldMention(
                    source_record_id=f"COMPANY_{company.org_id}",
                    field="directors[0]",
                    surface=v.surface,
                    script=v.script,
                    person_id=ma_person.person_id,
                )
            )
        else:
            raise ValueError(f"unknown trap source_type {surf.source_type!r}")

    # --- Raj Kumar: two people, each with their own FIR and their own phone.
    rk_trap = IDENTITY_TRAPS["raj_kumar"]
    rk_surfaces = rk_trap["surfaces"]
    rk_families = ("recovery", "cheating")  # distinct families, so the two read differently
    for i, person in enumerate(rk_trap["persons"]):
        v = rk_surfaces[i % len(rk_surfaces)]
        phone = Phone(
            phone_id=_next_phone_id(),
            msisdn=f"999990001{i}",
            subscriber_person_id=person.person_id,
            activated=ctx.profile.start_date - datetime.timedelta(days=600 + i),
            deactivated=None,
            imsi=f"IMSI{_TRAP_ID_BASE + phone_counter:09d}",
            seller=rng.choice(_DEALER_NAMES),
        )
        phones.append(phone)
        mentions.append(
            GoldMention(
                source_record_id=f"PHONEREG_{phone.phone_id}",
                field="subscriber_name",
                surface=v.surface,
                script=v.script,
                person_id=person.person_id,
            )
        )
        fir_id = _next_fir_id()
        firs.append(
            _render_and_record(
                rk_families[i % len(rk_families)],
                f"10{fir_counter}/2025",
                fir_id,
                rng,
                ctx,
                "LB-GENERIC-001",
                mentions,
                fir_truth,
                forced_slots={"accused_1": v.surface},
                forced_person_map={"accused_1": (person.person_id, v.script)},
            )
        )

    # --- Chatterjee: FIR (exact) + company register (formal surname).
    ct_trap = IDENTITY_TRAPS["chatterjee"]
    ct_person = ct_trap["person"]
    ct_surfaces = ct_trap["surfaces"]
    fir_id = _next_fir_id()
    firs.append(
        _render_and_record(
            "extortion",
            f"10{fir_counter}/2025",
            fir_id,
            rng,
            ctx,
            "LB-GENERIC-001",
            mentions,
            fir_truth,
            forced_slots={"accused_1": ct_surfaces[0].surface},
            forced_person_map={"accused_1": (ct_person.person_id, ct_surfaces[0].script)},
        )
    )
    formal = ct_surfaces[2]
    ct_company = Company(
        org_id=_next_org_id(),
        reg_no=f"REG{_TRAP_ID_BASE + org_counter:06d}",
        name="Chatterjee & Co Pvt Ltd",
        incorporated=ctx.profile.start_date - datetime.timedelta(days=400),
        address_key=_plausible_address(rng),
        director_person_ids=(ct_person.person_id,),
    )
    companies.append(ct_company)
    mentions.append(
        GoldMention(
            source_record_id=f"COMPANY_{ct_company.org_id}",
            field="directors[0]",
            surface=formal.surface,
            script=formal.script,
            person_id=ct_person.person_id,
        )
    )

    # --- Azhagiri: FIR (exact) + phone registration (spelling variant).
    az_trap = IDENTITY_TRAPS["azhagiri"]
    az_person = az_trap["person"]
    az_surfaces = az_trap["surfaces"]
    fir_id = _next_fir_id()
    firs.append(
        _render_and_record(
            "complaint",
            f"10{fir_counter}/2025",
            fir_id,
            rng,
            ctx,
            "LB-GENERIC-001",
            mentions,
            fir_truth,
            forced_slots={"accused_1": az_surfaces[0].surface},
            forced_person_map={"accused_1": (az_person.person_id, az_surfaces[0].script)},
        )
    )
    az_phone = Phone(
        phone_id=_next_phone_id(),
        msisdn="9999900099",
        subscriber_person_id=az_person.person_id,
        activated=ctx.profile.start_date - datetime.timedelta(days=450),
        deactivated=None,
        imsi=f"IMSI{_TRAP_ID_BASE + phone_counter:09d}",
        seller=rng.choice(_DEALER_NAMES),
    )
    phones.append(az_phone)
    mentions.append(
        GoldMention(
            source_record_id=f"PHONEREG_{az_phone.phone_id}",
            field="subscriber_name",
            surface=az_surfaces[1].surface,
            script=az_surfaces[1].script,
            person_id=az_person.person_id,
        )
    )

    return firs, accounts, phones, companies


# --- Main orchestration ------------------------------------------------------


def generate_world(out_dir: Path, profile: WorldProfile) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    master = random.Random(profile.seed)

    def child() -> random.Random:
        return random.Random(master.getrandbits(64))

    rng_population = child()
    pop, generated = _build_population(profile, rng_population)

    rng_demo_net = child()
    rng_bg_net = child()
    rng_lookalikes = child()
    claimed: set[str] = set()
    demo_structs = inject_demo_networks(
        pop, rng_demo_net, threshold_inr=profile.synthetic_threshold_inr,
        start=profile.start_date, end=profile.end_date, claimed=claimed,
    )
    bg_structs = inject_background_networks(
        pop, rng_bg_net, n=profile.background_networks, threshold_inr=profile.synthetic_threshold_inr,
        start=profile.start_date, end=profile.end_date, claimed=claimed,
    )
    la_structs = inject_lookalikes(
        pop, rng_lookalikes, threshold_inr=profile.synthetic_threshold_inr,
        start=profile.start_date, end=profile.end_date, claimed=claimed,
    )
    all_structs = [*demo_structs, *bg_structs, *la_structs]

    structure_companies = [c for s in all_structs for c in s.companies]
    structure_org_accounts = [shell_org_account(c) for s in all_structs for c in s.companies]

    mentions: list[GoldMention] = []
    fir_truth: dict[str, dict] = {}
    person_by_id = {p.person_id: p for p in pop.people}

    rng_traps = child()
    ctx = _FirCtx(profile=profile, people_pool=generated, pop=pop)
    trap_firs, trap_accounts, trap_phones, trap_companies = _place_identity_traps(
        rng_traps, ctx, mentions, fir_truth
    )

    # --- The demo case: FIR 224/2025 must name someone inside N1, or M5's
    # 2-hop case graph and M9's top lead have nothing to connect to (see
    # NOTES.md's M1 fix-round entry). Person C is the person who receives
    # N1's final payment — the end of the shell chain's money trail.
    n1 = demo_structs[0]
    account_by_id = {a.account_id: a for a in pop.accounts}
    n1_dest_account = account_by_id[n1.account_ids[-1]]
    person_c = person_by_id[n1_dest_account.holder_person_id]
    n1_company = n1.companies[-1]

    rng_demo_fir = child()
    # Must sit in the reserved band with the other dedicated records: the bulk
    # FIRs are FIR_000000..FIR_0004NN, so "FIR_000224" collided with bulk #224
    # and the upsert silently dropped one of the two. The human-facing number
    # stays 224/2025 (prd §4) — that is what the demo refers to, not this id.
    demo_fir_id = "FIR_900000"
    demo_variant = _pick_variant(person_c, rng_demo_fir)
    demo_fir_record = _render_and_record(
        "fraud",
        DEMO_FIR_NO,
        demo_fir_id,
        rng_demo_fir,
        ctx,
        "LB-CASE-0231",
        mentions,
        fir_truth,
        forced_slots={
            "accused_1": demo_variant.surface,
            "account_1": n1_dest_account.account_no,
            "org_1": n1_company.name,
        },
        forced_person_map={"accused_1": (person_c.person_id, demo_variant.script)},
        # The demo audience reads this record most closely (prd §4 beat 5), and
        # the prd's own excerpt is English. Other FIRs keep the code-mixed spread.
        language="en",
    )

    # --- Noise FIRs, filling out the configured `firs` total.
    rng_noise_fir = child()
    dedicated_count = 1 + len(trap_firs)
    noise_count = max(0, profile.firs - dedicated_count)
    noise_firs: list[dict] = []
    for i in range(noise_count):
        family = rng_noise_fir.choice(ALL_FAMILIES)
        fir_id = f"FIR_{i:06d}"
        fir_no = f"{500 + i}/2025"
        noise_firs.append(
            _render_and_record(family, fir_no, fir_id, rng_noise_fir, ctx, "LB-GENERIC-001", mentions, fir_truth)
        )

    all_fir_records = [demo_fir_record, *trap_firs, *noise_firs]

    # --- Accounts / phones / companies output lists (generated + structure + trap).
    all_accounts = [*pop.accounts, *structure_org_accounts, *trap_accounts]
    all_phones = [*pop.phones, *trap_phones]
    all_companies = [*pop.companies, *structure_companies, *trap_companies]

    company_by_id = {c.org_id: c for c in all_companies}

    person_surfaces: dict[str, set[tuple[str, str]]] = {}

    def _note_surface(person_id: str, surface: str, script: str) -> None:
        person_surfaces.setdefault(person_id, set()).add((surface, script))

    for m in mentions:
        _note_surface(m.person_id, m.surface, m.script)

    # --- Render account (KYC), phone registration and company records.
    # Trap accounts/phones already got their one authoritative name from
    # `_place_identity_traps`; a second, generic pick here would overwrite
    # the record's actual field and leave truth.json with two mentions for
    # one single-valued field (only one holder_name / subscriber_name can be
    # true at once) — so those ids are excluded from the generic pass below.
    trap_account_ids = {a.account_id for a in trap_accounts}
    trap_phone_ids = {p.phone_id for p in trap_phones}

    rng_records = child()
    account_records = []
    for account in all_accounts:
        if account.account_id in trap_account_ids:
            holder_name = next(m.surface for m in mentions if m.source_record_id == f"KYC_{account.account_id}")
            holder_kind = "person"
        elif account.holder_person_id is not None:
            person = person_by_id[account.holder_person_id]
            variant = _pick_variant(person, rng_records)
            holder_name = variant.surface
            holder_kind = "person"
            _note_surface(person.person_id, variant.surface, variant.script)
            mentions.append(
                GoldMention(
                    source_record_id=f"KYC_{account.account_id}",
                    field="holder_name",
                    surface=variant.surface,
                    script=variant.script,
                    person_id=person.person_id,
                )
            )
        else:
            holder_name = company_by_id[account.holder_org_id].name
            holder_kind = "organization"
        account_records.append(
            {
                "source_record_id": f"KYC_{account.account_id}",
                "source_system": "bank_kyc_system",
                "record_type": "kyc",
                "legal_basis": "LB-GENERIC-001",
                "account_id": account.account_id,
                "account_no": account.account_no,
                "holder_name": holder_name,
                "holder_kind": holder_kind,
                "opened": account.opened,
                "bank": account.bank,
                "kyc_status": account.kyc_status,
            }
        )

    phone_records = []
    for phone in all_phones:
        if phone.phone_id in trap_phone_ids:
            subscriber_name = next(
                m.surface for m in mentions if m.source_record_id == f"PHONEREG_{phone.phone_id}"
            )
        else:
            person = person_by_id[phone.subscriber_person_id]
            variant = _pick_variant(person, rng_records)
            subscriber_name = variant.surface
            _note_surface(person.person_id, variant.surface, variant.script)
            mentions.append(
                GoldMention(
                    source_record_id=f"PHONEREG_{phone.phone_id}",
                    field="subscriber_name",
                    surface=variant.surface,
                    script=variant.script,
                    person_id=person.person_id,
                )
            )
        phone_records.append(
            {
                "source_record_id": f"PHONEREG_{phone.phone_id}",
                "source_system": "phone_registration_system",
                "record_type": "phone_reg",
                "legal_basis": "LB-GENERIC-001",
                "phone_id": phone.phone_id,
                "msisdn": phone.msisdn,
                "subscriber_name": subscriber_name,
                "activated": phone.activated,
                "deactivated": phone.deactivated,
                "imsi": phone.imsi,
                "seller": phone.seller,
            }
        )

    company_records = []
    trap_company_ids = {c.org_id for c in trap_companies}
    for company in all_companies:
        if company.org_id in trap_company_ids:
            # Directors' surfaces were already fixed and recorded by
            # `_place_identity_traps`; reuse what it recorded verbatim.
            directors = [
                {"surface": m.surface, "script": m.script}
                for m in mentions
                if m.source_record_id == f"COMPANY_{company.org_id}"
            ]
        else:
            directors = []
            for person_id in company.director_person_ids:
                person = person_by_id[person_id]
                variant = _pick_variant(person, rng_records)
                _note_surface(person.person_id, variant.surface, variant.script)
                mentions.append(
                    GoldMention(
                        source_record_id=f"COMPANY_{company.org_id}",
                        field=f"directors[{len(directors)}]",
                        surface=variant.surface,
                        script=variant.script,
                        person_id=person.person_id,
                    )
                )
                # No person_id here — a real director register states a name,
                # not a database id; the answer belongs only in truth.json.
                directors.append({"surface": variant.surface, "script": variant.script})
        company_records.append(
            {
                "source_record_id": f"COMPANY_{company.org_id}",
                "source_system": "company_register_system",
                "record_type": "company",
                "legal_basis": "LB-GENERIC-001",
                "org_id": company.org_id,
                "reg_no": company.reg_no,
                "name": company.name,
                "incorporated": company.incorporated,
                "address_key": company.address_key,
                "directors": directors,
            }
        )

    # A real RC record states the owner's name, not a database id — the
    # same reasoning as KYC/phone_reg above (and directors, just fixed).
    vehicle_records = []
    for v in pop.vehicles:
        person = person_by_id[v.owner_person_id]
        variant = _pick_variant(person, rng_records)
        _note_surface(person.person_id, variant.surface, variant.script)
        mentions.append(
            GoldMention(
                source_record_id=f"VEHICLE_{v.vehicle_id}",
                field="owner_name",
                surface=variant.surface,
                script=variant.script,
                person_id=person.person_id,
            )
        )
        vehicle_records.append(
            {
                "source_record_id": f"VEHICLE_{v.vehicle_id}",
                "source_system": "vehicle_registry_system",
                "record_type": "vehicle",
                "legal_basis": "LB-GENERIC-001",
                "vehicle_id": v.vehicle_id,
                "registration": v.registration,
                "owner_name": variant.surface,
                "owner_script": variant.script,
            }
        )

    tower_records = [
        {"tower_id": t.tower_id, "name": t.name, "lat": t.lat, "lon": t.lon, "footprint_m": t.footprint_m}
        for t in pop.towers
    ]

    # --- CDR and transaction records: structure-embedded first, then noise
    # padded out to the configured totals (architecture.md §6.1).
    rng_cdr_noise = child()
    rng_txn_noise = child()

    structure_calls = [c for s in all_structs for c in s.calls]
    structure_transfers = [t for s in all_structs for t in s.transfers]

    cdr_records = []
    for i, call in enumerate(structure_calls):
        cdr_records.append(
            {
                "source_record_id": f"CDR_{i:07d}",
                "source_system": "cdr_system",
                "record_type": "cdr",
                "legal_basis": "LB-GENERIC-001",
                "calling_phone_id": call.calling_phone_id,
                "called_phone_id": call.called_phone_id,
                "ts": call.ts,
                "duration_s": call.duration_s,
                "tower_id": call.tower_id,
            }
        )
    noise_cdr_count = max(0, profile.cdr_rows - len(cdr_records))
    span_days = max((profile.end_date - profile.start_date).days, 1)
    for j in range(noise_cdr_count):
        i = len(cdr_records)
        a, b = rng_cdr_noise.sample(range(len(pop.phones)), 2)
        ts = datetime.datetime.combine(
            profile.start_date + datetime.timedelta(days=rng_cdr_noise.randint(0, span_days)),
            datetime.time(rng_cdr_noise.randint(0, 23), rng_cdr_noise.randint(0, 59)),
        )
        cdr_records.append(
            {
                "source_record_id": f"CDR_{i:07d}",
                "source_system": "cdr_system",
                "record_type": "cdr",
                "legal_basis": "LB-GENERIC-001",
                "calling_phone_id": pop.phones[a].phone_id,
                "called_phone_id": pop.phones[b].phone_id,
                "ts": ts,
                "duration_s": rng_cdr_noise.randint(10, 600),
                "tower_id": rng_cdr_noise.choice(pop.towers).tower_id,
            }
        )

    txn_records = []
    for transfer in structure_transfers:
        txn_records.append(
            {
                "source_record_id": transfer.txn_id,
                "source_system": "txn_system",
                "record_type": "txn",
                "legal_basis": "LB-GENERIC-001",
                "from_account_id": transfer.from_account_id,
                "to_account_id": transfer.to_account_id,
                "amount_inr": transfer.amount_inr,
                "ts": transfer.ts,
                "channel": transfer.channel,
            }
        )
    noise_txn_count = max(0, profile.txns - len(txn_records))
    for _ in range(noise_txn_count):
        a, b = rng_txn_noise.sample(range(len(pop.accounts)), 2)
        ts = datetime.datetime.combine(
            profile.start_date + datetime.timedelta(days=rng_txn_noise.randint(0, span_days)),
            datetime.time(rng_txn_noise.randint(0, 23), rng_txn_noise.randint(0, 59)),
        )
        i = len(txn_records)
        txn_records.append(
            {
                "source_record_id": f"TXN_{i:07d}",
                "source_system": "txn_system",
                "record_type": "txn",
                "legal_basis": "LB-GENERIC-001",
                "from_account_id": pop.accounts[a].account_id,
                "to_account_id": pop.accounts[b].account_id,
                "amount_inr": rng_txn_noise.randint(500, 100_000),
                "ts": ts,
                "channel": rng_txn_noise.choice(["NEFT", "IMPS", "RTGS"]),
            }
        )

    # --- Deliberately drop legal_basis from 5 records (never the demo FIR).
    rng_legal = child()
    candidate_ids = sorted(
        r["source_record_id"]
        for r in [
            *all_fir_records, *cdr_records, *txn_records, *account_records, *phone_records,
            *company_records, *vehicle_records,
        ]
        if r["source_record_id"] != demo_fir_id
    )
    missing_ids = sorted(rng_legal.sample(candidate_ids, min(5, len(candidate_ids))))
    missing_set = set(missing_ids)
    for record_list in (
        all_fir_records, cdr_records, txn_records, account_records, phone_records, company_records, vehicle_records,
    ):
        for r in record_list:
            if r["source_record_id"] in missing_set:
                r["legal_basis"] = None

    # --- Write everything.
    _write_jsonl(out_dir / "firs.jsonl", all_fir_records)
    _write_jsonl(out_dir / "cdr.jsonl", cdr_records)
    _write_jsonl(out_dir / "txns.jsonl", txn_records)
    _write_jsonl(out_dir / "accounts.jsonl", account_records)
    _write_jsonl(out_dir / "phone_regs.jsonl", phone_records)
    _write_jsonl(out_dir / "companies.jsonl", company_records)
    _write_jsonl(out_dir / "vehicles.jsonl", vehicle_records)
    _write_jsonl(out_dir / "towers.jsonl", tower_records)

    cases = [
        {
            "case_id": DEMO_CASE_ID,
            "title": "Case 0231",
            "anchor_record_id": demo_fir_id,
            "legal_basis": "LB-CASE-0231",
            "status": "open",
            "assigned_to": "io.patil",
        }
    ]
    _write_json(out_dir / "cases.json", cases)
    _write_json(out_dir / "users.json", DEMO_USERS)

    all_people = list(pop.people)
    output = WorldOutput(population=pop, structures=all_structs, mentions=mentions)
    truth = truth_mod.build_truth(
        output,
        seed=profile.seed,
        all_people=all_people,
        person_surfaces=person_surfaces,
        fir_truth=fir_truth,
        missing_legal_basis_ids=missing_ids,
        demo_case={
            "case_id": DEMO_CASE_ID,
            "anchor_record_id": demo_fir_id,
            "fir_no": DEMO_FIR_NO,
            "person_c_id": person_c.person_id,
            "assigned_to": "io.patil",
        },
    )
    _write_json(out_dir / "truth.json", truth)


def main() -> None:
    settings = get_settings()
    profile = WorldProfile.from_settings(settings)
    generate_world(REPO_ROOT / "data" / "world", profile)


if __name__ == "__main__":
    main()
