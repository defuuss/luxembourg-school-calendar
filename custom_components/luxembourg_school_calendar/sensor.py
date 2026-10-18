"""Holiday date, next school day and synchronization sensors for both levels."""
from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHOOL_NAMES
from .helpers import next_event, next_school_day, relevant, school_levels_for_entry
from .parser import label


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    primary, other = school_levels_for_entry(entry)
    async_add_entities([
        SchoolSensor(coordinator, entry, kind, school, legacy=school == primary)
        for school in (primary, other)
        for kind in ("next_holiday", "days_until", "next_school_day")
    ] + [
        SchoolSensor(coordinator, entry, kind)
        for kind in ("last_sync", "source_status")
    ])


class SchoolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, kind, school_type=None, legacy=False):
        super().__init__(coordinator)
        self.entry, self.kind, self.school_type = entry, kind, school_type
        # New entities use explicit school types, existing unique IDs are stable.
        if kind == "next_school_day":
            self._attr_unique_id = f"{entry.entry_id}_{school_type}_{kind}"
        else:
            self._attr_unique_id = (
                f"{entry.entry_id}_{kind}" if legacy or school_type is None
                else f"{entry.entry_id}_{school_type}_{kind}"
            )
        names = {
            "next_holiday": "Next School Holiday",
            "days_until": "Days Until School Holiday",
            "next_school_day": "Next School Day",
            "last_sync": "School Calendar Last Sync",
            "source_status": "School Calendar Source Status",
        }
        suffix = f" ({SCHOOL_NAMES[school_type]})" if school_type else ""
        self._attr_name = f"{names[kind]}{suffix}"
        if kind == "days_until":
            self._attr_native_unit_of_measurement = "d"
            self._attr_icon = "mdi:timer-sand"
        elif kind == "next_school_day":
            self._attr_device_class = SensorDeviceClass.DATE
            self._attr_icon = "mdi:school"

    def _events(self):
        return relevant(self.coordinator.data or [], self.school_type)

    def _upcoming(self):
        return next_event(self._events(), dt_util.now().date())

    @property
    def native_value(self):
        if self.kind == "last_sync":
            return self.coordinator.last_success
        if self.kind == "source_status":
            return self.coordinator.source
        if self.kind == "next_school_day":
            return next_school_day(self._events(), dt_util.now().date(), self.school_type)
        event = self._upcoming()
        if not event:
            return None
        if self.kind == "days_until":
            return (date.fromisoformat(event["start"]) - dt_util.now().date()).days
        language = self.entry.options.get("language", self.entry.data.get("language", "fr"))
        return event.get("title") if event.get("kind") == "other" else label(event["kind"], language)

    @property
    def extra_state_attributes(self):
        if self.kind == "source_status":
            events = self.coordinator.data or []
            dates = sorted({
                e["start"] for e in events
                if e.get("fundamental_only") and e.get("start", "")[5:10] == "12-06"
            })
            years = sorted({
                e["school_year"] for e in events
                if isinstance(e.get("school_year"), int)
            })
            return {
                "holiday_event_count": len(events),
                "school_years": [f"{year}/{year + 1}" for year in years],
                "saint_nicholas_fundamental_only": dates,
                "latest_holiday_end": max((e["end"] for e in events), default=None),
            }
        if self.kind == "next_school_day":
            today = dt_util.now().date()
            upcoming = next_school_day(self._events(), today, self.school_type)
            return {"days_until": (upcoming - today).days} if upcoming else {}
        if self.kind != "next_holiday":
            return None
        event = self._upcoming()
        return {"start_date": event["start"], "end_date": event["end"]} if event else {}
