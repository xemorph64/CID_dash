import random

from cid.pipeline.generate.lookalikes import inject_lookalikes
from tests.unit.test_networks import END, START, THRESHOLD_INR, _build_population


def _lookalikes(seed: int = 5):
    pop = _build_population()
    rng = random.Random(seed)
    structures = inject_lookalikes(pop, rng, threshold_inr=THRESHOLD_INR, start=START, end=END)
    return pop, {s.kind: s for s in structures}


def test_returns_four_lookalikes_all_lawful():
    _, by_kind = _lookalikes()
    assert len(by_kind) == 4
    for s in by_kind.values():
        assert s.is_criminal is False
        assert s.role == "lookalike"
        assert s.typologies == ()
        assert s.note  # one plain sentence explaining why it's lawful


def test_payroll_fanout_fails_t02():
    pop, by_kind = _lookalikes()
    payroll = by_kind["payroll_fanout"]
    acct_by_id = {a.account_id: a for a in pop.accounts}

    froms = {}
    for t in payroll.transfers:
        froms.setdefault(t.from_account_id, []).append(t)
    _employer_id, employer_transfers = max(froms.items(), key=lambda kv: len(kv[1]))
    assert len(employer_transfers) >= 15 * 3  # 15 staff, 3 monthly payments each

    staff_ids = {t.to_account_id for t in employer_transfers}
    assert len(staff_ids) >= 15

    # Fails T-02's "opened < 60 days before receipt": staff accounts are old.
    for t in employer_transfers:
        staff = acct_by_id[t.to_account_id]
        gap_days = (t.ts.date() - staff.opened).days
        assert gap_days >= 60

    # Fails T-02's "<48h holding time": nothing is ever forwarded on.
    for staff_id in staff_ids:
        assert not any(t.from_account_id == staff_id for t in payroll.transfers)

    # Payments recur monthly in a steady amount.
    amounts = {t.amount_inr for t in employer_transfers}
    assert len(amounts) == 1


def test_daytime_coworkers_fails_t05():
    _, by_kind = _lookalikes()
    coworkers = by_kind["daytime_coworkers"]

    presences = coworkers.presences
    assert len(presences) > 0
    night_count = sum(1 for p in presences if 0 <= p.ts.hour < 5)
    night_share = night_count / len(presences)
    assert night_share < 0.6, "daytime co-presence must not read as a night ring"

    by_day = {}
    for p in presences:
        by_day.setdefault(p.ts.date(), set()).add(p.phone_id)
    gatherings = [g for g in by_day.values() if len(g) == 5]
    assert len(gatherings) >= 10, "same co-presence frequency as a real night ring, just not at night"

    # Unlike a night ring, coworkers do call each other.
    assert len(coworkers.calls) > 0


def test_holding_company_fails_t01():
    _, by_kind = _lookalikes()
    holding = by_kind["holding_company"]

    assert len(holding.companies) == 1
    company = holding.companies[0]
    inbound = next(t for t in holding.transfers if t.to_account_id in holding.account_ids)
    outbound = next(t for t in holding.transfers if t.from_account_id == inbound.to_account_id)

    gap_days = (inbound.ts.date() - company.incorporated).days
    assert gap_days >= 90, "incorporated years before the transfer, not weeks"

    ratio = outbound.amount_inr / inbound.amount_inr
    assert ratio < 0.9, "retains most of the funds — pass-through well under the T-01 floor"


def test_family_phone_is_one_shared_handset():
    _, by_kind = _lookalikes()
    family = by_kind["family_phone"]
    assert len(family.phone_ids) == 1
    assert len(family.person_ids) >= 4
    assert all(p.phone_id == family.phone_ids[0] for p in family.presences)
