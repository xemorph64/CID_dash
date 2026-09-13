"""Plans criminal network structures over an already-built population.

`world.py` builds the `Population`; this module only *plans* structures over
it and returns `InjectedStructure` objects (events + ground truth) — see
`specs.py`'s module docstring. The numbers here are not decorative: M9's
typology queries (architecture.md §6.9) are numeric thresholds, so every
structure is built to satisfy them exactly, never approximately (CLAUDE.md
rule 10: tune the data, never the rules).

Determinism discipline (M1 hard acceptance criterion): every function here
takes an explicit `rng: random.Random`, never touches the builtin `random`
module, never calls `hash()`, `datetime.now()` or `uuid4()`, and never
iterates a `set` without sorting it first.

Entity exclusivity: M9 splits by network, never by node, and N1-N3 are
always held out (prd §7 / architecture §6.8). If a background network
shared an account, phone, company or person with N1-N3, part of the test
network would leak into training. Every function here therefore takes a
`claimed: set[str]` of entity ids already used by an earlier structure,
filters it out of every pool it samples from, and updates it with whatever
it picks — callers thread the same set through every `inject_*` call.
"""

from __future__ import annotations

import datetime
import random

from cid.pipeline.generate.specs import (
    Account,
    Call,
    Company,
    InjectedStructure,
    Phone,
    Population,
    Presence,
    Transfer,
)

# --- Small deterministic helpers --------------------------------------------


def _sample(pool: list, rng: random.Random, k: int) -> list:
    """Pick `k` distinct items from `pool`, order preserved, choice via rng."""
    if len(pool) < k:
        raise ValueError(f"pool has only {len(pool)} unclaimed candidates, need {k}")
    idx = sorted(rng.sample(range(len(pool)), k))
    return [pool[i] for i in idx]


def _claim(claimed: set[str], *ids: str) -> None:
    claimed.update(ids)


def _unclaimed_accounts(pop: Population, claimed: set[str]) -> list[Account]:
    """Person-held accounts not yet used by another structure. Chain/mule
    accounts in this module are always person-held picks from the
    population; org-held accounts are freshly minted (`shell_org_account`)
    and never drawn from this pool."""
    return sorted(
        (
            a
            for a in pop.accounts
            if a.holder_person_id is not None
            and a.account_id not in claimed
            and a.holder_person_id not in claimed
        ),
        key=lambda a: a.account_id,
    )


def _unclaimed_people(pop: Population, claimed: set[str]) -> list[str]:
    return sorted(p.person_id for p in pop.people if p.person_id not in claimed)


def _pick_people_with_phones(
    pop: Population, rng: random.Random, n: int, claimed: set[str]
) -> list[tuple[str, str]]:
    """`n` distinct (person_id, phone_id) pairs, each still unclaimed."""
    candidates = []
    for p in sorted(pop.people, key=lambda x: x.person_id):
        if p.person_id in claimed:
            continue
        phone = next((ph for ph in pop.phones_of(p.person_id) if ph.phone_id not in claimed), None)
        if phone is not None:
            candidates.append((p.person_id, phone.phone_id))
    chosen = _sample(candidates, rng, n)
    for person_id, phone_id in chosen:
        _claim(claimed, person_id, phone_id)
    return chosen


# --- N1 / background — shell chain around a central person (T-01, T-08) ----


def shell_org_account(company: Company) -> Account:
    """The bank account a shell company holds directly (`holder_org_id`).

    `InjectedStructure` has no separate slot for freshly minted accounts (it
    only carries new `Company` objects), so this stays a pure function of
    the company: `_shell_chain` uses it to build the chain's transfers, and
    tests call the same function to verify org ownership directly.
    """
    return Account(
        account_id=f"ACC_ORGHOLD_{company.org_id}",
        account_no=f"ORGACC{company.org_id}",
        opened=company.incorporated,
        bank="Demo Bank",
        kyc_status="verified",
        holder_org_id=company.org_id,
    )


