"""School-day calendars contain ONLY teaching days.

These tests verify weekend, public holiday and school-level exclusions
independently of whether each statutory holiday appears as a Ministry event.
"""
from datetime import date, timedelta
from pathlib import Path
import importlib.util

MODULE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/luxembourg_school_calendar/helpers.py"
)
spec = importlib.util.spec_from_file_location("school_calendar_helpers_v2", MODULE)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


EVENTS = [
    {"kind": "autumn", "start": "2026-10-31", "end": "2026-11-08", "school_year": 2026},
    {"kind": "christmas", "start": "2026-12-19", "end": "2027-01-03", "school_year": 2026},
    {"kind": "summer", "start": "2027-07-16", "end": "2027-09-14", "school_year": 2026},
    {"kind": "st_nicholas", "start": "2027-12-06", "end": "2027-12-06",
     "school_year": 2027, "fundamental_only": True},
    {"kind": "summer", "start": "2028-07-14", "end": "2028-09-14", "school_year": 2027},
    {"kind": "st_nicholas", "start": "2028-12-06", "end": "2028-12-06",
     "school_year": 2028, "fundamental_only": True},
    {"kind": "summer", "start": "2029-07-13", "end": "2029-09-16", "school_year": 2028},
]


def days(level, start, end):
    return helpers.school_days_between(
        helpers.relevant(EVENTS, level), start, end, level
    )


def test_no_events_on_weekends_or_during_vacations():
    assert days("fundamental", date(2026, 10, 30), date(2026, 11, 11)) == [
        date(2026, 10, 30), date(2026, 11, 9), date(2026, 11, 10)
    ]
    assert days("secondary", date(2026, 10, 31), date(2026, 11, 9)) == []


def test_6_december_is_fundamental_only_school_closed():
    for year in (2027, 2028):
        start, end = date(year, 12, 6), date(year, 12, 7)
        assert days("fundamental", start, end) == []
        assert days("secondary", start, end) == [start]


def test_statutory_fixed_holidays_excluded_without_explicit_event():
    # No event for Europe Day, Labour Day or National Day is in EVENTS.
    for d in (date(2028, 5, 1), date(2028, 5, 9), date(2027, 6, 23)):
        assert d.weekday() < 5
        for level in ("fundamental", "secondary"):
            assert days(level, d, d + timedelta(days=1)) == []


def test_movable_public_holidays_and_easter_computus():
    assert helpers.easter_sunday(2026) == date(2026, 4, 5)
    assert helpers.easter_sunday(2027) == date(2027, 3, 28)
    assert helpers.easter_sunday(2028) == date(2028, 4, 16)
    assert helpers.easter_sunday(2029) == date(2029, 4, 1)
    for d in (date(2027, 5, 6), date(2027, 5, 17),
              date(2028, 4, 17), date(2028, 5, 25)):
        assert d in helpers.public_holidays(d.year)
        assert helpers.is_school_day(EVENTS, d, "secondary") is False


def test_all_11_public_holidays_and_no_monday_substitution():
    holidays = helpers.public_holidays(2027)
    assert len(holidays) == 11
    assert date(2027, 5, 9) in holidays  # Europe Day is Sunday.
    assert date(2027, 5, 10) not in holidays


def test_calendar_does_not_invent_unpublished_school_year():
    for level in ("fundamental", "secondary"):
        assert days(level, date(2029, 9, 17), date(2029, 10, 1)) == []
        assert helpers.is_school_day(EVENTS, date(2029, 9, 17), level) is None


def test_school_day_and_next_day_share_same_rules():
    e = helpers.relevant(EVENTS, "fundamental")
    assert helpers.next_school_day(e, date(2027, 12, 5), "fundamental") == date(2027, 12, 7)
    assert helpers.next_school_day(
        helpers.relevant(EVENTS, "secondary"), date(2027, 12, 5), "secondary"
    ) == date(2027, 12, 6)


def test_missing_saint_nicholas_in_fallback_is_still_excluded_for_fundamental():
    missing = [e for e in EVENTS if e.get("kind") != "st_nicholas"]
    assert helpers.is_school_day(missing, date(2027, 12, 6), "fundamental") is False
    assert helpers.is_school_day(missing, date(2027, 12, 6), "secondary") is True


def test_no_events_if_source_has_no_complete_school_year():
    truncated = [{"kind": "autumn", "start": "2027-10-30",
                  "end": "2027-11-07", "school_year": 2027}]
    assert helpers.school_days_between(
        truncated, date(2027, 10, 1), date(2027, 11, 1), "fundamental"
    ) == []
