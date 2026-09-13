"""Shared contracts for world generation.

`world.py` builds the population and renders source records; `networks.py` and
`lookalikes.py` plan structures over an already-built population. Both sides
depend on this module and not on each other, which keeps the imports acyclic.

Everything here is plain data. No randomness, no I/O.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

from cid.pipeline.generate.names import TruePerson

# Entity id formats are architecture.md §5.3.
PERSON_ID = "PERSON_{:06d}"
ORG_ID = "ORG_{:06d}"
ACCOUNT_ID = "ACC_{:06d}"
PHONE_ID = "PHN_{:06d}"
VEHICLE_ID = "VEH_{:06d}"
LOCATION_ID = "LOC_{:06d}"
EVENT_ID = "EVT_{:06d}"
DEVICE_ID = "DEV_{:06d}"


@dataclass(frozen=True)
class Account:
    """A bank account. Exactly one of holder_person_id / holder_org_id is set.

    Organisations hold accounts directly (P-02 allows `Organization` as an
    `OWNS` source for accounts), which is what T-01 needs: its query walks
    transfer chains through accounts *owned by organisations* incorporated
    shortly before the money moved.
    """

    account_id: str
    account_no: str  # synthetic, appears in records
    opened: datetime.date
    bank: str
    kyc_status: str
    holder_person_id: str | None = None
    holder_org_id: str | None = None

    def __post_init__(self) -> None:
        if (self.holder_person_id is None) == (self.holder_org_id is None):
            raise ValueError(
                f"{self.account_id}: set exactly one of holder_person_id / holder_org_id"
            )


@dataclass(frozen=True)
class Phone:
    phone_id: str
    msisdn: str  # synthetic 10-digit
    subscriber_person_id: str
    activated: datetime.date
    deactivated: datetime.date | None
    imsi: str
    seller: str  # activation batches share a seller (T-04 burner signal)


@dataclass(frozen=True)
class Company:
    org_id: str
    reg_no: str
    name: str
    incorporated: datetime.date
    address_key: str
    director_person_ids: tuple[str, ...]


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    registration: str
    owner_person_id: str


@dataclass(frozen=True)
class Tower:
    tower_id: str
    name: str
    lat: float
    lon: float
    footprint_m: int


@dataclass(frozen=True)
class Transfer:
    txn_id: str
    from_account_id: str
    to_account_id: str
    amount_inr: int
    ts: datetime.datetime
    channel: str


@dataclass(frozen=True)
class Call:
    calling_phone_id: str
    called_phone_id: str
    ts: datetime.datetime
    duration_s: int
    tower_id: str


@dataclass(frozen=True)
class Presence:
    """A phone seen in a tower footprint. Towers are areas, never points —
    prd §5.3 rule 6 and master D-20. Never call this a location fix."""

    phone_id: str
    tower_id: str
    ts: datetime.datetime


@dataclass(frozen=True)
class Population:
    """Everything that exists in the district before any network is injected."""

    people: tuple[TruePerson, ...]
    accounts: tuple[Account, ...]
    phones: tuple[Phone, ...]
    companies: tuple[Company, ...]
    vehicles: tuple[Vehicle, ...]
    towers: tuple[Tower, ...]

    def accounts_of(self, person_id: str) -> tuple[Account, ...]:
        return tuple(a for a in self.accounts if a.holder_person_id == person_id)

    def phones_of(self, person_id: str) -> tuple[Phone, ...]:
        return tuple(p for p in self.phones if p.subscriber_person_id == person_id)


@dataclass(frozen=True)
class InjectedStructure:
    """A planned structure over the population, plus the ground truth about it.

    Used for both criminal networks and look-alikes. `is_criminal` is what
    separates them: look-alikes are lawful patterns that resemble a typology,
    and they are the honesty test — they must stay in the world and must not be
    deleted to make metrics look better (implementation.md risk table).
    """

    structure_id: str  # "N1", "BG_007", "LA_payroll"
    kind: str  # 'shell_chain' | 'mule_fanout' | 'burner_night' | look-alike kinds
    typologies: tuple[str, ...]  # ("T-01", "T-08"); empty for look-alikes
    role: str  # 'demo' | 'background' | 'lookalike'
    is_criminal: bool
    note: str  # one plain sentence; for look-alikes, why it is lawful

    person_ids: tuple[str, ...] = ()
    account_ids: tuple[str, ...] = ()
    org_ids: tuple[str, ...] = ()
    phone_ids: tuple[str, ...] = ()

    transfers: tuple[Transfer, ...] = ()
    calls: tuple[Call, ...] = ()
    presences: tuple[Presence, ...] = ()

    # Companies incorporated specifically for this structure (shell chains).
    companies: tuple[Company, ...] = ()


@dataclass(frozen=True)
class GoldMention:
    """One place a source record names a person, and who it really is.

    This is the ground truth M4's entity resolution is scored against: the
    surface is what the record says, `person_id` is who it actually was.
    """

    source_record_id: str
    field: str  # which field of the record carried the name
    surface: str  # as written, may be any script
    script: str
    person_id: str


@dataclass
class WorldOutput:
    """Everything one generation run produces, before it is written to disk."""

    population: Population
    structures: list[InjectedStructure] = field(default_factory=list)
    mentions: list[GoldMention] = field(default_factory=list)
