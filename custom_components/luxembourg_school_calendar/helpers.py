"""Pure date calculations shared by the calendar and sensors."""
from datetime import date


def relevant(events: list[dict], school_type: str) -> list[dict]:
    return [e for e in events if school_type == "fundamental" or not e.get("fundamental_only")]


def active(events: list[dict], today: date) -> dict | None:
    return next(
        (e for e in events if date.fromisoformat(e["start"]) <= today <= date.fromisoformat(e["end"])),
        None,
    )


def next_event(events: list[dict], today: date) -> dict | None:
    return next((e for e in events if date.fromisoformat(e["start"]) > today), None)


def is_school_day(events: list[dict], today: date) -> bool | None:
    """Return None outside published school years; never guess future dates."""
    years = [e.get("school_year") for e in events if isinstance(e.get("school_year"), int)]
    if not years:
        return None
    if not (date(min(years), 9, 15) <= today < date(max(years) + 1, 9, 15)):
        return None
    return today.weekday() < 5 and active(events, today) is None
