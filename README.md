# Luxembourg School Calendar

Independent Home Assistant custom integration for Luxembourg school holidays using the official [Ministry of Education calendar](https://men.public.lu/fr/vacances-scolaires.html).

**Early beta (v0.1.0).** The integration parses an HTML page, not a stable API. Verify holiday dates against the Ministry before relying on it for important automations. Installation on a live Home Assistant instance has not yet been verified.

## Features

- Native read-only calendar with all-day events and correct inclusive holiday dates.
- Binary sensors: School Holidays and School Day.
- Sensors: Next School Holiday, Days Until School Holiday, School Calendar Last Sync, School Calendar Source Status.
- Daily download and change detection; cached last valid calendar stored persistently.
- Start from cached data during an Internet outage; automatic retry if no cache exists.
- Recalculate date-dependent sensors just after local midnight without a new download.
- Language options: French, Luxembourgish, German, English.
- School type: fundamental or secondary (Saint Nicholas is fundamental-only).
- Integration options flow for updating preferences.

## HACS installation

1. Open Home Assistant → HACS → three-dot menu → Custom repositories.
2. Add https://github.com/defuuss/luxembourg-school-calendar with type **Integration**.
3. Download the integration, then restart Home Assistant.
4. Open Settings → Devices & services → Add integration → Luxembourg School Calendar.
5. Choose your language and school type. Entity IDs are assigned by Home Assistant and can be viewed in the entity registry.

Manual: copy the custom_components/luxembourg_school_calendar directory into the Home Assistant configuration's custom_components directory and restart.

## Entities

| Type | Display name | Function |
|---|---|---|
| Calendar | Luxembourg School Holidays | All published holiday events |
| Binary sensor | School Holidays | On during known Ministry school holidays |
| Binary sensor | School Day | On during weekdays outside holidays, unknown outside published school years |
| Sensor | Next School Holiday | Next holiday starting after today |
| Sensor | Days Until School Holiday | Days until that upcoming holiday |
| Sensor | School Calendar Last Sync | Last successful remote sync (ISO UTC string) |
| Sensor | School Calendar Source Status | Online or cached after a failed download |

## Updates and reliability

The coordinator checks the [Ministry's school holiday page](https://men.public.lu/fr/vacances-scolaires.html) approximately every 24 hours. It validates entries, calculates a content hash and stores the last verified results with Home Assistant storage. On HTTP failures or unexpected page structure it retains cached events and marks source status as cached. The local midnight callback recalculates state without HTTP traffic. School-day state becomes unknown outside the published year range; no dates are invented.

## Limitations

- The Ministry page is HTML, not an official machine-readable API. Its structure may change.
- Only the Ministry's published school years are supported; future years are not automatically inferred.
- No individual school closures, exceptional timetable changes or preschool-specific breaks.
- Last Sync is an ISO date string, not a timestamp device-class entity.
- The Next Holiday sensor intentionally skips any holiday already in progress.
- French source descriptions are retained regardless of the selected translated event label.
- Unit tests use representative HTML fixtures and do not guarantee live Home Assistant compatibility.

## Development

Install pytest and run the unit tests and Python compilation:

    python -m pip install pytest
    python -m pytest -q tests
    python -m compileall -q custom_components

GitHub Actions also runs Home Assistant hassfest validation.

## License

MIT License, Copyright (c) 2026 defuuss. This project is an original implementation and does not incorporate code from the unlicensed sim0nx/hass_school_holidays_lu repository.
