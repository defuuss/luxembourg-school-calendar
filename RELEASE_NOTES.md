# Luxembourg School Calendar 1.1.0

## Added

- **Next School Day (Fundamental)** and **Next School Day (Secondary)** date sensors.
- Uses the next actual school day strictly *after today*, skipping weekends, Ministry holidays and fundamental-only days where applicable.
- `days_until` attribute on each Next School Day sensor for reminders and dashboards.
- Returns unknown when future school-year coverage is unavailable rather than guessing.
- Tests for long breaks, ordinary weekends, Saint Nicholas Day and unpublished future school years.

## Compatibility

- Both existing calendars, holiday countdowns, source-status sensors and entity IDs remain unchanged.
- No change to the Ministry-first / Open Data fallback / offline cache order.
- Home Assistant icon files remain bundled; the HACS "Icon not available" notification placeholder is an upstream issue that HACS maintainers report is fixed by Marketplace in Home Assistant 2026.11.

## Upgrade

In HACS, choose Update information if needed, then update or redownload version 1.1.0 and restart Home Assistant.