def _shell_chain(
    pop: Population,
    rng: random.Random,
    *,
    structure_id: str,
    org_id_start: int,
    start: datetime.date,
    end: datetime.date,
    role: str,
    claimed: set[str],
    hops: int = 2,
) -> InjectedStructure:
    """A chain source -> hop_1 -> ... -> hop_k -> dest.

    Each hop account is held directly by a freshly incorporated shell
    company (`holder_org_id`, via `shell_org_account`); Person A (the source
    account's holder) directs every one of those companies, so the companies
    always share a director (Person A), and they also share a registered
    address. Each hop keeps under 10% (pass-through ratio > 0.9).
    """
    source, dest = _sample(_unclaimed_accounts(pop, claimed), rng, 2)
    _claim(claimed, source.account_id, source.holder_person_id, dest.account_id, dest.holder_person_id)
    person_a = source.holder_person_id

    co_directors = _sample(_unclaimed_people(pop, claimed), rng, hops)
    _claim(claimed, *co_directors)

    ts = datetime.datetime.combine(
        start + datetime.timedelta(days=rng.randint(5, max(6, (end - start).days - 30))),
        datetime.time(10, 0),
    )

    transfers: list[Transfer] = []
    companies: list[Company] = []
    hop_account_ids: list[str] = []
    amount = 1_000_000
    prev_account_id = source.account_id
    incoming_ts = ts
    for i, co_director in enumerate(co_directors):
        org_id = f"ORG_{org_id_start + i:06d}"
        incorporated = incoming_ts.date() - datetime.timedelta(days=rng.randint(20, 80))
        company = Company(
            org_id=org_id,
            reg_no=f"REG{org_id_start + i:06d}",
            name=f"{structure_id} Shell {i + 1} Pvt Ltd",
            incorporated=incorporated,
            address_key=f"ADDR_{structure_id}_SHELL",
            director_person_ids=(person_a, co_director),
        )
        hop_account = shell_org_account(company)
        companies.append(company)
        hop_account_ids.append(hop_account.account_id)
        transfers.append(
            Transfer(
                txn_id=f"TXN_{structure_id}_{i:02d}",
                from_account_id=prev_account_id,
                to_account_id=hop_account.account_id,
                amount_inr=amount,
                ts=incoming_ts,
                channel="NEFT",
            )
        )
        ratio = rng.uniform(0.91, 0.97)  # keeps <10%, i.e. pass-through > 0.9.
        amount = round(amount * ratio)
        prev_account_id = hop_account.account_id
        incoming_ts = incoming_ts + datetime.timedelta(
            days=rng.randint(2, 8), hours=rng.randint(0, 12)
        )

    transfers.append(
        Transfer(
            txn_id=f"TXN_{structure_id}_{hops:02d}",
            from_account_id=prev_account_id,
            to_account_id=dest.account_id,
            amount_inr=amount,
            ts=incoming_ts,
            channel="NEFT",
        )
    )

    _claim(claimed, *(c.org_id for c in companies), *hop_account_ids)

    person_ids = tuple(sorted({person_a, dest.holder_person_id, *co_directors}))
    account_ids = (source.account_id, *hop_account_ids, dest.account_id)
    org_ids = tuple(c.org_id for c in companies)

    return InjectedStructure(
        structure_id=structure_id,
        kind="shell_chain",
        typologies=("T-01", "T-08"),
        role=role,
        is_criminal=True,
        note=(
            "Person A directs a chain of freshly incorporated shell companies "
            "that hold the layering accounts directly, keeping under 10% at "
            "each hop."
        ),
        person_ids=person_ids,
        account_ids=account_ids,
        org_ids=org_ids,
        transfers=tuple(transfers),
        companies=tuple(companies),
    )


# --- N2 / background — mule fan-out (T-02, T-03) ---------------------------


def _mule_fanout(
    pop: Population,
    rng: random.Random,
    *,
    structure_id: str,
    start: datetime.date,
    end: datetime.date,
    role: str,
    threshold_inr: int,
    claimed: set[str],
    n_mules: int = 12,
) -> InjectedStructure:
    """One hub account fans sub-threshold payments to `n_mules` freshly
    opened accounts, each of which forwards the money on within hours.

    All receipts land inside one ~60 h window (comfortably under the T-03
    72 h window); every mule was opened 15-55 days before it (under T-02's
    60-day bound); every forward happens 6-36 h later (T-02's <48 h median).
    """
    total_days = (end - start).days
    if total_days < 70:
        raise ValueError("mule fanout needs a start/end span of at least 70 days")
    center_date = start + datetime.timedelta(days=rng.randint(65, total_days - 3))
    center_ts = datetime.datetime.combine(center_date, datetime.time(11, 0))

    open_lo = center_date - datetime.timedelta(days=55)
    open_hi = center_date - datetime.timedelta(days=15)
    open_pool = [a for a in _unclaimed_accounts(pop, claimed) if open_lo <= a.opened <= open_hi]
    if len(open_pool) < n_mules:
        raise ValueError(
            f"population has only {len(open_pool)} unclaimed accounts opened "
            f"between {open_lo} and {open_hi}, need {n_mules} for a mule fan-out"
        )
    mules = _sample(open_pool, rng, n_mules)
    _claim(claimed, *(a.account_id for a in mules), *(a.holder_person_id for a in mules))

    other_pool = _unclaimed_accounts(pop, claimed)
    hub, sink = _sample(other_pool, rng, 2)
    _claim(claimed, hub.account_id, hub.holder_person_id, sink.account_id, sink.holder_person_id)

    receive: list[Transfer] = []
    forward: list[Transfer] = []
    for i, mule in enumerate(mules):
        receipt_ts = center_ts + datetime.timedelta(hours=5 * i)
        amount = rng.randint(int(threshold_inr * 0.4), threshold_inr - 1)
        receive.append(
            Transfer(
                txn_id=f"TXN_{structure_id}_H{i:02d}",
                from_account_id=hub.account_id,
                to_account_id=mule.account_id,
                amount_inr=amount,
                ts=receipt_ts,
                channel="IMPS",
            )
        )
        forward_ts = receipt_ts + datetime.timedelta(hours=rng.uniform(6, 36))
        forward.append(
            Transfer(
                txn_id=f"TXN_{structure_id}_F{i:02d}",
                from_account_id=mule.account_id,
                to_account_id=sink.account_id,
                amount_inr=amount,
                ts=forward_ts,
                channel="IMPS",
            )
        )

    person_ids = tuple(
        sorted({hub.holder_person_id, sink.holder_person_id, *(m.holder_person_id for m in mules)})
    )
    account_ids = (hub.account_id, sink.account_id, *(m.account_id for m in mules))

    return InjectedStructure(
        structure_id=structure_id,
        kind="mule_fanout",
        typologies=("T-02", "T-03"),
        role=role,
        is_criminal=True,
        note=(
            "One hub account fans sub-threshold payments out to freshly "
            "opened mule accounts that forward the money on within hours."
        ),
        person_ids=person_ids,
        account_ids=account_ids,
        transfers=(*receive, *forward),
    )


