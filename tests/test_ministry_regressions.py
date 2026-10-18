"""Regression tests based on the Ministry's published 2026–2029 dates.

The simplified HTML fixture mirrors the ministry's headings and dated list
items, including Saint Nicholas being fundamental-only in 2027 and 2028.
"""
from datetime import date
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser = load("parser")
helpers = load("helpers")

SCHOOL_YEAR_EVENTS = {
    2026: [
        "le congé de la Toussaint commence le samedi 31 octobre 2026 et finit le dimanche 8 novembre 2026",
        "les vacances de Noël commencent le samedi 19 décembre 2026 et finissent le dimanche 3 janvier 2027",
        "le congé de Carnaval commence le samedi 6 février 2027 et finit le dimanche 14 février 2027",
        "les vacances de Pâques commencent le samedi 27 mars 2027 et finissent le dimanche 11 avril 2027",
        "jour férié légal : samedi 1<sup>er</sup> mai 2027",
        "jour férié légal pour l’Ascension : jeudi 6 mai 2027",
        "jour férié légal le lundi de Pentecôte : lundi 17 mai 2027",
        "le congé de la Pentecôte commence le samedi 29 mai 2027 et finit le dimanche 6 juin 2027",
        "jour de congé pour la célébration publique de l’anniversaire de S.A.R. le Grand-Duc : mercredi 23 juin 2027",
        "les vacances d’été commencent le vendredi 16 juillet 2027 et finissent le mardi 14 septembre 2027",
    ],
    2027: [
        "le congé de la Toussaint commence le samedi 30 octobre 2027 et finit le dimanche 7 novembre 2027",
        "la fête de Saint Nicolas : lundi le 6 décembre 2027 (uniquement pour l'enseignement fondamental)",
        "les vacances de Noël commencent le samedi 18 décembre 2027 et finissent le dimanche 2 janvier 2028",
        "le congé de Carnaval commence le samedi 12 février 2028 et finit le dimanche 20 février 2028",
        "les vacances de Pâques commencent le samedi 1<sup>er</sup> avril 2028 et finissent le dimanche 16 avril 2028",
        "jour férié légal le lundi de Pâques : lundi 17 avril 2028",
        "jour férié légal : lundi 1<sup>er</sup> mai 2028",
        "jour férié légal de la Journée de l’Europe : mardi 9 mai 2028",
        "jour de congé pour l’Ascension : jeudi 25 mai 2028",
        "le congé de la Pentecôte commence le samedi 27 mai 2028 et finit le dimanche 4 juin 2028",
        "jour férié légal le lundi de Pentecôte : lundi 5 juin 2028",
        "jour de congé pour la célébration publique de l’anniversaire de S.A.R. le Grand-Duc : vendredi 23 juin 2028",
        "les vacances d’été commencent le vendredi 14 juillet 2028 et finissent le jeudi 14 septembre 2028",
    ],
    2028: [
        "le congé de la Toussaint commence le samedi 28 octobre 2028 et finit le dimanche 5 novembre 2028",
        "la fête de Saint Nicolas : mercredi 6 décembre 2028 (uniquement pour l'enseignement fondamental)",
        "les vacances de Noël commencent le samedi 16 décembre 2028 et finissent le dimanche 31 décembre 2028",
        "jour férié légal le Jour de l’an : lundi 1<sup>er</sup> janvier 2029",
        "le congé de Carnaval commence le samedi 10 février 2029 et finit le dimanche 18 février 2029",
        "les vacances de Pâques commencent le samedi 31 mars 2029 et finissent le dimanche 15 avril 2029",
        "jour férié légal : mardi 1<sup>er</sup> mai 2029",
        "jour férié légal de la Journée de l’Europe : mercredi 9 mai 2029",
        "jour férié légal pour l’Ascension : jeudi 10 mai 2029",
        "le congé de la Pentecôte commence le samedi 19 mai 2029 et finit le dimanche 27 mai 2029",
        "jour de congé pour la célébration publique de l’anniversaire de S.A.R. le Grand-Duc : samedi 23 juin 2029",
        "les vacances d’été commencent le vendredi 13 juillet 2029 et finissent le dimanche 16 septembre 2029",
    ],
}


def ministry_fixture(events_by_year=None):
    years = events_by_year or SCHOOL_YEAR_EVENTS
    return "\n".join(
        f"<h2>Année scolaire {year}/{year + 1}</h2><ul>"
        + "".join(f"<li>{event}</li>" for event in entries)
        + "</ul>"
        for year, entries in years.items()
    )


def test_all_35_official_holidays_are_preserved():
    events = parser.parse_ministry_html(ministry_fixture())
    assert len(events) == 35
    assert sorted({e["school_year"] for e in events}) == [2026, 2027, 2028]
    assert {e["kind"] for e in events if e["start"] == "2029-01-01"} == {"new_year"}
    assert {e["kind"] for e in events if e["start"] == "2028-05-25"} == {"ascension"}
    assert any(e["kind"] == "summer" and e["end"] == "2029-09-16" for e in events)


