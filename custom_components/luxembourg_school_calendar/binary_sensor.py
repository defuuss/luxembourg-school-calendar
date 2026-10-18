"""Holiday and school-day binary sensors."""
from homeassistant.util import dt as dt_util
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .helpers import relevant, active, is_school_day


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SchoolBinary(coordinator, entry, "holidays"),
        SchoolBinary(coordinator, entry, "school_day"),
    ])


class SchoolBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, kind):
        super().__init__(coordinator)
        self.entry, self.kind = entry, kind
        self._attr_unique_id = f"{entry.entry_id}_{kind}"
        self._attr_name = "School Holidays" if kind == "holidays" else "School Day"
        self._attr_icon = "mdi:beach" if kind == "holidays" else "mdi:school"

    @property
    def is_on(self):
        school = self.entry.options.get("school_type", self.entry.data["school_type"])
        events = relevant(self.coordinator.data or [], school)
        today = dt_util.now().date()
        if self.kind == "holidays":
            return bool(active(events, today))
        return is_school_day(events, today)