# --- N3 / background — burner tree + night ring (T-04, T-05) ---------------


def _phone_batches(pop: Population) -> dict[tuple[datetime.date, str], list[str]]:
    """Group phone ids by (activation date, seller) — the T-04 batch signal
    (specs.py's `Phone.seller` docstring). Grouping key order is comparison-
    based, never `hash()`-based, so it stays stable across processes."""
    groups: dict[tuple[datetime.date, str], list[str]] = {}
    for p in pop.phones:
        groups.setdefault((p.activated, p.seller), []).append(p.phone_id)
    return {k: sorted(v) for k, v in sorted(groups.items())}


def _active_days(phone: Phone, end: datetime.date) -> int:
    last = phone.deactivated or end
    return (last - phone.activated).days


def _select_burner_batch(
    pop: Population, rng: random.Random, n_needed: int, end: datetime.date, claimed: set[str]
) -> list[str]:
    by_id = {p.phone_id: p for p in pop.phones}
    candidates = []
    for ids in _phone_batches(pop).values():
        qualifying = sorted(
            pid
            for pid in ids
            if pid not in claimed
            and by_id[pid].subscriber_person_id not in claimed
            and _active_days(by_id[pid], end) < 45
        )
        if len(qualifying) >= n_needed:
            candidates.append(qualifying)
    if not candidates:
        raise ValueError(
            f"population has no unclaimed batch of >= {n_needed} phones sharing "
            "an activation day and seller, all active < 45 days"
        )
    qualifying = candidates[rng.randrange(len(candidates))]
    chosen = _sample(qualifying, rng, n_needed)
    _claim(claimed, *chosen, *(by_id[pid].subscriber_person_id for pid in chosen))
    return chosen


def _pick_persistent(pop: Population, rng: random.Random, claimed: set[str], exclude: set[str]) -> str:
    by_id = {p.phone_id: p for p in pop.phones}
    pool = sorted(
        p.phone_id
        for p in pop.phones
        if p.phone_id not in exclude
        and p.phone_id not in claimed
        and p.subscriber_person_id not in claimed
    )
    chosen = pool[rng.randrange(len(pool))]
    _claim(claimed, chosen, by_id[chosen].subscriber_person_id)
    return chosen


