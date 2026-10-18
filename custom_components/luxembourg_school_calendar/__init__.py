"""Luxembourg School Calendar integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .const import DOMAIN
from .coordinator import HolidayCoordinator

PLATFORMS = ["calendar", "binary_sensor", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = HolidayCoordinator(hass, async_get_clientsession(hass))
    await coordinator.async_load()
    # A cached calendar permits startup during an Internet outage.
    await coordinator.async_refresh()
    if not coordinator.data:
        raise ConfigEntryNotReady("No verified school calendar is available yet")
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    def _midnight(now):
        if coordinator.data:
            coordinator.async_set_updated_data(coordinator.data)

    # Force local date-dependent states to recalculate without an HTTP request.
    entry.async_on_unload(async_track_time_change(hass, _midnight, hour=0, minute=0, second=5))
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