def test_saint_nicholas_2027_and_2028_only_fundamental():
    events = parser.parse_ministry_html(ministry_fixture())
    fundamental = helpers.relevant(events, "fundamental")
    secondary = helpers.relevant(events, "secondary")
    for year in (2027, 2028):
        holiday = date(year, 12, 6)
        assert helpers.active(fundamental, holiday)["kind"] == "st_nicholas"
        assert helpers.active(secondary, holiday) is None
        assert helpers.is_school_day(fundamental, holiday) is False
        assert helpers.is_school_day(secondary, holiday) is True
        assert helpers.next_school_day(fundamental, date(year, 12, 5)) == date(year, 12, 7)
        assert helpers.next_school_day(secondary, date(year, 12, 5)) == date(year, 12, 6)


def test_2026_saint_nicholas_is_a_sunday_not_a_separate_holiday():
    events = parser.parse_ministry_html(ministry_fixture())
    assert date(2026, 12, 6).weekday() == 6
    assert helpers.is_school_day(helpers.relevant(events, "fundamental"), date(2026, 12, 6)) is False
    assert helpers.is_school_day(helpers.relevant(events, "secondary"), date(2026, 12, 6)) is False


def test_missing_saint_nicholas_rejects_incomplete_ministry_data():
    data = {year: items[:] for year, items in SCHOOL_YEAR_EVENTS.items()}
    data[2027] = [e for e in data[2027] if "Saint Nicolas" not in e]
    try:
        parser.parse_ministry_html(ministry_fixture(data))
    except ValueError as err:
        assert "Saint Nicholas" in str(err)
    else:
        raise AssertionError("Missing fundamental holiday must reject incomplete download")


def test_missing_regular_vacation_rejects_incomplete_ministry_data():
    data = {year: items[:] for year, items in SCHOOL_YEAR_EVENTS.items()}
    data[2028] = [e for e in data[2028] if "Carnaval" not in e]
    try:
        parser.parse_ministry_html(ministry_fixture(data))
    except ValueError as err:
        assert "carnival" in str(err)
    else:
        raise AssertionError("Missing holiday period must reject incomplete download")


def test_unknown_new_holiday_is_not_silently_dropped():
    data = {year: items[:] for year, items in SCHOOL_YEAR_EVENTS.items()}
    data[2027].append("jour de congé exceptionnel : jeudi 3 février 2028")
    events = parser.parse_ministry_html(ministry_fixture(data))
    extra = next(e for e in events if e["start"] == "2028-02-03")
    assert extra["kind"] == "other"
    assert "congé exceptionnel" in extra["title"]
    assert len(events) == 36


def test_saint_nicolas_hyphenated_name_still_fundamental_only():
    data = {year: items[:] for year, items in SCHOOL_YEAR_EVENTS.items()}
    data[2027] = [e.replace("Saint Nicolas", "Saint-Nicolas") for e in data[2027]]
    events = parser.parse_ministry_html(ministry_fixture(data))
    saint = next(e for e in events if e["start"] == "2027-12-06")
    assert saint["kind"] == "st_nicholas"
    assert saint["fundamental_only"]


def test_page_legal_references_not_misread_as_holidays():
    # The real Ministry page has a regulation link under the calendar.
    # Its date is not a vacation, even though the link mentions school years.
    legal_links = (
        "<ul><li>Règlement grand-ducal du 3 juin 2026 fixant les "
        "calendriers des vacances et congés scolaires pour les années "
        "scolaires 2026/2027, 2027/2028 et 2028/2029</li></ul>"
    )
    events = parser.parse_ministry_html(ministry_fixture() + legal_links)
    assert len(events) == 35
    assert not any(e["start"] == "2026-06-03" for e in events)


def test_real_ministry_layout_one_list_per_holiday():
    # The actual Ministry CMS wraps each holiday in its own UL.
    html = "\n".join(
        f"<h2>Année scolaire {year}/{year + 1}</h2>"
        + "".join(f"<ul><li>{event}</li></ul>" for event in events)
        for year, events in SCHOOL_YEAR_EVENTS.items()
    )
    html += (
        "<h2 id='page-more__title'>Pour en savoir plus</h2>"
        "<ul><li>Règlement grand-ducal du 3 juin 2026 fixant les calendriers "
        "des vacances pour les années scolaires 2026/2027, 2027/2028 "
        "et 2028/2029</li></ul>"
    )
    parsed = parser.parse_ministry_html(html)
    assert len(parsed) == 35
    assert len(helpers.relevant(parsed, "secondary")) == 33
    assert helpers.active(helpers.relevant(parsed, "fundamental"), date(2027, 12, 6))
    assert helpers.active(helpers.relevant(parsed, "secondary"), date(2027, 12, 6)) is None
