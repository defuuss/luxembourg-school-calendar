"""Coverage checks: do not report normal school days outside published years."""
from datetime import date
from pathlib import Path
import importlib.util

HELPERS = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar/helpers.py"
spec = importlib.util.spec_from_file_location("coverage_helpers", HELPERS)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

EVENTS = [
    {"start": "2028-12-06", "end": "2028-12-06", "school_year": 2028, "fundamental_only": True},
    {"kind": "summer", "start": "2029-07-13", "end": "2029-09-16", "school_year": 2028, "fundamental_only": False},
]


def test_unknown_outside_published_years():
    assert h.is_covered(EVENTS, date(2030, 1, 7)) is False
    assert h.is_school_day(EVENTS, date(2030, 1, 7)) is None


def test_known_holiday_at_end_of_coverage():
    assert h.is_school_day(EVENTS, date(2029, 9, 16)) is False


def test_saint_nicholas_is_fundamental_only():
    assert h.is_school_day(h.relevant(EVENTS, "fundamental"), date(2028, 12, 6)) is False
    assert h.is_school_day(h.relevant(EVENTS, "secondary"), date(2028, 12, 6)) is True
