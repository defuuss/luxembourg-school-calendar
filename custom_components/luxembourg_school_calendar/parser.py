"""Read school holiday entries from the Luxembourg Ministry of Education website."""
from __future__ import annotations

from datetime import date, timedelta
from html.parser import HTMLParser
import re

MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12,
}
DATE_RE = re.compile(
    r"\b(\d{1,2})(?:\s*er)?\s+(" + "|".join(MONTHS) + r")\s+(20\d{2})\b",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"ann[ée]e scolaire\s+(20\d{2})\s*/\s*(20\d{2})", re.I)

# Six regular vacation periods appear in every full published school year.
# Reject a partially parsed calendar rather than marking vacation days as
# ordinary school days when the Ministry changes its page layout.
REQUIRED_BREAKS = frozenset({
    "autumn", "christmas", "carnival", "easter", "whitsun", "summer",
    "ascension",
})


class _ListExtractor(HTMLParser):
    """Capture the first school-holiday <ul> after each school-year heading.

    The Ministry page has unrelated dated <li> elements (e.g. links to legal
    regulations) after the calendars. Never treat those as school holidays.
    """

    _VOID_ELEMENTS = frozenset({"br", "img", "hr", "input", "meta", "link", "wbr"})

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.level = 0
        self.active_tag = None
        self.parts = []
        self.entries = []
        self.year = None
        self._awaiting_calendar_list = False
        self._calendar_list_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "ul":
            if self._awaiting_calendar_list:
                self._calendar_list_depth = 1
                self._awaiting_calendar_list = False
            elif self._calendar_list_depth:
                self._calendar_list_depth += 1

        if self.active_tag:
            if tag not in self._VOID_ELEMENTS:
                self.level += 1
        elif tag in ("h2", "h3") or (tag == "li" and self._calendar_list_depth > 0):
            self.active_tag = tag
            self.level = 1
            self.parts = []

    def handle_startendtag(self, tag, attrs):
        """Self-closing elements do not change the nesting level."""

    def handle_data(self, data):
        if self.active_tag:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if self.active_tag and tag not in self._VOID_ELEMENTS:
            self.level -= 1
            if self.level == 0:
                content = " ".join(" ".join(self.parts).split())
                if self.active_tag in ("h2", "h3"):
                    match = YEAR_RE.search(content)
                    self.year = int(match.group(1)) if match else None
                    self._awaiting_calendar_list = bool(match)
                    self._calendar_list_depth = 0
                elif self.active_tag == "li" and self.year is not None:
                    self.entries.append((self.year, content))
                self.active_tag = None
                self.parts = []

        if tag == "ul" and self._calendar_list_depth:
            self._calendar_list_depth -= 1
            if self._calendar_list_depth == 0 and self.year is not None:
                # The Ministry CMS uses a separate <ul> for every holiday.
                # Keep collecting sibling lists until another heading.
                self._awaiting_calendar_list = True



def _category(value: str) -> str:
    text = value.casefold()
    if "toussaint" in text:
        return "autumn"
    if "noël" in text:
        return "christmas"
    if "carnaval" in text:
        return "carnival"
    if "pâques" in text and "vacances" in text:
        return "easter"
    if "pentecôte" in text and "congé" in text:
        return "whitsun"
    if "été" in text:
        return "summer"
    if re.search(r"saint[\s-]*nicolas", text) or "kleeschen" in text:
        return "st_nicholas"
    if "ascension" in text:
        return "ascension"
    if "pentecôte" in text:
        return "whit_monday"
    if "pâques" in text:
        return "easter_monday"
    if "grand-duc" in text:
        return "national_day"
    if "europe" in text:
        return "europe_day"
    if re.search(r"\b1\s*(?:er)?\s+mai\b", text):
        return "labour_day"
    if "jour de l’an" in text or "jour de l'an" in text:
        return "new_year"
    return "other"


