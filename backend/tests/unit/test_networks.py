import datetime
import os
import random
import subprocess
import sys
from collections import Counter

from cid.pipeline.generate.lookalikes import inject_lookalikes
from cid.pipeline.generate.names import make_people
from cid.pipeline.generate.networks import (
    inject_background_networks,
    inject_demo_networks,
    shell_org_account,
)
from cid.pipeline.generate.specs import Account, Phone, Population, Tower

START = datetime.date(2022, 1, 1)
END = datetime.date(2023, 6, 1)
THRESHOLD_INR = 50_000

_HISTORY_DAYS = 1000  # how far before START the oldest accounts were opened
_ACCOUNTS_PER_DAY = 3  # dense enough that exclusivity claims across many
# structures never starve a mule fan-out's opened-date window
_N_BATCHES = 20
_BATCH_SIZE = 12
_N_LONGTERM_PHONES = 400


def _build_population(seed: int = 1) -> Population:
    """A small district: dense day-by-day account coverage (so any window a
    network picks has enough unclaimed candidates) plus several batch-
    activated phone groups (the T-04 signal). One person per account and per
    phone — no accidental holder/subscriber collisions to trip up a test's
    assumptions."""
    rng = random.Random(seed)

    account_days = (END - START).days + _HISTORY_DAYS + 1
    account_span = account_days * _ACCOUNTS_PER_DAY
    phone_span = _N_BATCHES * _BATCH_SIZE + _N_LONGTERM_PHONES
    people = make_people(account_span + phone_span, rng)

    accounts = []
    idx = 0
    for day_offset in range(account_days):
        opened = START - datetime.timedelta(days=_HISTORY_DAYS) + datetime.timedelta(days=day_offset)
        for _ in range(_ACCOUNTS_PER_DAY):
            accounts.append(
                Account(
                    account_id=f"ACC_{idx:06d}",
                    account_no=str(100_000_000 + idx),
                    holder_person_id=people[idx].person_id,
                    opened=opened,
                    bank="Demo Bank",
                    kyc_status="verified",
                )
            )
            idx += 1

    phones = []
    idx = 0
    for batch in range(_N_BATCHES):
        batch_start = START + datetime.timedelta(days=15 * batch + 10)
        seller = f"Seller{batch}"
        for _ in range(_BATCH_SIZE):
            phones.append(
                Phone(
                    phone_id=f"PHN_{idx:06d}",
                    msisdn=str(9_000_000_000 + idx),
                    subscriber_person_id=people[account_span + idx].person_id,
                    activated=batch_start,
                    deactivated=batch_start + datetime.timedelta(days=20),
                    imsi=f"IMSI{idx:09d}",
                    seller=seller,
                )
            )
            idx += 1
    for _ in range(_N_LONGTERM_PHONES):
        phones.append(
            Phone(
                phone_id=f"PHN_{idx:06d}",
                msisdn=str(9_000_000_000 + idx),
                subscriber_person_id=people[account_span + idx].person_id,
                activated=START - datetime.timedelta(days=800),
                deactivated=None,
                imsi=f"IMSI{idx:09d}",
                seller="LongTerm",
            )
        )
        idx += 1

    towers = tuple(
        Tower(tower_id=f"TWR_{k:04d}", name=f"Tower {k}", lat=20.0 + k * 0.01, lon=78.0 + k * 0.01, footprint_m=500)
        for k in range(5)
    )

    return Population(
        people=tuple(people),
        accounts=tuple(accounts),
        phones=tuple(phones),
        companies=(),
        vehicles=(),
        towers=towers,
    )


def _demo(seed: int = 42):
    pop = _build_population()
    rng = random.Random(seed)
    n1, n2, n3 = inject_demo_networks(pop, rng, threshold_inr=THRESHOLD_INR, start=START, end=END)
    return pop, n1, n2, n3


# --- N1 — shell chain around Person A (T-01, T-08) --------------------------


