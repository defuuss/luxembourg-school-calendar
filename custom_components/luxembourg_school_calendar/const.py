"""Constants for Luxembourg School Calendar."""
from datetime import timedelta

DOMAIN = "luxembourg_school_calendar"
NAME = "Luxembourg School Calendar"
MINISTRY_URL = "https://men.public.lu/fr/vacances-scolaires.html"
# Stable resource link published on data.public.lu (provider: EducDesign S.A.).
OPEN_DATA_ICS_URL = (
    "https://data.public.lu/fr/datasets/r/"
    "17a030a8-d4d4-488a-a867-c7cf5d746657"
)
UPDATE_INTERVAL = timedelta(days=1)
STORAGE_VERSION = 1
LANGUAGES = ("fr", "lb", "de", "en")
SCHOOL_TYPES = ("fundamental", "secondary")
SCHOOL_NAMES = {"fundamental": "Fundamental", "secondary": "Secondary"}
