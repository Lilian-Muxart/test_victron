import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VictronConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Victron Integration."""

    async def async_step_user(self, user_input=None):
        """Handle the initial user input."""
        if user_input is not None:
            # Valider les entrées et créer la configuration
            device_id = user_input["device_id"]
            device_name = user_input["device_name"]
            device_area = user_input["device_area"]
            email = user_input["email"]
            password = user_input["password"]

            # Créer une entrée de configuration
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Victron Device {device_name}",
                data={
                    "device_id": device_id,
                    "device_name": device_name,
                    "device_area": device_area,
                    "email": email,
                    "password": password
                }
            )

        # Si aucune entrée n'a été fournie, demander à l'utilisateur
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )

    def _get_device_schema(self):
        """Retourne le schéma du formulaire de configuration."""
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol

        return vol.Schema({
            vol.Required("device_id"): cv.string,
            vol.Required("device_name"): cv.string,
            vol.Required("device_area"): cv.string,
            vol.Required("email"): cv.string,
            vol.Required("password"): cv.string
        })