def test_n1_shell_chain_typology_conditions():
    pop, n1, _, _ = _demo()

    assert n1.structure_id == "N1"
    assert set(n1.typologies) == {"T-01", "T-08"}
    assert n1.is_criminal is True
    assert len(n1.companies) == 2  # >= 2 hops
    assert len(n1.transfers) == 3  # source->hop1->hop2->dest

    orgs = n1.companies
    assert set(orgs[0].director_person_ids) & set(orgs[1].director_person_ids), "must share a director"
    assert orgs[0].address_key == orgs[1].address_key, "must share a registered address"

    hop_account_ids = n1.account_ids[1:-1]
    assert len(hop_account_ids) == 2
    for company, hop_id in zip(orgs, hop_account_ids):
        # Org ownership, directly: the hop account really is held by the
        # company (holder_org_id), not by a person.
        hop_account = shell_org_account(company)
        assert hop_account.account_id == hop_id
        assert hop_account.holder_org_id == company.org_id
        assert hop_account.holder_person_id is None

        inbound = [t for t in n1.transfers if t.to_account_id == hop_id]
        outbound = [t for t in n1.transfers if t.from_account_id == hop_id]
        assert len(inbound) == 1
        assert len(outbound) == 1
        gap_days = (inbound[0].ts.date() - company.incorporated).days
        assert 0 <= gap_days < 90, "incorporated < 90 days before first transfer in"
        ratio = outbound[0].amount_inr / inbound[0].amount_inr
        assert ratio > 0.9, "pass-through ratio must keep < 10%"

    person_a = next(iter(set(orgs[0].director_person_ids) & set(orgs[1].director_person_ids)))
    acct_by_id = {a.account_id: a for a in pop.accounts}
    owned = [aid for aid in n1.account_ids if acct_by_id.get(aid) and acct_by_id[aid].holder_person_id == person_a]
    directed = [c for c in n1.companies if person_a in c.director_person_ids]
    assert len(owned) + len(directed) == 3, "Person A must have exactly 3 direct links"


# --- N2 — mule fan-out (T-02 and T-03) --------------------------------------


def test_n2_mule_fanout_typology_conditions():
    pop, _, n2, _ = _demo()

    assert n2.structure_id == "N2"
    assert set(n2.typologies) == {"T-02", "T-03"}

    froms = Counter(t.from_account_id for t in n2.transfers)
    hub_id, _ = froms.most_common(1)[0]
    hub_transfers = sorted((t for t in n2.transfers if t.from_account_id == hub_id), key=lambda t: t.ts)

    assert len(hub_transfers) >= 8, "hub must fan out to >= 8 accounts"
    mule_ids = {t.to_account_id for t in hub_transfers}
    assert len(mule_ids) == len(hub_transfers)
    assert all(t.amount_inr < THRESHOLD_INR for t in hub_transfers), "all sub-threshold"

    acct_by_id = {a.account_id: a for a in pop.accounts}
    holding_hours = []
    for t_in in hub_transfers:
        mule = acct_by_id[t_in.to_account_id]
        gap_days = (t_in.ts.date() - mule.opened).days
        assert 0 <= gap_days < 60, "mule account opened < 60 days before receipt"
        t_out = next(t for t in n2.transfers if t.from_account_id == t_in.to_account_id)
        holding_hours.append((t_out.ts - t_in.ts).total_seconds() / 3600)

    holding_hours.sort()
    mid = len(holding_hours) // 2
    median_hours = (
        holding_hours[mid]
        if len(holding_hours) % 2
        else (holding_hours[mid - 1] + holding_hours[mid]) / 2
    )
    assert median_hours < 48, "median holding time must be < 48 h"

    timestamps = sorted(t.ts for t in hub_transfers)
    window = datetime.timedelta(hours=72)
    assert any(
        sum(1 for ts in timestamps if t0 <= ts <= t0 + window) >= 5 for t0 in timestamps
    ), ">= 5 sub-threshold transfers inside some 72 h window"


# --- N3 — burner tree + night ring (T-04, T-05) -----------------------------


def test_n3_burner_tree_and_night_ring_typology_conditions():
    pop, _, _, n3 = _demo()

    assert n3.structure_id == "N3"
    assert set(n3.typologies) == {"T-04", "T-05"}

    phone_by_id = {p.phone_id: p for p in pop.phones}
    called = Counter(c.called_phone_id for c in n3.calls)
    persistent_id, _ = called.most_common(1)[0]
    callers = {c.calling_phone_id for c in n3.calls if c.called_phone_id == persistent_id}

    assert len(callers) >= 5, ">= 5 burner phones"
    activated_dates = {phone_by_id[pid].activated for pid in callers}
    sellers = {phone_by_id[pid].seller for pid in callers}
    assert len(activated_dates) == 1, "same activation day"
    assert len(sellers) == 1, "same seller (batch signal)"

    for pid in callers:
        phone = phone_by_id[pid]
        last = phone.deactivated or END
        assert (last - phone.activated).days < 45, "active < 45 days"
        this_phone_calls = Counter(c.called_phone_id for c in n3.calls if c.calling_phone_id == pid)
        top_contact, _ = this_phone_calls.most_common(1)[0]
        assert top_contact == persistent_id, "top contact must be the persistent number"

    presences = n3.presences
    ring_phones = {p.phone_id for p in presences}
    assert len(ring_phones) == 4, "4 people in the night ring"

    by_day: dict[datetime.date, set[str]] = {}
    for p in presences:
        by_day.setdefault(p.ts.date(), set()).add(p.phone_id)
    gatherings = [phones for phones in by_day.values() if len(phones) == 4]
    assert len(gatherings) >= 10, ">= 10 co-presence events"

    night_count = sum(1 for p in presences if 0 <= p.ts.hour < 5)
    assert night_count / len(presences) >= 0.6, "night share >= 0.6"

    pairs_with_calls = {(c.calling_phone_id, c.called_phone_id) for c in n3.calls}
    for a in ring_phones:
        for b in ring_phones:
            if a != b:
                assert (a, b) not in pairs_with_calls, "zero direct calls between the ring's members"


