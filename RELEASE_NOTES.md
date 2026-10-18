# Luxembourg School Calendar 1.0.0

First stable release of the independent HACS integration for Luxembourg school holidays.

### Included features

- Fundamental and Secondary holiday calendars, both created from a single installation.
- School-day and holiday binary sensors; next-holiday and countdown sensors for both levels.
- Daily update using the Luxembourg Ministry of Education as primary source.
- Validated data.public.lu ICS fallback, with persistent offline cache.
- French, Luxembourgish, German and English labels.
- Original red-lion calendar branding and one-click Home Assistant/HACS installation links.
- GitHub Actions unit tests and Home Assistant Hassfest validation.

### Improvements for this release

- Cleaner README: removed the beta banner and hard-coded current version.
- Simplified setup: new installations select only a language because both calendars are created automatically.
- Fixed entity identity stability: the legacy school-level identity is now based on the original configuration entry, so editing options no longer swaps which school level owns existing unique IDs.
- Added a future improvements roadmap.

### Updating

Install or redownload the latest release in HACS and restart Home Assistant. Earlier installations that tracked commits instead of releases may need to select this release manually once.

The project remains independently maintained and is not affiliated with or endorsed by the Luxembourg government.
