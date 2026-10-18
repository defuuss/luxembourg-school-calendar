"""Regression tests for the dual-calendar school-level selection."""
from pathlib import Path
import importlib.util

HELPERS = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar/helpers.py"
spec = importlib.util.spec_from_file_location("school_helpers", HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


class Entry:
    data = {"school_type": "secondary"}
    options = {}


def test_secondary_existing_entry_stays_primary():
    assert helpers.school_levels_for_entry(Entry()) == ("secondary", "fundamental")


def test_options_change_primary_and_both_remain():
    entry = Entry()
    entry.options = {"school_type": "fundamental"}
    assert helpers.school_levels_for_entry(entry) == ("fundamental", "secondary")


def test_new_installation_defaults_fundamental():
    entry = Entry()
    entry.data = {}
    assert helpers.school_levels_for_entry(entry) == ("fundamental", "secondary")
