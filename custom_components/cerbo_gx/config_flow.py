import logging
from copy import deepcopy
from typing import Dict, Any
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import EntityRegistry

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_AREA_NAME = "area_name"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

class AppareilConfigFlow(ConfigFlow, domain="appareil_integration"):
    """Gère la configuration de l'intégration Appareil."""

    def __init__(self):
        self.config_entry: ConfigEntry | None = None
        self.new_data = {}
        self.new_options = {}

    def set_current_config_entry(self, config_entry: ConfigEntry) -> None:
        """Réinitialise l'entrée de configuration actuelle."""
        self.config_entry = config_entry
        self.new_data = deepcopy(dict(config_entry.data))
        self.new_options = deepcopy(dict(config_entry.options))

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Affiche le formulaire de configuration pour l'utilisateur."""

        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_DEVICE_NAME): str,
                    vol.Required(CONF_AREA_NAME): str,
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                })
            )

        # Enregistrer les données de configuration
        self.new_data[CONF_DEVICE_ID] = user_input.get(CONF_DEVICE_ID)
        self.new_data[CONF_DEVICE_NAME] = user_input.get(CONF_DEVICE_NAME)
        self.new_data[CONF_AREA_NAME] = user_input.get(CONF_AREA_NAME)
        self.new_data[CONF_EMAIL] = user_input.get(CONF_EMAIL)
        self.new_data[CONF_PASSWORD] = user_input.get(CONF_PASSWORD)

        # Créer l'entrée de configuration
        return self.async_create_entry(
            title=self.new_data[CONF_DEVICE_NAME],
            data=self.new_data,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Si reconfiguration, réinitialise l'entrée et relance le flux."""
        self.set_current_config_entry(self.hass.config_entries.async_get_entry(self.context["entry_id"]))
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AppareilOptionsFlow(config_entry)

class AppareilOptionsFlow(OptionsFlow):
    """Gestion des options pour l'intégration Appareil."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Étape initiale de la configuration des options."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL, default=self.config_entry.data.get(CONF_EMAIL, "")): str,
                vol.Required(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD, "")): str,
            })
        )

    async def async_step_options(self, user_input: dict[str, Any] | None = None):
        """Mise à jour des options (email, mot de passe)."""
        if user_input:
            self.config_entry.data[CONF_EMAIL] = user_input[CONF_EMAIL]
            self.config_entry.data[CONF_PASSWORD] = user_input[CONF_PASSWORD]
            self.hass.config_entries.async_update_entry(
                entry_id=self.config_entry.entry_id,
                data=self.config_entry.data
            )
            return self.async_create_entry(title="Appareil Configuré", data={})
        return self.async_show_form(step_id="options", data_schema=vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
        }))
