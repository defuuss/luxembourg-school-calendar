"""Home Assistant configuration flow and language options."""
import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, LANGUAGES

# Both school levels are created, so no school-type choice is necessary.
CONFIG_SCHEMA = vol.Schema({
    vol.Required("language", default="fr"): vol.In(LANGUAGES),
})


class LuxembourgSchoolCalendarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="Luxembourg School Calendar", data=user_input)
        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

    @staticmethod
    def async_get_options_flow(config_entry):
        return LuxembourgSchoolCalendarOptionsFlow()


class LuxembourgSchoolCalendarOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        values = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema({
            vol.Required("language", default=values.get("language", "fr")): vol.In(LANGUAGES),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
