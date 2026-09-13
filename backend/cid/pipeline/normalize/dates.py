"""Date/time normalisation (architecture §6.2): everything → UTC, `source_tz` kept alongside.

`source_tz` is not folded into the UTC instant here — the caller stores it
next to `to_utc`'s result so downstream typologies (e.g. T-05's night-ring
detector, which keys off local hour-of-day) can recover the original wall
clock time from the UTC instant plus the zone.
"""

from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo


def to_utc(value: datetime.date | datetime.datetime | str, source_tz: str) -> datetime.datetime:
    """Parse `value` and return an aware UTC datetime.

    - A naive `datetime`/ISO string is assumed to be local wall-clock time
      in `source_tz` (e.g. `Asia/Kolkata`, UTC+05:30 — no DST) and is
      localised before converting.
    - An already-aware `datetime`/ISO string is converted as-is; its own
      offset wins over `source_tz`.
    - A bare `date` has no time-of-day to localise: midnight in `source_tz`
      is used as the instant.
    """
    if isinstance(value, str):
        parsed: datetime.date | datetime.datetime = datetime.datetime.fromisoformat(value)
    else:
        parsed = value

    if isinstance(parsed, datetime.datetime):
        dt = parsed
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(source_tz))
    else:
        dt = datetime.datetime.combine(parsed, datetime.time.min, tzinfo=ZoneInfo(source_tz))

    return dt.astimezone(datetime.UTC)
