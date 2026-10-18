# Luxembourg School Calendar

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=defuuss&repository=luxembourg-school-calendar&category=integration)
[![Configure in Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=luxembourg_school_calendar)

Independent Home Assistant integration for school holidays in Luxembourg, providing **both Fundamental and Secondary calendars** from one installation.

**Current version: 0.3.0 beta.** This is a community project, not an official government integration. Always verify important dates against the Ministry before making family scheduling automations.

## Install

1. Click **Open in HACS** above (or add the GitHub repository as a custom Integration).
2. Download **Luxembourg School Calendar** (prefer the latest numbered GitHub release).
3. Restart Home Assistant after installing or changing the Python code.
4. Click **Configure in Home Assistant** or use **Settings → Devices & services → Add integration**.
5. Choose your language and a preferred school level. **Both levels are always created.** The preferred level only determines which entities retain original v0.1.0 unique IDs.

## Both calendars

- **Luxembourg School Holidays (Fundamental)**: includes any fundamental-only days, including Saint Nicholas Day.
- **Luxembourg School Holidays (Secondary)**: excludes fundamental-only days.

Each level has its own calendar, School Holidays and School Day binary sensors, and Next School Holiday and Days Until School Holiday sensors. Shared sensors are **School Calendar Last Sync** and **School Calendar Source Status**. That makes 12 entities total.

Home Assistant assigns actual entity IDs; find them under Devices & services → Entities.

## Sources and update logic

The integration checks for updates about once a day:

1. **Primary: Ministry of Education** — https://men.public.lu/fr/vacances-scolaires.html . The official published school calendar is authoritative.
2. **Backup: data.public.lu ICS dataset** — https://data.public.lu/fr/datasets/vacances-et-conges-scolaires/ . The dataset is a CC0 feed published by EducDesign S.A. and is specifically labeled as covering fundamental education. It is used only after the Ministry download or parsing fails.
3. **Local persistent cache:** When the feeds are unavailable or stale, continue using the last verified schedule.

The **School Calendar Source Status** sensor reports:

- ministry — Ministry HTML was downloaded and validated.
- open_data — the ICS fallback was successfully downloaded and validated.
- cache — both sources were unusable or fallback data was older than cached official Ministry information.

Old or malformed ICS data will not silently replace a newer and more complete Ministry calendar. Unrecognized recurrence patterns are deliberately rejected rather than silently omitted. All event dates are validated.

The integration preserves the last good calendar across restarts and recalculates local binary sensor state just after midnight without a network request.

## Updating with HACS

GitHub Actions creates a **numbered GitHub release** on the main branch whenever the integration manifest version changes, but only after Python tests and Home Assistant Hassfest succeed. HACS prefers numbered releases when present.

HACS custom repositories normally poll GitHub about every 48 hours. To check sooner, open this repository in HACS and select **Update information**.

**Existing installations:** If you installed an early commit before the first release, HACS may not automatically switch from default-branch commit tracking to release tracking. Choose **Redownload → 0.3.0** once, then restart Home Assistant.

## Known limitations

- Ministry HTML is not a versioned machine-readable API; upstream page changes can break its parser.
- The Open Data resource is produced by EducDesign, not the Ministry; it is an optional backup and may be out of date.
- The ISC fallback implements ordinary VEVENT date ranges, not all possible recurrence extensions.
- There is no support for exceptional school closures, school-specific events or unpublished future calendar years.
- The school-day state is unknown outside the calendar's published school-year coverage.
- This project ships an original lion-calendar icon, not the official Luxembourg government crest.

## Development

    python -m pip install pytest
    python -m pytest -q tests
    python -m compileall -q custom_components

GitHub Actions runs these tests, Hassfest, and an automatic release job.

License: MIT, copyright (c) 2026 defuuss.