LABELS = {
    "autumn": ("Congé de la Toussaint", "Allerhellegevakanz", "Allerheiligenferien", "Autumn holidays"),
    "christmas": ("Vacances de Noël", "Chrëschtvakanz", "Weihnachtsferien", "Christmas holidays"),
    "carnival": ("Congé de Carnaval", "Fuesvakanz", "Karnevalsferien", "Carnival holidays"),
    "easter": ("Vacances de Pâques", "Ouschtervakanz", "Osterferien", "Easter holidays"),
    "whitsun": ("Congé de la Pentecôte", "Päischtvakanz", "Pfingstferien", "Whitsun holidays"),
    "summer": ("Vacances d’été", "Summervakanz", "Sommerferien", "Summer holidays"),
    "st_nicholas": ("Saint Nicolas", "Kleeschen", "Nikolaustag", "Saint Nicholas Day"),
    "ascension": ("Ascension", "Christi Himmelfaart", "Christi Himmelfahrt", "Ascension Day"),
    "whit_monday": ("Lundi de Pentecôte", "Päischtméindeg", "Pfingstmontag", "Whit Monday"),
    "easter_monday": ("Lundi de Pâques", "Ouschterméindeg", "Ostermontag", "Easter Monday"),
    "national_day": ("Fête nationale", "Nationalfeierdag", "Nationalfeiertag", "National Day"),
    "europe_day": ("Journée de l’Europe", "Europadag", "Europatag", "Europe Day"),
    "labour_day": ("Fête du Travail", "Dag vun der Aarbecht", "Tag der Arbeit", "Labour Day"),
    "new_year": ("Nouvel An", "Neijoerschdag", "Neujahr", "New Year’s Day"),
    "other": ("Congé scolaire", "Schoulfräi", "Schulfreier Tag", "School holiday"),
}


def label(category: str, language: str) -> str:
    return LABELS.get(category, LABELS["other"])[{"fr": 0, "lb": 1, "de": 2, "en": 3}.get(language, 0)]


def _validate(events: list[dict]) -> None:
    school_years = {e["school_year"] for e in events}
    if len(events) < 15 or len(school_years) < 2:
        raise ValueError("Ministry page returned too few school holidays")
    for year in school_years:
        year_events = [e for e in events if e["school_year"] == year]
        kinds = {e["kind"] for e in year_events}
        missing = REQUIRED_BREAKS - kinds
        if missing:
            raise ValueError(f"School year {year}/{year + 1} missing holiday periods: {sorted(missing)}")

        # Other fixed Luxembourg holidays can also make a weekday non-school.
        # They may fall within an already listed vacation period instead of
        # appearing as separate events (e.g. New Year's Day).
        fixed_dates = (
            date(year + 1, 1, 1),
            date(year + 1, 5, 1),
            date(year + 1, 5, 9),
            date(year + 1, 6, 23),
        )
        for holiday_date in fixed_dates:
            if holiday_date.weekday() >= 5:
                continue
            if not any(
                e["start"] <= holiday_date.isoformat() <= e["end"]
                for e in year_events
            ):
                raise ValueError(
                    f"School year {year}/{year + 1} missing legal holiday on "
                    f"{holiday_date}"
                )

        # 6 December is a fundamental-school holiday on school weekdays.
        # On a weekend it need not be explicitly listed in the Ministry page.
        saint_day = date(year, 12, 6)
        if saint_day.weekday() < 5:
            matches = [
                e for e in year_events
                if e["start"] == saint_day.isoformat() and e["end"] == saint_day.isoformat()
                and e["fundamental_only"]
            ]
            if not matches:
                raise ValueError(
                    f"School year {year}/{year + 1} missing fundamental-only "
                    f"Saint Nicholas holiday on {saint_day}"
                )


def parse_ministry_html(html: str) -> list[dict]:
    extractor = _ListExtractor()
    extractor.feed(html)
    events = []
    for academic_year, title in extractor.entries:
        if title.casefold().startswith(("règlement grand-ducal", "loi du ")):
            # Reference links in the page sidebar, not school closures.
            continue
        matches = DATE_RE.findall(title)
        if not matches:
            continue
        if len(matches) > 2:
            raise ValueError(f"Ambiguous Ministry date range: {title}")
        days = [date(int(year), MONTHS[month.casefold()], int(day)) for day, month, year in matches]
        start, end = days[0], days[-1]
        if end < start or end - start > timedelta(days=100):
            raise ValueError(f"Invalid Ministry dates: {title}")
        if start.year not in (academic_year, academic_year + 1):
            raise ValueError(f"Unexpected school year for event: {title}")

        category = _category(title)
        fundamental_only = (
            category == "st_nicholas"
            or "uniquement pour l'enseignement fondamental" in title.casefold()
            or (start == end and start.month == 12 and start.day == 6)
        )
        # Keep unfamiliar dated list items instead of silently discarding a
        # new holiday because its wording isn't in the classifier yet.
        events.append({
            "start": start.isoformat(),
            "end": end.isoformat(),
            "kind": category,
            "title": title if category == "other" else None,
            "fundamental_only": fundamental_only,
            "school_year": academic_year,
            "source_text": title,
            "id": f"{category}-{start.isoformat()}",
        })

    events.sort(key=lambda e: (e["start"], e["end"], e["kind"]))
    events = list({(e["school_year"], e["start"], e["end"], e["kind"]): e for e in events}.values())
    _validate(events)
    return events
