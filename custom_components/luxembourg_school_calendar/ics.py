"""Fallback parser for the CC0 school calendar ICS feed from data.public.lu.

Only standard all-day and dated VEVENT ranges are interpreted. For an ICS
all-day event, DTEND is exclusive. Unsupported recurrence rules are rejected
rather than silently yielding an incomplete calendar.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import re


def _ical_unescape(value: str) -> str:
    return (
        value.replace(r"\n", " ")
        .replace(r"\N", " ")
        .replace(r"\,", ",")
        .replace(r"\;", ";")
        .replace(r"\\", "\\")
    )


def _event_date(value: str) -> date:
    """Parse iCalendar date or datetime; the date portion is local to event."""
    if not re.match(r"^\d{8}(?:T\d{6}Z?)?$", value):
        raise ValueError(f"Unsupported iCalendar date: {value[:40]}")
    return datetime.strptime(value[:8], "%Y%m%d").date()


def _kind(name: str) -> str:
    s = name.casefold()
    # Distinguish one-day holidays before broader multi-day categories.
    patterns = (
        ("st_nicholas", ("nicolas", "nikolaus", "kleeschen")),
        ("national_day", ("grand-duc", "nationalfeier", "nationalfeiertag", "fête nationale")),
        ("ascension", ("ascension", "himmelfahrt", "himmelfaart")),
        ("whit_monday", ("lundi de pentecôte", "pfingstmontag", "päischtméindeg")),
        ("easter_monday", ("lundi de pâques", "ostermontag", "ouschterméindeg")),
        ("europe_day", ("journée de l’europe", "journée de l'europe", "europatag")),
        ("labour_day", ("fête du travail", "tag der arbeit", "dag vun der aarbecht")),
        ("autumn", ("toussaint", "allerheilig", "allerhell", "halloween")),
        ("christmas", ("noël", "chrëscht", "weihnacht", "christmas")),
        ("carnival", ("carnaval", "karneval", "fues", "fasching")),
        ("easter", ("pâques", "ouschter", "osterferien", "easter")),
        ("whitsun", ("pentecôte", "päischt", "pfingst", "whitsun")),
        ("summer", ("été", "summer", "sommer", "vacances d'ete")),
        ("new_year", ("jour de l’an", "jour de l'an", "neijoer", "neujahr")),
    )
    for category, needles in patterns:
        if any(part in s for part in needles):
            return category
    return "other"


def parse_open_data_ics(body: str, today: date | None = None) -> list[dict]:
    """Validate and parse Open Data holiday ranges as a fallback.

    Require future coverage rather than accepting an old, stale calendar.
    """
    if "BEGIN:VCALENDAR" not in body:
        raise ValueError("Response is not an iCalendar feed")
    unfolded: list[str] = []
    for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    events: list[dict] = []
    props: dict[str, str] | None = None
    for line in unfolded:
        if line == "BEGIN:VEVENT":
            props = {}
            continue
        if line == "END:VEVENT":
            if props is None:
                continue
            if props.get("STATUS", "").upper() == "CANCELLED":
                props = None
                continue
            if "RRULE" in props or "RDATE" in props or "EXDATE" in props:
                raise ValueError("Unsupported recurrence in Open Data calendar")
            if "DTSTART" not in props or "SUMMARY" not in props:
                props = None
                continue
            start = _event_date(props["DTSTART"])
            if "DTEND" in props:
                # End dates are exclusive in RFC 5545; date-only and timed
                # events are converted to inclusive day ranges.
                end_exclusive = _event_date(props["DTEND"])
                end = max(start, end_exclusive - timedelta(days=1))
            else:
                end = start
            if end < start or end - start > timedelta(days=100):
                raise ValueError("Invalid event range in Open Data calendar")
            summary = _ical_unescape(props["SUMMARY"]).strip()
            kind = _kind(summary)
            school_year = start.year if start.month >= 9 else start.year - 1
            fundamental_only = kind == "st_nicholas" or (start.month == 12 and start.day == 6 and start == end)
            events.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "kind": kind,
                "title": summary,
                "fundamental_only": fundamental_only,
                "school_year": school_year,
                "source_text": _ical_unescape(props.get("DESCRIPTION", summary)),
                "id": f"ics-{start.isoformat()}-{kind}-{len(events)}",
            })
            props = None
            continue
        if props is not None and ":" in line:
            key, value = line.split(":", 1)
            props[key.split(";", 1)[0].upper()] = value
    events.sort(key=lambda e: (e["start"], e["end"], e["id"]))
    events = list({(e["start"], e["end"], e["kind"], e["title"]): e for e in events}.values())
    if len(events) < 10:
        raise ValueError("Open Data calendar has too few events")
    today = today or date.today()
    if not any(date.fromisoformat(event["end"]) >= today + timedelta(days=180) for event in events):
        raise ValueError("Open Data calendar is outdated (insufficient future coverage)")
    return events
