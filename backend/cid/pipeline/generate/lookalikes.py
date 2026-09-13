"""Plans the four look-alikes — lawful patterns that resemble a typology.

These exist to prove C.I.D. is honest about false positives (prd §7): each
one deliberately fails the numeric condition of the typology it resembles.
They stay `is_criminal=False` forever and must never be deleted or weakened
to make detection metrics look better (implementation.md risk table).

Same determinism discipline as `networks.py`: explicit `rng`, no `hash()`,
no wall-clock time, sets sorted before use. Also the same entity-exclusivity
discipline — look-alikes must not share an account, phone or person with a
network structure either, so this module reuses `networks.py`'s `claimed`
helpers rather than sampling the population directly.
"""

from __future__ import annotations

import datetime
import random

from cid.pipeline.generate.networks import (
    _business_name,
    _claim,
    _pick_people_with_phones,
    _sample,
    _unclaimed_accounts,
    _unclaimed_people,
)
from cid.pipeline.generate.specs import (
    Call,
    Company,
    InjectedStructure,
    Population,
    Presence,
    Transfer,
)

# --- Payroll fan-out — resembles T-02, fails on age and holding time -------


def _payroll_fanout(
    pop: Population,
    rng: random.Random,
    *,
    threshold_inr: int,
    start: datetime.date,
    end: datetime.date,
    claimed: set[str],
) -> InjectedStructure:
    """An employer paying ~15 staff. Unlike T-02's mules: staff accounts are
    old, nothing is forwarded on, and payments recur monthly in a steady
    amount — the opposite of a fresh mule forwarding within 48 h."""
    n_staff = 15
    pay_date = start + datetime.timedelta(days=rng.randint(400, max(401, (end - start).days - 90)))
    old_pool = [a for a in _unclaimed_accounts(pop, claimed) if (pay_date - a.opened).days > 400]
    employer, *staff = _sample(old_pool, rng, n_staff + 1)
    _claim(claimed, employer.account_id, employer.holder_person_id, *(a.account_id for a in staff))
    _claim(claimed, *(a.holder_person_id for a in staff))

    amount = threshold_inr + 10_000  # above the synthetic threshold — a real salary, not structuring.
    transfers = []
    for month in range(3):
        month_ts = datetime.datetime.combine(
            pay_date + datetime.timedelta(days=30 * month), datetime.time(9, 0)
        )
        for i, acct in enumerate(staff):
            transfers.append(
                Transfer(
                    txn_id=f"TXN_LA_PAYROLL_{month:02d}_{i:02d}",
                    from_account_id=employer.account_id,
                    to_account_id=acct.account_id,
                    amount_inr=amount,
                    ts=month_ts,
                    channel="NEFT",
                )
            )
    # No onward transfers: the whole point is money is not forwarded on.

    person_ids = tuple(sorted({employer.holder_person_id, *(a.holder_person_id for a in staff)}))
    account_ids = (employer.account_id, *(a.account_id for a in staff))

    return InjectedStructure(
        structure_id="LA_payroll",
        kind="payroll_fanout",
        typologies=(),
        role="lookalike",
        is_criminal=False,
        note=(
            "An employer paying long-established staff the same amount every "
            "month, with nothing forwarded on — ordinary payroll, not mule "
            "structuring."
        ),
        person_ids=person_ids,
        account_ids=account_ids,
        transfers=tuple(transfers),
    )


# --- Family sharing one phone -----------------------------------------------


