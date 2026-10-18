## Luxembourg School Calendar 0.3.0

- **Ministry first:** Download and validate the official Luxembourg Ministry of Education's school-calendar page daily.
- **Open Data backup:** If the Ministry fails, attempt the ICS feed published on data.public.lu by EducDesign S.A.
- **Cache protection:** Preserve the existing validated calendar if both live sources fail, or the backup is older and less complete than saved Ministry dates.
- **New status values:** The source-status sensor now reports ministry, open_data, or cache.
- **Two calendars:** Fundamental and Secondary entities remain available with independent holiday and school-day sensors.
- **Updates:** This release is published automatically after GitHub Actions unit tests and Hassfest checks pass.

**Upgrade:** Install or redownload version 0.3.0 through HACS, then restart Home Assistant. Earlier installs tracking the default branch may need a one-time manual selection of this release.
