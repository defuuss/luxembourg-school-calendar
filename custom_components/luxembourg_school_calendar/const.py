"""Constants for Luxembourg School Calendar."""
from datetime import timedelta

DOMAIN = "luxembourg_school_calendar"
NAME = "Luxembourg School Calendar"
MINISTRY_URL = "https://men.public.lu/fr/vacances-scolaires.html"
UPDATE_INTERVAL = timedelta(days=1)
STORAGE_VERSION = 1
LANGUAGES = ("fr", "lb", "de", "en")
SCHOOL_TYPES = ("fundamental", "secondary")
