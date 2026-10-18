"""Fetch official Ministry dates daily; retain a verified offline copy."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import logging

from aiohttp import ClientError, ClientTimeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store

from .const import DOMAIN, MINISTRY_URL, STORAGE_VERSION, UPDATE_INTERVAL
from .parser import parse_ministry_html

_LOGGER = logging.getLogger(__name__)


class HolidayCoordinator(DataUpdateCoordinator[list[dict]]):
    def __init__(self, hass, session):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.session = session
        self.store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.calendar")
        self.last_success: str | None = None
        self.content_hash: str | None = None
        self.cached_events: list[dict] = []
        self.offline = False

    async def async_load(self):
        cached = await self.store.async_load()
        if not isinstance(cached, dict) or not isinstance(cached.get("events"), list):
            return
        events = cached["events"]
        if not events or not all(
            isinstance(e, dict) and isinstance(e.get("start"), str)
            and isinstance(e.get("end"), str) and isinstance(e.get("school_year"), int)
            for e in events
        ):
            return
        self.cached_events = events
        self.last_success = cached.get("last_success")
        self.content_hash = cached.get("hash")
        self.async_set_updated_data(events)

    async def _async_update_data(self) -> list[dict]:
        try:
            async with self.session.get(MINISTRY_URL, timeout=ClientTimeout(total=25)) as response:
                response.raise_for_status()
                html = await response.text()
            events = parse_ministry_html(html)
            digest = hashlib.sha256(html.encode()).hexdigest()
        except (ClientError, TimeoutError, ValueError) as err:
            self.offline = True
            if self.cached_events:
                _LOGGER.warning("School calendar download failed; keeping cached events: %s", err)
                return self.cached_events
            raise UpdateFailed(f"Cannot download a valid school calendar: {err}") from err
        self.offline = False
        self.last_success = datetime.now(timezone.utc).isoformat()
        if digest != self.content_hash or not self.cached_events:
            self.cached_events = events
            self.content_hash = digest
        self.store.async_delay_save(
            lambda: {
                "events": self.cached_events,
                "hash": self.content_hash,
                "last_success": self.last_success,
            },
            1,
        )
        return self.cached_events
