"""Smoke-check current live Ministry HTML without Home Assistant dependencies."""
from datetime import date
from pathlib import Path
import importlib.util
from urllib.request import Request, urlopen

parser_file = (
    Path(__file__).resolve().parents[1]
    / "custom_components/luxembourg_school_calendar/parser.py"
)
spec = importlib.util.spec_from_file_location("ministry_parser", parser_file)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

url = "https://men.public.lu/fr/vacances-scolaires.html"
request = Request(
    url,
    headers={"User-Agent": "HomeAssistant-LuxembourgSchoolCalendar-SourceCheck/1.0",
             "Accept-Language": "fr"},
)
with urlopen(request, timeout=30) as response:
    content = response.read().decode("utf-8")

try:
    events = parser.parse_ministry_html(content)
except ValueError:
    extractor = parser._ListExtractor()
    extractor.feed(content)
    print("HTML bytes:", len(content), flush=True)
    print("Extracted year/list entries:", len(extractor.entries), flush=True)
    print("First extracted entries:", extractor.entries[:3], flush=True)
    for phrase in ("Année scolaire 2026/2027", "Toussaint", "Saint Nicolas", "Règlement grand-ducal"):
        offset = content.casefold().find(phrase.casefold())
        if offset >= 0:
            print(f"HTML near {phrase}: {content[max(0, offset-200):offset+1000]}", flush=True)
    raise
years = sorted({e["school_year"] for e in events})
saint_dates = sorted(e["start"] for e in events if e["kind"] == "st_nicholas")
print(f"Ministry calendar: {len(events)} events, school years {years}")
print(f"Fundamental-only Saint Nicholas dates: {saint_dates}")
assert len(events) >= 20
for year in years:
    saint = date(year, 12, 6)
    if saint.weekday() < 5:
        assert any(e["start"] == saint.isoformat() and e["fundamental_only"] for e in events)
