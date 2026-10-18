"""Parse Luxembourg Ministry of Education school-calendar HTML.

Independent implementation. Dates come from the Ministry, not third-party JSON.
"""
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


class _ListExtractor(HTMLParser):
    """Collect holiday list items beneath school-year headings."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.level = 0
        self.active_tag = None
        self.parts = []
        self.entries = []
        self.year = None

    def handle_starttag(self, tag, attrs):
        if self.active_tag:
            if tag not in ("br", "img", "hr", "input", "meta", "link"):
                self.level += 1
        elif tag in ("h2", "h3", "li"):
            self.active_tag = tag
            self.level = 1
            self.parts = []

    def handle_startendtag(self, tag, attrs):
        """Void elements must not change nesting level."""

    def handle_data(self, data):
        if self.active_tag:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if not self.active_tag:
            return
        if tag in ("br", "img", "hr", "input", "meta", "link"):
            return
        self.level -= 1
        if self.level == 0:
            content = " ".join(" ".join(self.parts).split())
            if self.active_tag in ("h2", "h3"):
                match = YEAR_RE.search(content)
                if match:
                    self.year = int(match.group(1))
            elif self.active_tag == "li" and self.year:
                self.entries.append((self.year, content))
            self.active_tag = None
            self.parts = []


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
    if "saint nicolas" in text:
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


def parse_ministry_html(html: str) -> list[dict]:
    parser = _ListExtractor()
    parser.feed(html)
    events = []
    for academic_year, title in parser.entries:
        matches = DATE_RE.findall(title)
        if not matches:
            continue
        days = [date(int(year), MONTHS[month.casefold()], int(day)) for day, month, year in matches]
        start, end = days[0], days[-1]
        if end < start or end - start > timedelta(days=100):
            raise ValueError(f"Invalid Ministry dates: {title}")
        category = _category(title)
        if category == "other":
            continue
        events.append({
            "start": start.isoformat(),
            "end": end.isoformat(),
            "kind": category,
            "fundamental_only": category == "st_nicholas",
            "school_year": academic_year,
            "source_text": title,
            "id": f"{category}-{start.isoformat()}",
        })
    events.sort(key=lambda item: (item["start"], item["end"], item["kind"]))
    if len(events) < 15 or len({e["school_year"] for e in events}) < 2:
        raise ValueError("Ministry page returned too few school holidays; format may have changed")
    # Avoid duplicate list items without destroying chronological ordering.
    return list({event["id"]: event for event in events}.values())
