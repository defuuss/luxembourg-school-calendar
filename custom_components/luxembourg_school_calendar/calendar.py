"""Calendars containing actual school days, never school closures."""
from datetime import date, datetime, time, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHOOL_NAMES
from .helpers import (
    is_school_day,
    next_school_day,
    relevant,
    school_days_between,
    school_levels_for_entry,
)

SCHOOL_DAY_TITLES = {
    "fr": "Jour d'école",
    "lb": "Schouldag",
    "de": "Schultag",
    "en": "School Day",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    primary, other = school_levels_for_entry(entry)
    # Preserve existing unique IDs to keep dashboard and automation references.
    # Version 2 changes calendar *semantics*, not entity identity.
    async_add_entities([
        SchoolDayCalendar(coordinator, entry, primary, legacy=True),
        SchoolDayCalendar(coordinator, entry, other),
    ])


class SchoolDayCalendar(CoordinatorEntity, CalendarEntity):
    _attr_icon = "mdi:school"
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, entry, school_type, legacy=False):
        super().__init__(coordinator)
        self.entry = entry
        self.school_type = school_type
        self._attr_name = f"Luxembourg School Days ({SCHOOL_NAMES[school_type]})"
        self._attr_unique_id = (
            f"{entry.entry_id}_calendar" if legacy
            else f"{entry.entry_id}_calendar_{school_type}"
        )

    @property
    def _holidays(self):
        return relevant(self.coordinator.data or [], self.school_type)

    @property
    def _summary(self):
        language = self.entry.options.get("language", self.entry.data.get("language", "fr"))
        return SCHOOL_DAY_TITLES.get(language, SCHOOL_DAY_TITLES["fr"])

    def _make_event(self, school_day: date) -> CalendarEvent:
        return CalendarEvent(
            start=school_day,
            end=school_day + timedelta(days=1),
            summary=self._summary,
            uid=f"{self.school_type}-school-{school_day.isoformat()}",
        )

    @property
    def event(self):
        today = dt_util.now().date()
        day = (
            today if is_school_day(self._holidays, today, self.school_type)
            else next_school_day(self._holidays, today, self.school_type)
        )
        return self._make_event(day) if day else None

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime):
        if end_date <= start_date:
            return []
        # Calendar input bounds use the local Home Assistant timezone.
        # Include the final date only if the requested end time is after midnight.
        end_day = end_date.date()
        if end_date.time() != time.min:
            end_day += timedelta(days=1)

        return [
            self._make_event(day)
            for day in school_days_between(
                self._holidays, start_date.date(), end_day, self.school_type
            )
        ]
