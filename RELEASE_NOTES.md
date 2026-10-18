# Luxembourg School Calendar 1.1.2

## Real Ministry HTML parsing fix

A new live-website test caught a parsing failure in the previous update: the Ministry page includes dated legal-reference links after the holiday calendars. The parser was treating these unrelated links as holiday entries.

- Parse **only the holiday list associated with each school-year heading**.
- Ignore unrelated legal references, site links, and dates appearing after the calendar.
- Add regression coverage for the exact Luxembourg regulation-link issue.
- Require a successful **live Ministry download and parsing check** before GitHub Actions publishes any future release.
- Continue a separate weekly live-source monitor.

All 35 published school-holiday events for 2026/27 through 2028/29 are checked by regression tests, including fundamental-only Saint Nicholas on 6 December 2027 and 2028. The distinction between Fundamental and Secondary calendars is preserved.

The date validation, visibility of new/unknown holiday names, and offline fallback protections introduced in 1.1.1 remain in place.

## Upgrade

Update to 1.1.2 through HACS and restart Home Assistant. Check the School Calendar Source Status sensor for `ministry` and inspect the fundamental-only Saint Nicholas dates in its attributes.
