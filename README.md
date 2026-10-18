# Luxembourg School Calendar

See **which days children have school** in Luxembourg, directly in Home Assistant. This integration creates two school-day calendars: one for **enseignement fondamental** and one for **enseignement secondaire**.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=defuuss&repository=luxembourg-school-calendar&category=integration)
[![Configure in Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=luxembourg_school_calendar)

## How the calendars work

**Calendar entries mean SCHOOL DAYS, not holidays.** Each day with school gets one all-day event named **School Day** (translated into your selected language). If there is no school, that date is **empty** in the calendar.

The following days do **not** appear:

- Saturdays and Sundays.
- Ministry-published school vacations and additional school closures.
- Luxembourg's 11 statutory public holidays, including Easter Monday, Ascension, Whit Monday and the fixed-date holidays.
- **6 December (Saint Nicholas Day) for Fundamental education only.** Secondary education can still have school that day if it is a weekday.

Example: **Monday, 6 December 2027** is empty in Fundamental, but appears as a school day in Secondary.

These are **all-day calendar markers**, not class schedules or school opening hours. They only cover published school years; the integration does not invent future dates. It cannot know about closures specific to an individual school, local emergencies or last-minute announcements that the Ministry has not published.

## Features

- Separate **School Days (Fundamental)** and **School Days (Secondary)** calendars from one installation.
- School-day and holiday binary sensors for each level.
- Next School Day date sensor, next holiday name and days-until-holiday sensors.
- One daily check of the official Ministry calendar, followed by validated Open Data fallback and offline cache.
- French, Luxembourgish, German and English.
- Original red lion/calendar branding.
- 14 Home Assistant entities total (two calendars, four binary sensors and eight sensors).

## Installation

1. Click **Open in HACS** above, or add this repository under **HACS → Custom repositories → Integration**.
2. Download the latest GitHub release and restart Home Assistant.
3. Click **Configure in Home Assistant**, or use **Settings → Devices & services → Add integration**.
4. Select the language. Both school levels are automatically available.

Manual installation: copy `custom_components/luxembourg_school_calendar/` into Home Assistant's `config/custom_components/` folder and restart.

## Entities

| Type | Fundamental | Secondary |
|---|---|---|
| **Calendar** | School Days (Fundamental) | School Days (Secondary) |
| Binary sensor | School Day (Fundamental) | School Day (Secondary) |
| Binary sensor | School Holidays (Fundamental) | School Holidays (Secondary) |
| Date sensor | Next School Day (Fundamental) | Next School Day (Secondary) |
| Sensor | Next School Holiday (Fundamental) | Next School Holiday (Secondary) |
| Sensor | Days Until School Holiday (Fundamental) | Days Until School Holiday (Secondary) |

Two additional shared sensors report the last successful synchronization and the active data source.

The **School Day** binary sensors follow the same rules as the calendars, so they are `on` only on school days. The **School Holidays** binary sensors report published school holidays (not every weekend or public holiday). A missing future school year returns `unknown` rather than a guessed school day.

### Important change for users upgrading from the holiday calendars

Earlier releases displayed **school holidays** as calendar events. The school calendars now display **school days instead**. The integration retains the existing calendar entities' unique IDs to avoid deleting dashboard references; depending on your installation, their entity IDs may still contain `school_holidays`. You can rename those entity IDs under **Settings → Devices & services → Entities** if you prefer.

**Review any automations that trigger on calendar events**: an event now means a day with school, not a holiday. All other holiday and countdown sensors remain available and keep their original meaning.

## How date accuracy works

1. **Primary:** [Ministry of Education calendar](https://men.public.lu/fr/vacances-scolaires.html).
2. **Fallback:** [Open Data ICS school calendar](https://data.public.lu/fr/datasets/vacances-et-conges-scolaires/) (published by EducDesign S.A.; mainly Fundamental).
3. **Offline:** Last validated local data if live downloads fail or an older backup is less complete.

In addition to published holidays, the code independently calculates Luxembourg's 11 [statutory public holidays](https://guichet.public.lu/en/citoyens/travail/conges-jours-feries/jours-feries/travail-jours-feries.html), so dates like 9 May cannot accidentally become school days merely because a source omitted an individual event. Statutory compensatory leave days for employers are not assumed to be school closures.

Both calendars share a daily update coordinator and persistent cache. A GitHub Actions live-source check also verifies that the Ministry's current HTML can be parsed successfully before a new version is released.

## Updates and diagnostics

Open the integration in HACS, select **Update information**, then install or **Redownload** the latest release and restart Home Assistant. HACS may take up to 48 hours to discover updates automatically.

The **School Calendar Source Status** entity shows `ministry`, `open_data` or `cache`; attributes show event count, covered school years and Fundamental-only Saint Nicholas dates.

Home Assistant 2026.3+ loads the original icon and logo from the integration's `brand/` directory. Some older HACS notifications may still show "Icon not available"; this is a known upstream HACS frontend issue, not a missing image.

## Project

- [Releases](https://github.com/defuuss/luxembourg-school-calendar/releases)
- [Roadmap](ROADMAP.md)
- [Issues](https://github.com/defuuss/luxembourg-school-calendar/issues)

Development: run `python -m pip install pytest` then `python -m pytest -q tests`. GitHub Actions also runs Home Assistant Hassfest and live Ministry verification before automatically publishing numbered releases.

MIT licensed, independently developed, and **not an official Luxembourg government integration**.
