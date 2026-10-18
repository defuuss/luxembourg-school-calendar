"""School-day calculations for both levels of Luxembourg education."""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


def relevant(events: list[dict], school_type: str) -> list[dict]:
    """Return scheduled closures that apply to one school level."""
    return [e for e in events if school_type == "fundamental" or not e.get("fundamental_only")]


def active(events: list[dict], today: date) -> dict | None:
    """Return a published closure covering this date, if any."""
    return next(
        (e for e in events if date.fromisoformat(e["start"]) <= today <= date.fromisoformat(e["end"])),
        None,
    )


def next_event(events: list[dict], today: date) -> dict | None:
    """Return the next published closure beginning after today."""
    return next((e for e in events if date.fromisoformat(e["start"]) > today), None)


def easter_sunday(year: int) -> date:
    """Calculate Gregorian Easter Sunday (Meeus/Jones/Butcher algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


@lru_cache(maxsize=64)
def public_holidays(year: int) -> frozenset[date]:
    """Luxembourg's 11 statutory holidays (not employer-specific makeup days)."""
    easter = easter_sunday(year)
    return frozenset({
        date(year, 1, 1),       # New Year
        easter + timedelta(days=1),   # Easter Monday
        date(year, 5, 1),       # Labour Day
        date(year, 5, 9),       # Europe Day
        easter + timedelta(days=39),  # Ascension
        easter + timedelta(days=50),  # Whit Monday
        date(year, 6, 23),      # National Day
        date(year, 8, 15),      # Assumption
        date(year, 11, 1),      # All Saints
        date(year, 12, 25),     # Christmas
        date(year, 12, 26),     # Saint Stephen
    })


def covered_range(events: list[dict]) -> tuple[date, date] | None:
    """Known school-year interval, with exclusive end.

    Do not invent the beginning of a school year that has not been published.
    The final summer holiday extends coverage only through its last date.
    """
    years = {e["school_year"] for e in events if isinstance(e.get("school_year"), int)}
    if not years:
        return None
    last_year = max(years)
    summers = [
        date.fromisoformat(e["end"]) for e in events
        if e.get("school_year") == last_year and e.get("kind") == "summer"
    ]
    if not summers:
        return None
    return date(min(years), 9, 15), max(summers) + timedelta(days=1)


def is_covered(events: list[dict], today: date) -> bool:
    """Whether the date lies within the published calendar coverage."""
    bounds = covered_range(events)
    if not bounds or not (bounds[0] <= today < bounds[1]):
        return False
    years = {e["school_year"] for e in events if isinstance(e.get("school_year"), int)}
    school_year = today.year if today >= date(today.year, 9, 15) else today.year - 1
    return school_year in years


def is_school_day(
    events: list[dict], today: date, school_type: str | None = None
) -> bool | None:
    """True only when school is open; None means future coverage unknown.

    This applies regardless of whether a public holiday was listed explicitly
    by a particular calendar source.
    """
    if active(events, today):
        return False
    if not is_covered(events, today):
        return None
    if today.weekday() >= 5 or today in public_holidays(today.year):
        return False
    if school_type == "fundamental" and today.month == 12 and today.day == 6:
        return False
    return True


def next_school_day(
    events: list[dict], today: date, school_type: str | None = None
) -> date | None:
    """First known school day strictly after today, not during a closure."""
    bounds = covered_range(events)
    if not bounds:
        return None
    candidate = max(today + timedelta(days=1), bounds[0])
    while candidate < bounds[1]:
        if is_school_day(events, candidate, school_type):
            return candidate
        candidate += timedelta(days=1)
    return None


def school_days_between(
    events: list[dict], start: date, end: date, school_type: str
) -> list[date]:
    """All known school days in the half-open interval [start, end)."""
    bounds = covered_range(events)
    if not bounds:
        return []
    first = max(start, bounds[0])
    last = min(end, bounds[1])
    days = []
    day = first
    while day < last:
        if is_school_day(events, day, school_type):
            days.append(day)
        day += timedelta(days=1)
    return days


def school_levels_for_entry(entry) -> tuple[str, str]:
    """Preserve stable existing entity unique IDs for each school level."""
    primary = entry.data.get("school_type", "fundamental")
    if primary not in ("fundamental", "secondary"):
        primary = "fundamental"
    other = "secondary" if primary == "fundamental" else "fundamental"
    return primary, other
