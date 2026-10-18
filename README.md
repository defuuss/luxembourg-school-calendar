# Luxembourg School Calendar

A community-maintained Home Assistant integration for the official Luxembourg [Ministry of Education school holidays](https://men.public.lu/fr/vacances-scolaires.html).

> **Beta 0.2.0** — The Ministry HTML parser may need adjustments when the official page changes. Verify important dates with the Ministry before scheduling family automations. This is **not an official government integration**.

## Install in one click

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=defuuss&repository=luxembourg-school-calendar&category=integration)

1. Open the button above on a device connected to your Home Assistant instance.
2. Download **Luxembourg School Calendar** from HACS and restart Home Assistant if necessary.
3. Use the button below to start setup, or select **Settings → Devices & services → Add integration**.

[![Configure in Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=luxembourg_school_calendar)

For manual installation, copy `custom_components/luxembourg_school_calendar` into your Home Assistant `config/custom_components/` directory, then restart.

## Both school calendars, automatically

**One integration installation creates both calendars simultaneously:**

- **Luxembourg School Holidays (Fundamental)** — includes fundamental-only days such as St Nicholas Day.
- **Luxembourg School Holidays (Secondary)** — excludes fundamental-only days.

Both calendars use the same centrally downloaded and cached schedule. They can be shown separately on a dashboard and referenced independently from Home Assistant automations.

The **preferred school level** setting controls which calendar retains the original unique IDs from v0.1.0. This helps preserve existing automations. **It does not disable the other calendar.** An existing installation keeps its previously selected school level as its preferred level.

## Entities

| Type | Fundamental | Secondary |
|---|---|---|
| Calendar | Luxembourg School Holidays (Fundamental) | Luxembourg School Holidays (Secondary) |
| Binary sensor | School Holidays (Fundamental) | School Holidays (Secondary) |
| Binary sensor | School Day (Fundamental) | School Day (Secondary) |
| Sensor | Next School Holiday (Fundamental) | Next School Holiday (Secondary) |
| Sensor | Days Until School Holiday (Fundamental) | Days Until School Holiday (Secondary) |

Also provides two shared sensors: **School Calendar Last Sync** and **School Calendar Source Status**. That's **12 entities** in total (2 calendars, 4 binary sensors, 6 regular sensors). Home Assistant assigns actual entity IDs from the entity registry. An existing entity retains its original ID unless you rename it manually.

## Updates and reliability

- Downloads the [Ministry school calendar](https://men.public.lu/fr/vacances-scolaires.html) approximately once every 24 hours.
- Validates the returned calendar and stores the last good version for offline use.
- Updates date-based states after local midnight without additional HTTP requests.
- Supports French, Luxembourgish, German and English.
- Distinguishes fundamental and secondary schools, notably for St Nicholas Day.

## Known limitations

- The source is government HTML, not a stable machine-readable API.
- School-specific closures and unannounced exceptional closures aren't included.
- The next-holiday sensor skips holidays already in progress.
- School-day sensor is **unknown** outside published school-year coverage.
- Tests and Home Assistant hassfest validation do not replace testing on a real instance.
- The government crest/logo is not included; the project uses independently designed Luxembourg-inspired branding.

## Development

```bash
python -m pip install pytest
python -m pytest -q tests
python -m compileall -q custom_components
```

License: MIT. © 2026 defuuss. Not affiliated with or endorsed by the Luxembourg government.
