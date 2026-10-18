"""ICS fallback tests with deterministic fixed dates."""
from datetime import date
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar"
spec = importlib.util.spec_from_file_location("ics_parser", ROOT / "ics.py")
ics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ics)


def fixture():
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0"]
    for i in range(11):
        start = date(2026 + i // 6, 10 if i % 2 else 12, 6)
        end = date.fromordinal(start.toordinal() + 1)
        lines += [
            "BEGIN:VEVENT",
            f"UID:holiday-{i}@example.org",
            f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end:%Y%m%d}",
            "SUMMARY:Saint Nicolas" if i == 0 else f"SUMMARY:Congé de Carnaval {i}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def test_fallback_ics_parsing_and_exclusive_end():
    parsed = ics.parse_open_data_ics(fixture(), today=date(2026, 1, 1))
    assert len(parsed) == 11
    saint = next(e for e in parsed if e["kind"] == "st_nicholas")
    assert saint["start"] == saint["end"] == "2026-12-06"
    assert saint["fundamental_only"]
    assert parsed[-1]["school_year"] == 2027


def test_reject_stale_ics():
    try:
        ics.parse_open_data_ics(fixture(), today=date(2032, 1, 1))
    except ValueError:
        return
    raise AssertionError("Expired fallback must fail validation")


def test_reject_non_ics():
    try:
        ics.parse_open_data_ics("<html>No calendar here</html>", today=date(2026, 1, 1))
    except ValueError:
        return
    raise AssertionError("HTML response must not be trusted as ICS")


def test_reject_recurrence():
    value = fixture().replace("SUMMARY:Saint Nicolas", "RRULE:FREQ=YEARLY\r\nSUMMARY:Saint Nicolas")
    try:
        ics.parse_open_data_ics(value, today=date(2026, 1, 1))
    except ValueError:
        return
    raise AssertionError("Recurrences must not be silently dropped")