def _family_phone(
    pop: Population, rng: random.Random, *, start: datetime.date, end: datetime.date, claimed: set[str]
) -> InjectedStructure:
    """Several household members co-present through one shared handset."""
    towers = sorted(pop.towers, key=lambda t: t.tower_id)
    home_tower = towers[rng.randrange(len(towers))].tower_id

    [(subscriber_id, phone_id)] = _pick_people_with_phones(pop, rng, 1, claimed)

    other_household = _sample(_unclaimed_people(pop, claimed), rng, 3)
    _claim(claimed, *other_household)
    household = tuple(sorted([subscriber_id, *other_household]))

    total_days = max((end - start).days, 20)
    presences = [
        Presence(
            phone_id=phone_id,
            tower_id=home_tower,
            ts=datetime.datetime.combine(
                start + datetime.timedelta(days=(k * total_days) // 20),
                datetime.time(rng.randint(6, 22), rng.randint(0, 59)),
            ),
        )
        for k in range(20)
    ]

    return InjectedStructure(
        structure_id="LA_family_phone",
        kind="family_phone",
        typologies=(),
        role="lookalike",
        is_criminal=False,
        note="One household's shared handset, so its subscriber and family are always co-present with it — not a burner ring.",
        person_ids=household,
        phone_ids=(phone_id,),
        presences=tuple(presences),
    )


# --- Daytime co-workers — resembles T-05, fails on night share -------------


def _daytime_coworkers(
    pop: Population, rng: random.Random, *, start: datetime.date, end: datetime.date, claimed: set[str]
) -> InjectedStructure:
    """5 people co-present at the same tower 10+ times, but during working
    hours, so night_share (00:00-05:00) is well below the 0.6 T-05 floor."""
    towers = sorted(pop.towers, key=lambda t: t.tower_id)
    tower_id = towers[rng.randrange(len(towers))].tower_id

    pairs = _pick_people_with_phones(pop, rng, 5, claimed)
    people = [person_id for person_id, _ in pairs]
    phones = [phone_id for _, phone_id in pairs]

    total_days = max((end - start).days, 15)
    presences = []
    calls = []
    for k in range(12):
        day = start + datetime.timedelta(days=(k * total_days) // 12)
        base_ts = datetime.datetime.combine(day, datetime.time(rng.randint(10, 16), rng.randint(0, 59)))
        for phone_id in phones:
            presences.append(
                Presence(
                    phone_id=phone_id,
                    tower_id=tower_id,
                    ts=base_ts + datetime.timedelta(minutes=rng.randint(0, 15)),
                )
            )
    # Coworkers also just call each other, unlike a night ring's zero calls.
    for i in range(len(phones) - 1):
        calls.append(
            Call(
                calling_phone_id=phones[i],
                called_phone_id=phones[i + 1],
                ts=datetime.datetime.combine(start + datetime.timedelta(days=5), datetime.time(13, 0)),
                duration_s=90,
                tower_id=tower_id,
            )
        )

    return InjectedStructure(
        structure_id="LA_daytime_coworkers",
        kind="daytime_coworkers",
        typologies=(),
        role="lookalike",
        is_criminal=False,
        note="Five coworkers at the same office tower during working hours, not a night ring — night share is near zero, and they call each other.",
        person_ids=tuple(sorted(people)),
        phone_ids=tuple(phones),
        presences=tuple(presences),
        calls=tuple(calls),
    )


# --- Legitimate holding company — resembles T-01, fails on age/pass-through -


def _holding_company(
    pop: Population, rng: random.Random, *, start: datetime.date, end: datetime.date, claimed: set[str]
) -> InjectedStructure:
    """A real group structure: a subsidiary incorporated years before an
    intercompany transfer, which retains most of the funds."""
    parent_acct, sub_acct = _sample(_unclaimed_accounts(pop, claimed), rng, 2)
    _claim(
        claimed,
        parent_acct.account_id,
        parent_acct.holder_person_id,
        sub_acct.account_id,
        sub_acct.holder_person_id,
    )

    transfer_ts = datetime.datetime.combine(
        start + datetime.timedelta(days=rng.randint(400, max(401, (end - start).days - 90))),
        datetime.time(14, 0),
    )
    company = Company(
        org_id="ORG_990101",
        reg_no="REG990101",
        name=_business_name(rng),
        incorporated=transfer_ts.date() - datetime.timedelta(days=365 * 6),  # years, not weeks.
        address_key="ADDR_LA_HOLDING",
        director_person_ids=(parent_acct.holder_person_id, sub_acct.holder_person_id),
    )
    _claim(claimed, company.org_id)

    amount_in = 1_000_000
    amount_out = 300_000  # retains 70% — pass-through well under the 0.9 T-01 floor.
    transfers = (
        Transfer(
            txn_id="TXN_LA_HOLDING_IN",
            from_account_id=parent_acct.account_id,
            to_account_id=sub_acct.account_id,
            amount_inr=amount_in,
            ts=transfer_ts,
            channel="RTGS",
        ),
        Transfer(
            txn_id="TXN_LA_HOLDING_OUT",
            from_account_id=sub_acct.account_id,
            to_account_id=parent_acct.account_id,
            amount_inr=amount_out,
            ts=transfer_ts + datetime.timedelta(days=10),
            channel="RTGS",
        ),
    )

    return InjectedStructure(
        structure_id="LA_holding_company",
        kind="holding_company",
        typologies=(),
        role="lookalike",
        is_criminal=False,
        note="An intercompany transfer inside a group incorporated years earlier that keeps most of the funds — not a shell-chain layering scheme.",
        person_ids=tuple(sorted({parent_acct.holder_person_id, sub_acct.holder_person_id})),
        account_ids=(parent_acct.account_id, sub_acct.account_id),
        org_ids=(company.org_id,),
        companies=(company,),
        transfers=transfers,
    )


def inject_lookalikes(
    pop: Population,
    rng: random.Random,
    *,
    threshold_inr: int,
    start: datetime.date,
    end: datetime.date,
    claimed: set[str] | None = None,
) -> list[InjectedStructure]:
    """The four look-alikes (prd §7): honest false positives that must
    never be deleted or weakened to make metrics look better.

    `claimed` should be the same set already threaded through
    `networks.inject_demo_networks` / `inject_background_networks`, so a
    look-alike never shares an entity with a criminal network either.
    """
    claimed = set() if claimed is None else claimed
    return [
        _payroll_fanout(pop, rng, threshold_inr=threshold_inr, start=start, end=end, claimed=claimed),
        _family_phone(pop, rng, start=start, end=end, claimed=claimed),
        _daytime_coworkers(pop, rng, start=start, end=end, claimed=claimed),
        _holding_company(pop, rng, start=start, end=end, claimed=claimed),
    ]
