"""School holiday calendars for both Luxembourg education levels."""
from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHOOL_NAMES
from .helpers import active, next_event, relevant, school_levels_for_entry
from .parser import label


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    primary, other = school_levels_for_entry(entry)
    async_add_entities([
        LuxCalendar(coordinator, entry, primary, legacy=True),
        LuxCalendar(coordinator, entry, other),
    ])


class LuxCalendar(CoordinatorEntity, CalendarEntity):
    _attr_icon = "mdi:calendar-school"

    def __init__(self, coordinator, entry, school_type, legacy=False):
        super().__init__(coordinator)
        self.entry = entry
        self.school_type = school_type
        self._attr_name = f"Luxembourg School Holidays ({SCHOOL_NAMES[school_type]})"
        self._attr_unique_id = (
            f"{entry.entry_id}_calendar" if legacy
            else f"{entry.entry_id}_calendar_{school_type}"
        )

    @property
    def _events(self):
        return relevant(self.coordinator.data or [], self.school_type)

    def _make_event(self, item):
        language = self.entry.options.get("language", self.entry.data.get("language", "fr"))
        return CalendarEvent(
            start=date.fromisoformat(item["start"]),
            end=date.fromisoformat(item["end"]) + timedelta(days=1),
            summary=label(item["kind"], language),
            description=item.get("source_text", ""),
            uid=item["id"],
        )

    @property
    def event(self):
        today = dt_util.now().date()
        item = active(self._events, today) or next_event(self._events, today)
        return self._make_event(item) if item else None

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime):
        return [
            converted for item in self._events
            if (converted := self._make_event(item)).start < end_date.date()
            and converted.end > start_date.date()
        ]
