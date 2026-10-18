"""Next school holidays for both levels plus shared synchronization status."""
from datetime import date

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHOOL_NAMES
from .helpers import next_event, relevant, school_levels_for_entry
from .parser import label


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    primary, other = school_levels_for_entry(entry)
    async_add_entities([
        SchoolSensor(coordinator, entry, kind, school, legacy=school == primary)
        for school in (primary, other)
        for kind in ("next_holiday", "days_until")
    ] + [
        SchoolSensor(coordinator, entry, kind)
        for kind in ("last_sync", "source_status")
    ])


class SchoolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, kind, school_type=None, legacy=False):
        super().__init__(coordinator)
        self.entry, self.kind, self.school_type = entry, kind, school_type
        self._attr_unique_id = (
            f"{entry.entry_id}_{kind}" if legacy or school_type is None
            else f"{entry.entry_id}_{school_type}_{kind}"
        )
        names = {
            "next_holiday": "Next School Holiday",
            "days_until": "Days Until School Holiday",
            "last_sync": "School Calendar Last Sync",
            "source_status": "School Calendar Source Status",
        }
        suffix = f" ({SCHOOL_NAMES[school_type]})" if school_type else ""
        self._attr_name = f"{names[kind]}{suffix}"
        if kind == "days_until":
            self._attr_native_unit_of_measurement = "d"
            self._attr_icon = "mdi:timer-sand"

    def _upcoming(self):
        events = relevant(self.coordinator.data or [], self.school_type)
        return next_event(events, dt_util.now().date())

    @property
    def native_value(self):
        if self.kind == "last_sync":
            return self.coordinator.last_success
        if self.kind == "source_status":
            return "cached" if self.coordinator.offline else "online"
        event = self._upcoming()
        if not event:
            return None
        if self.kind == "days_until":
            return (date.fromisoformat(event["start"]) - dt_util.now().date()).days
        language = self.entry.options.get("language", self.entry.data.get("language", "fr"))
        return label(event["kind"], language)

    @property
    def extra_state_attributes(self):
        if self.kind != "next_holiday":
            return None
        event = self._upcoming()
        return {"start_date": event["start"], "end_date": event["end"]} if event else {}
