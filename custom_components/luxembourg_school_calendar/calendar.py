"""Home Assistant read-only school holiday calendar."""
from datetime import date, datetime, timedelta
from homeassistant.util import dt as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .helpers import relevant, active, next_event
from .parser import label


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LuxCalendar(hass.data[DOMAIN][entry.entry_id], entry)])


class LuxCalendar(CoordinatorEntity, CalendarEntity):
    _attr_name = "Luxembourg School Holidays"
    _attr_icon = "mdi:calendar-school"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def _events(self):
        school_type = self.entry.options.get("school_type", self.entry.data["school_type"])
        return relevant(self.coordinator.data or [], school_type)

    def _make_event(self, e):
        lang = self.entry.options.get("language", self.entry.data["language"])
        return CalendarEvent(
            start=date.fromisoformat(e["start"]),
            end=date.fromisoformat(e["end"]) + timedelta(days=1),
            summary=label(e["kind"], lang),
            description=e.get("source_text", ""),
            uid=e["id"],
        )

    @property
    def event(self):
        today = dt_util.now().date()
        current = active(self._events, today)
        upcoming = next_event(self._events, today)
        return self._make_event(current or upcoming) if current or upcoming else None

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime):
        return [
            ev for e in self._events
            if (ev := self._make_event(e)).start < end_date.date()
            and ev.end > start_date.date()
        ]
