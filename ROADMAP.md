# Improvement ideas

This is a wishlist for future versions, **not a list of implemented features**. Suggestions and feedback are welcome via GitHub Issues.

## High priority

- **Next school day / first day back:** A dedicated date sensor so users can automate reminders on the evening before school resumes.
- **School-days-remaining countdown:** Count instructional days, not just calendar days, until the next break.
- **Source diagnostics:** Add a diagnostic entity or downloadable diagnostic information with source URL, last check, latest covered school year and reason for fallback.
- **Live source change detection:** Scheduled tests against the Ministry's current page and an alert when its structure changes.

## Medium priority

- **Discrepancy report:** Compare overlapping dates between the Ministry calendar and the Open Data resource without letting an outdated feed overwrite authoritative data.
- **Refresh now button:** A manual update action or button entity that respects sensible rate limits.
- **Dashboard examples:** Home Assistant cards showing both calendars, days until holidays and next school day.
- **Future coverage alerts:** Notify when the published schedule is approaching its last school year.

## Ideas requiring more design

- **School-specific closures:** Optional manually managed events for local schools, independent of government holidays.
- **Custom notification helpers:** Optional built-in holiday start/end alert blueprints.
- **Per-child selection:** Assign Fundamental and Secondary calendars to separate family dashboard sections.
- **Additional machine-readable sources:** Investigate an officially maintained API or ICS feed if the Ministry publishes one.

## Reliability notes

The Ministry calendar is authoritative. Its website is an HTML page rather than a stable API; current parsing is tested against representative fixtures. The Open Data ICS resource is a fallback and may lag behind. The integration retains validated dates in a local cache rather than discarding them during remote failures.
