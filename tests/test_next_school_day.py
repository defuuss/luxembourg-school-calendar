"""Tests for Next School Day, weekends, holidays and school types."""
from datetime import date
from pathlib import Path
import importlib.util

HELPERS = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar/helpers.py"
spec = importlib.util.spec_from_file_location("next_school_day_helpers", HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

EVENTS = [
    {"start": "2026-10-31", "end": "2026-11-08", "school_year": 2026, "fundamental_only": False},
    {"start": "2027-12-06", "end": "2027-12-06", "school_year": 2027, "fundamental_only": True},
    {"start": "2027-12-18", "end": "2028-01-02", "school_year": 2027, "fundamental_only": False},
    {"kind": "summer", "start": "2028-07-14", "end": "2028-09-14", "school_year": 2027, "fundamental_only": False},
]


def next_day(level, on):
    return helpers.next_school_day(helpers.relevant(EVENTS, level), on)


def test_friday_before_holiday_returns_monday_after_holiday():
    assert next_day("fundamental", date(2026, 10, 30)) == date(2026, 11, 9)
    assert next_day("secondary", date(2026, 10, 30)) == date(2026, 11, 9)


def test_last_day_of_holiday_returns_first_school_day():
    assert next_day("fundamental", date(2026, 11, 8)) == date(2026, 11, 9)


def test_normal_weekend_skipped():
    assert next_day("fundamental", date(2026, 11, 13)) == date(2026, 11, 16)
    assert next_day("secondary", date(2026, 11, 14)) == date(2026, 11, 16)


def test_saint_nicholas_day_differs_between_levels():
    assert next_day("fundamental", date(2027, 12, 5)) == date(2027, 12, 7)
    assert next_day("secondary", date(2027, 12, 5)) == date(2027, 12, 6)


def test_last_published_summer_does_not_invent_next_year():
    assert next_day("fundamental", date(2028, 9, 13)) is None
    assert next_day("secondary", date(2028, 9, 14)) is None


def test_empty_calendar_has_no_next_day():
    assert helpers.next_school_day([], date(2026, 11, 13)) is None
