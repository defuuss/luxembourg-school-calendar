# Luxembourg School Calendar 2.0.0

## School days only — intentional breaking change

The two Home Assistant **calendars now contain school days only**, not school holidays.

- An all-day calendar event means **school is scheduled on that date**.
- No events on weekends, Ministry school holidays or statutory Luxembourg public holidays.
- Fundamental: 6 December is always a day off; Secondary has school on 6 December if it falls on an ordinary school weekday.
- The calendar produces one independent all-day event per actual school day.
- Only published school years are included. No unverified future school days are invented.

### Improvements

- Independent calculation of Luxembourg's 11 statutory holidays (including Easter Monday, Ascension and Whit Monday), protecting school-day status if a source omits a holiday event.
- Common date logic used by School Day binary sensors, Next School Day date sensors and both calendars.
- Unit tests for weekends, vacation weeks, both 6 December school-level exceptions, fixed and moveable public holidays, and missing future years.
- Primary Ministry source, Open Data fallback, offline caching, original branding and existing holiday/countdown sensors are retained.

### Important for existing users

This release changes the meaning of calendar events, so **review calendar-triggered automations**. Calendar entity unique IDs are preserved to avoid orphaning existing entities and dashboard references; their prior `school_holidays` entity IDs may remain even though the displayed calendars now contain school days. If desired, rename the entity IDs manually in Home Assistant.

**School Holidays binary sensors and Next School Holiday countdown sensors are unchanged.**

Install through HACS and restart Home Assistant.
