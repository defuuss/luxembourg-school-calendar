"""Use Ministry first, Open Data ICS second, and last valid cache third."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import logging

from aiohttp import ClientError, ClientTimeout
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MINISTRY_URL, OPEN_DATA_ICS_URL, STORAGE_VERSION, UPDATE_INTERVAL
from .ics import parse_open_data_ics
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
        self.source = "cache"

    async def async_load(self):
        cached = await self.store.async_load()
        if not isinstance(cached, dict) or not isinstance(cached.get("events"), list):
            return
        events = cached["events"]
        if not events or not all(
            isinstance(e, dict)
            and isinstance(e.get("start"), str)
            and isinstance(e.get("end"), str)
            and isinstance(e.get("school_year"), int)
            for e in events
        ):
            return
        self.cached_events = events
        self.last_success = cached.get("last_success")
        self.content_hash = cached.get("hash")
        self.source = "cache"
        self.offline = True
        self.async_set_updated_data(events)

    async def _fetch(self, url: str) -> str:
        async with self.session.get(url, timeout=ClientTimeout(total=25)) as response:
            response.raise_for_status()
            return await response.text()

    async def _async_update_data(self) -> list[dict]:
        errors: list[str] = []
        for name, url, parser in (
            ("ministry", MINISTRY_URL, parse_ministry_html),
            ("open_data", OPEN_DATA_ICS_URL, parse_open_data_ics),
        ):
            try:
                raw = await self._fetch(url)
                events = parser(raw)
                # If falling back, do not replace complete authoritative
                # cached coverage with an older and truncated ICS schedule.
                if name == "open_data" and self.cached_events:
                    latest_cached = max(e["end"] for e in self.cached_events)
                    latest_downloaded = max(e["end"] for e in events)
                    if latest_cached > latest_downloaded:
                        raise ValueError("Open Data coverage is older than cached calendar")
                digest = hashlib.sha256((name + "\n" + raw).encode()).hexdigest()
            except (ClientError, TimeoutError, ValueError, UnicodeError) as err:
                errors.append(f"{name}: {err}")
                _LOGGER.warning("School calendar %s source failed validation or download: %s", name, err)
                continue

            self.offline = False
            self.source = name
            self.last_success = datetime.now(timezone.utc).isoformat()
            if digest != self.content_hash or not self.cached_events:
                self.cached_events = events
                self.content_hash = digest
            self.store.async_delay_save(
                lambda: {
                    "events": self.cached_events,
                    "hash": self.content_hash,
                    "last_success": self.last_success,
                    "source": self.source,
                },
                1,
            )
            return self.cached_events

        self.offline = True
        self.source = "cache"
        if self.cached_events:
            _LOGGER.warning("Both school calendar sources failed; retaining cached data: %s", "; ".join(errors))
            return self.cached_events
        raise UpdateFailed(f"No valid school holiday data available: {'; '.join(errors)}")
