# Luxembourg School Calendar 1.1.1

## Date correctness and validation

- Confirmed the official Ministry distinction: 6 December is a school holiday **only for Fundamental**, including Monday 2027-12-06 and Wednesday 2028-12-06. Both levels remain off school on Sunday 2026-12-06.
- Added comprehensive regression tests against all **35 published 2026/27–2028/29 Ministry calendar entries**, including both Saint Nicholas dates and the 2029 New Year's Day event.
- The Ministry parser now keeps unfamiliar dated holiday entries instead of silently discarding them.
- Validates regular vacation periods, weekday Saint Nicholas holidays and fixed-date public holidays in each published school year; incomplete remote calendars are rejected and fallback/cached data are used.
- Improved recognition of Saint-Nicolas with hyphenated spelling.

## Home Assistant sensors

- **School Calendar Source Status** attributes now expose event count, covered school years, last event date and fundamental-only Saint Nicholas dates, making troubleshooting easier.
- Holiday and school-day binary sensors return **unknown** outside published school-year coverage, rather than reporting a falsely definitive off/on state.
- Existing entity IDs are unchanged.

## Monitoring

- Added a weekly GitHub Actions live Ministry calendar check, plus a manual run option. This independently detects upstream changes to the HTML.

## Update

Install 1.1.1 through HACS and restart Home Assistant. Inspect `sensor.school_calendar_source_status` (the actual entity ID may differ) and confirm the Saint Nicholas dates are present in its attributes. As before, the primary data source is the Ministry, then Open Data ICS fallback, then saved cache.
