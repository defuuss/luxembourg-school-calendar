"""Regression tests for stable IDs and dual-calendar selection."""
from pathlib import Path
import importlib.util

HELPERS = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar/helpers.py"
spec = importlib.util.spec_from_file_location("school_helpers", HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


class Entry:
    data = {"school_type": "secondary"}
    options = {}


def test_secondary_existing_entry_retains_legacy_ids():
    assert helpers.school_levels_for_entry(Entry()) == ("secondary", "fundamental")


def test_changing_old_preference_cannot_move_legacy_ids():
    entry = Entry()
    entry.options = {"school_type": "fundamental"}
    assert helpers.school_levels_for_entry(entry) == ("secondary", "fundamental")


def test_new_installation_has_both_calendars():
    entry = Entry()
    entry.data = {"language": "lb"}
    assert helpers.school_levels_for_entry(entry) == ("fundamental", "secondary")


def test_invalid_legacy_type_falls_back_safely():
    entry = Entry()
    entry.data = {"school_type": "other"}
    assert helpers.school_levels_for_entry(entry) == ("fundamental", "secondary")
