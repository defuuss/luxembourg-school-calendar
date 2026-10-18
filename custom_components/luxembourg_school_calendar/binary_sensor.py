"""School holiday and school day sensors for both education levels."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHOOL_NAMES
from .helpers import active, is_school_day, relevant, school_levels_for_entry


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    primary, other = school_levels_for_entry(entry)
    async_add_entities([
        SchoolBinary(coordinator, entry, kind, school, legacy=school == primary)
        for school in (primary, other)
        for kind in ("holidays", "school_day")
    ])


class SchoolBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, kind, school_type, legacy=False):
        super().__init__(coordinator)
        self.kind = kind
        self.school_type = school_type
        self._attr_unique_id = (
            f"{entry.entry_id}_{kind}" if legacy
            else f"{entry.entry_id}_{school_type}_{kind}"
        )
        title = "School Holidays" if kind == "holidays" else "School Day"
        self._attr_name = f"{title} ({SCHOOL_NAMES[school_type]})"
        self._attr_icon = "mdi:beach" if kind == "holidays" else "mdi:school"

    @property
    def is_on(self):
        events = relevant(self.coordinator.data or [], self.school_type)
        today = dt_util.now().date()
        if self.kind == "holidays":
            return bool(active(events, today))
        return is_school_day(events, today)
