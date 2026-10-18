"""Unit tests with representative entries from Luxembourg's Ministry calendar."""
from datetime import date
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1] / "custom_components/luxembourg_school_calendar"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


p = load("parser")
h = load("helpers")

SAMPLE = """<h2>Année scolaire 2026/2027</h2><ul>
<li>le congé de la Toussaint commence le samedi 31 octobre 2026 et finit le dimanche 8 novembre 2026 ;</li>
<li>les vacances de Noël commencent le samedi 19 décembre 2026 et finissent le dimanche 3 janvier 2027 ;</li>
<li>le congé de Carnaval commence le samedi 6 février 2027 et finit le dimanche 14 février 2027 ;</li>
<li>les vacances de Pâques commencent le samedi 27 mars 2027 et finissent le dimanche 11 avril 2027 ;</li>
<li>jour férié légal : samedi 1<sup>er</sup> mai 2027 ;</li>
<li>jour férié légal pour l’Ascension : jeudi 6 mai 2027 ;</li>
<li>jour férié légal le lundi de Pentecôte : lundi 17 mai 2027 ;</li>
<li>le congé de la Pentecôte commence le samedi 29 mai 2027 et finit le dimanche 6 juin 2027 ;</li>
<li>jour de congé pour l’anniversaire du Grand-Duc : mercredi 23 juin 2027 ;</li>
<li>les vacances d’été commencent le vendredi 16 juillet 2027 et finissent le mardi 14 septembre 2027.</li>
</ul>
<h2>Année scolaire 2027/2028</h2><ul>
<li>le congé de la Toussaint commence le samedi 30 octobre 2027 et finit le dimanche 7 novembre 2027 ;</li>
<li>la fête de Saint Nicolas : lundi le 6 décembre 2027 (uniquement pour l'enseignement fondamental) ;</li>
<li>les vacances de Noël commencent le samedi 18 décembre 2027 et finissent le dimanche 2 janvier 2028 ;</li>
<li>le congé de Carnaval commence le samedi 12 février 2028 et finit le dimanche 20 février 2028 ;</li>
<li>les vacances de Pâques commencent le samedi 1<sup>er</sup> avril 2028 et finissent le dimanche 16 avril 2028 ;</li>
<li>jour férié légal le lundi de Pâques : lundi 17 avril 2028 ;</li>
<li>jour férié légal : lundi 1<sup>er</sup> mai 2028 ;</li>
<li>jour férié légal de la Journée de l’Europe : mardi 9 mai 2028 ;</li>
<li>jour de congé pour l’Ascension : jeudi 25 mai 2028 ;</li>
<li>le congé de la Pentecôte commence le samedi 27 mai 2028 et finit le dimanche 4 juin 2028 ;</li>
<li>jour férié légal le lundi de Pentecôte : lundi 5 juin 2028 ;</li>
<li>jour de congé anniversaire du Grand-Duc : vendredi 23 juin 2028 ;</li>
<li>les vacances d’été commencent le vendredi 14 juillet 2028 et finissent le jeudi 14 septembre 2028.</li>
</ul>"""


def test_official_dates_and_school_type():
    events = p.parse_ministry_html(SAMPLE)
    assert len(events) == 23
    assert [e["start"] for e in events] == sorted(e["start"] for e in events)
    ascension = next(e for e in events if e["kind"] == "ascension" and e["start"].startswith("2028"))
    assert ascension["start"] == ascension["end"] == "2028-05-25"
    saint = next(e for e in events if e["kind"] == "st_nicholas")
    assert saint["fundamental_only"]
    assert saint not in h.relevant(events, "secondary")
    assert h.active(events, date(2026, 11, 2))["kind"] == "autumn"
    assert h.is_school_day(events, date(2026, 11, 2)) is False
    assert h.is_school_day(events, date(2026, 11, 14)) is False
    assert h.is_school_day(events, date(2026, 11, 16)) is True
    assert h.is_school_day(events, date(2029, 10, 1)) is None


def test_reject_invalid_html():
    try:
        p.parse_ministry_html("<html>Calendar unavailable</html>")
    except ValueError:
        return
    raise AssertionError("Invalid page must not replace stored dates")


def test_language_names():
    assert p.label("st_nicholas", "lb") == "Kleeschen"
    assert p.label("summer", "de") == "Sommerferien"