def _burner_night(
    pop: Population,
    rng: random.Random,
    *,
    structure_id: str,
    start: datetime.date,
    end: datetime.date,
    role: str,
    claimed: set[str],
    n_burners: int = 8,
    n_night: int = 4,
    n_presence: int = 10,
) -> InjectedStructure:
    """A batch of burner phones all calling one persistent number, plus a
    separate ring of `n_night` people co-present at ~2 a.m. with zero calls
    between them."""
    by_id = {p.phone_id: p for p in pop.phones}
    burner_ids = _select_burner_batch(pop, rng, n_burners, end, claimed)
    persistent_id = _pick_persistent(pop, rng, claimed, exclude=set(burner_ids))

    towers = sorted(pop.towers, key=lambda t: t.tower_id)
    tower_id = towers[rng.randrange(len(towers))].tower_id

    calls: list[Call] = []
    for phone_id in burner_ids:
        phone = by_id[phone_id]
        span_days = max(1, _active_days(phone, end))
        for _ in range(6):
            day_offset = rng.randint(0, span_days - 1) if span_days > 1 else 0
            call_ts = datetime.datetime.combine(
                phone.activated + datetime.timedelta(days=day_offset),
                datetime.time(rng.randint(0, 23), rng.randint(0, 59)),
            )
            calls.append(
                Call(
                    calling_phone_id=phone_id,
                    called_phone_id=persistent_id,
                    ts=call_ts,
                    duration_s=rng.randint(20, 240),
                    tower_id=tower_id,
                )
            )

    night_pairs = _pick_people_with_phones(pop, rng, n_night, claimed)
    night_people = [person_id for person_id, _ in night_pairs]
    night_phones = [phone_id for _, phone_id in night_pairs]

    presences: list[Presence] = []
    total_days = max((end - start).days, n_presence)
    for k in range(n_presence):
        day = start + datetime.timedelta(days=(k * total_days) // n_presence)
        base_ts = datetime.datetime.combine(day, datetime.time(2, 0))
        for phone_id in night_phones:
            presences.append(
                Presence(
                    phone_id=phone_id,
                    tower_id=tower_id,
                    ts=base_ts + datetime.timedelta(minutes=rng.randint(0, 20)),
                )
            )

    burner_person_ids = {by_id[pid].subscriber_person_id for pid in [*burner_ids, persistent_id]}
    person_ids = tuple(sorted(burner_person_ids | set(night_people)))

    return InjectedStructure(
        structure_id=structure_id,
        kind="burner_night",
        typologies=("T-04", "T-05"),
        role=role,
        is_criminal=True,
        note=(
            "A batch of burner phones all call one persistent number, and a "
            "separate group shares a tower at night with zero calls between "
            "them."
        ),
        person_ids=person_ids,
        phone_ids=(*burner_ids, persistent_id, *night_phones),
        calls=tuple(calls),
        presences=tuple(presences),
    )


# --- Public entry points -----------------------------------------------------


def inject_demo_networks(
    pop: Population,
    rng: random.Random,
    *,
    threshold_inr: int,
    start: datetime.date,
    end: datetime.date,
    claimed: set[str] | None = None,
) -> list[InjectedStructure]:
    """N1 (shell chain), N2 (mule fan-out), N3 (burner tree + night ring) —
    prd §7. These three are always in the test split, never trained on.

    `claimed` is mutated in place; pass the same set into
    `inject_background_networks` and `lookalikes.inject_lookalikes` so no
    entity is shared across structures (demo claims first).
    """
    claimed = set() if claimed is None else claimed
    n1 = _shell_chain(
        pop,
        rng,
        structure_id="N1",
        org_id_start=990001,
        start=start,
        end=end,
        role="demo",
        claimed=claimed,
        hops=2,
    )
    n2 = _mule_fanout(
        pop,
        rng,
        structure_id="N2",
        start=start,
        end=end,
        role="demo",
        threshold_inr=threshold_inr,
        claimed=claimed,
        n_mules=12,
    )
    n3 = _burner_night(
        pop,
        rng,
        structure_id="N3",
        start=start,
        end=end,
        role="demo",
        claimed=claimed,
        n_burners=8,
        n_night=4,
        n_presence=10,
    )
    return [n1, n2, n3]


def inject_background_networks(
    pop: Population,
    rng: random.Random,
    *,
    n: int,
    threshold_inr: int,
    start: datetime.date,
    end: datetime.date,
    claimed: set[str] | None = None,
) -> list[InjectedStructure]:
    """`n` more networks of the same three kinds, varied sizes and timings —
    what the model actually trains on, since N1-N3 are held out (prd §7)."""
    claimed = set() if claimed is None else claimed
    out: list[InjectedStructure] = []
    for i in range(1, n + 1):
        structure_id = f"BG_{i:03d}"
        kind = i % 3
        if kind == 1:
            out.append(
                _shell_chain(
                    pop,
                    rng,
                    structure_id=structure_id,
                    org_id_start=890000 + i * 10,
                    start=start,
                    end=end,
                    role="background",
                    claimed=claimed,
                    hops=rng.randint(2, 4),
                )
            )
        elif kind == 2:
            out.append(
                _mule_fanout(
                    pop,
                    rng,
                    structure_id=structure_id,
                    start=start,
                    end=end,
                    role="background",
                    threshold_inr=threshold_inr,
                    claimed=claimed,
                    n_mules=rng.randint(8, 20),
                )
            )
        else:
            out.append(
                _burner_night(
                    pop,
                    rng,
                    structure_id=structure_id,
                    start=start,
                    end=end,
                    role="background",
                    claimed=claimed,
                    n_burners=rng.randint(5, 8),
                    n_night=4,
                    n_presence=rng.randint(10, 20),
                )
            )
    return out
