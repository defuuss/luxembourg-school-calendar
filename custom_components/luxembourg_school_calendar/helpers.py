"""Pure date calculations shared by the calendar and sensors."""
from datetime import date, timedelta


def relevant(events: list[dict], school_type: str) -> list[dict]:
    return [e for e in events if school_type == "fundamental" or not e.get("fundamental_only")]


def active(events: list[dict], today: date) -> dict | None:
    return next(
        (e for e in events if date.fromisoformat(e["start"]) <= today <= date.fromisoformat(e["end"])),
        None,
    )


def next_event(events: list[dict], today: date) -> dict | None:
    return next((e for e in events if date.fromisoformat(e["start"]) > today), None)


def is_covered(events: list[dict], today: date) -> bool:
    """Whether the published school years cover today's possible school days."""
    years = [e.get("school_year") for e in events if isinstance(e.get("school_year"), int)]
    return bool(
        years and date(min(years), 9, 15) <= today < date(max(years) + 1, 9, 15)
    )


def is_school_day(events: list[dict], today: date) -> bool | None:
    """Return None when school-day status is unknown beyond published years."""
    if active(events, today):
        return False
    if not is_covered(events, today):
        return None
    return today.weekday() < 5


def next_school_day(events: list[dict], today: date) -> date | None:
    """Find the next known school day after today, skipping weekends and holidays.

    Only look inside published school year coverage, never guessing new years.
    The caller supplies events for one particular school level.
    """
    years = [e["school_year"] for e in events if isinstance(e.get("school_year"), int)]
    if not years:
        return None
    first_covered = date(min(years), 9, 15)
    end_exclusive = date(max(years) + 1, 9, 15)
    candidate = today + timedelta(days=1)
    if candidate < first_covered:
        return None
    while candidate < end_exclusive:
        if is_school_day(events, candidate):
            return candidate
        candidate += timedelta(days=1)
    return None


def school_levels_for_entry(entry) -> tuple[str, str]:
    """Create both levels with stable IDs anchored to original config.

    Older versions allowed changing school_type in options, which could silently
    transfer the legacy calendar's unique ID to the *other* school level.
    The original school_type stored in entry.data must remain authoritative for
    legacy entity naming. New installations default to fundamental.
    """
    primary = entry.data.get("school_type", "fundamental")
    if primary not in ("fundamental", "secondary"):
        primary = "fundamental"
    other = "secondary" if primary == "fundamental" else "fundamental"
    return primary, other
