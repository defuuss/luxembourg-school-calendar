"""Next holiday, countdown, and data-source status sensors."""
from datetime import date
from homeassistant.util import dt as dt_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .helpers import relevant, next_event
from .parser import label


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SchoolSensor(coordinator, entry, kind)
        for kind in ("next_holiday", "days_until", "last_sync", "source_status")
    ])


class SchoolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, kind):
        super().__init__(coordinator)
        self.entry, self.kind = entry, kind
        self._attr_unique_id = f"{entry.entry_id}_{kind}"
        self._attr_name = {
            "next_holiday": "Next School Holiday",
            "days_until": "Days Until School Holiday",
            "last_sync": "School Calendar Last Sync",
            "source_status": "School Calendar Source Status",
        }[kind]
        if kind == "days_until":
            self._attr_native_unit_of_measurement = "d"
            self._attr_icon = "mdi:timer-sand"

    @property
    def native_value(self):
        if self.kind == "last_sync":
            return self.coordinator.last_success
        if self.kind == "source_status":
            return "cached" if self.coordinator.offline else "online"
        school = self.entry.options.get("school_type", self.entry.data["school_type"])
        today = dt_util.now().date()
        upcoming = next_event(relevant(self.coordinator.data or [], school), today)
        if not upcoming:
            return None
        if self.kind == "days_until":
            return (date.fromisoformat(upcoming["start"]) - today).days
        lang = self.entry.options.get("language", self.entry.data["language"])
        return label(upcoming["kind"], lang)

    @property
    def extra_state_attributes(self):
        if self.kind != "next_holiday":
            return None
        school = self.entry.options.get("school_type", self.entry.data["school_type"])
        event = next_event(relevant(self.coordinator.data or [], school), dt_util.now().date())
        return {"start_date": event["start"], "end_date": event["end"]} if event else {}