# --- Background networks -----------------------------------------------------


def test_background_networks_count_kinds_and_ids():
    pop = _build_population()
    rng = random.Random(7)
    n = 12
    structures = inject_background_networks(
        pop, rng, n=n, threshold_inr=THRESHOLD_INR, start=START, end=END
    )

    assert len(structures) == n
    assert [s.structure_id for s in structures] == [f"BG_{i:03d}" for i in range(1, n + 1)]
    assert {s.kind for s in structures} == {"shell_chain", "mule_fanout", "burner_night"}
    assert all(s.role == "background" for s in structures)

    mule_sizes = {len(s.account_ids) for s in structures if s.kind == "mule_fanout"}
    assert len(mule_sizes) > 1, "background mule fan-outs must vary in size"

    burner_sizes = {sum(1 for _ in s.phone_ids) for s in structures if s.kind == "burner_night"}
    assert len(burner_sizes) >= 1  # not all necessarily distinct, but must exist and be non-trivial


def test_background_networks_regenerate_identically():
    pop = _build_population()
    a = inject_background_networks(
        pop, random.Random(7), n=6, threshold_inr=THRESHOLD_INR, start=START, end=END
    )
    b = inject_background_networks(
        pop, random.Random(7), n=6, threshold_inr=THRESHOLD_INR, start=START, end=END
    )
    assert a == b


# --- Determinism -------------------------------------------------------------


def test_demo_networks_deterministic_same_seed():
    pop = _build_population()
    a = inject_demo_networks(pop, random.Random(99), threshold_inr=THRESHOLD_INR, start=START, end=END)
    b = inject_demo_networks(pop, random.Random(99), threshold_inr=THRESHOLD_INR, start=START, end=END)
    assert a == b


def test_demo_networks_deterministic_across_pythonhashseed():
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    script = (
        f"import random, sys; sys.path.insert(0, {backend_dir!r}); "
        "from tests.unit.test_networks import _build_population, START, END, THRESHOLD_INR; "
        "from cid.pipeline.generate.networks import inject_demo_networks; "
        "pop = _build_population(); "
        "structs = inject_demo_networks(pop, random.Random(123), threshold_inr=THRESHOLD_INR, start=START, end=END); "
        "print(repr(structs))"
    )

    def run(hashseed: str) -> str:
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True
        )
        return result.stdout

    assert run("0") == run("1")


# --- Entity exclusivity across structures -----------------------------------


def test_no_entity_shared_across_demo_background_and_lookalikes():
    """N1-N3 are always held out at M9 (split by network, never by node); if
    a background network or look-alike reused one of their entities, part of
    the held-out test networks would leak into training."""
    pop = _build_population()
    rng = random.Random(11)
    claimed: set[str] = set()

    demo = inject_demo_networks(
        pop, rng, threshold_inr=THRESHOLD_INR, start=START, end=END, claimed=claimed
    )
    background = inject_background_networks(
        pop, rng, n=30, threshold_inr=THRESHOLD_INR, start=START, end=END, claimed=claimed
    )
    lookalikes = inject_lookalikes(
        pop, rng, threshold_inr=THRESHOLD_INR, start=START, end=END, claimed=claimed
    )

    seen: dict[str, str] = {}
    for structure in [*demo, *background, *lookalikes]:
        ids = (
            *structure.person_ids,
            *structure.account_ids,
            *structure.org_ids,
            *structure.phone_ids,
        )
        for entity_id in ids:
            assert entity_id not in seen, (
                f"{entity_id} appears in both {seen.get(entity_id)} and {structure.structure_id}"
            )
            seen[entity_id] = structure.structure_id
