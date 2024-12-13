import logging
from homeassistant import config_entries
from homeassistant.const import CONF_ID, CONF_NAME, CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import selector
from homeassistant.core import HomeAssistant
from homeassistant.components.device_registry import async_get_registry as async_get_device_registry
from homeassistant.components.entity_registry import async_get_registry as async_get_entity_registry
from . import _get_vrm_broker_url  # Importation correcte depuis __init__.py
from .const import DOMAIN
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

class VictronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a configuration flow for Victron integration."""

    VERSION = 1

    def __init__(self):
        self.id_site = None
        self.device_name = None
        self.room = None
        self.email = None
        self.password = None

    async def async_step_user(self, user_input=None):
        """Handle the user input in the configuration flow."""
        if user_input is None:
            return await self.async_show_form(step_id="user", data_schema=self._get_data_schema())

        # Enregistrer les informations d'entrée de l'utilisateur
        self.device_name = user_input[CONF_NAME]
        self.id_site = user_input[CONF_ID]
        self.room = user_input.get("room")
        self.email = user_input[CONF_EMAIL]
        self.password = user_input[CONF_PASSWORD]

        # Connexion au serveur MQTT
        broker_url = _get_vrm_broker_url(self.id_site)  # Utiliser directement la fonction
        _LOGGER.info(f"Connecting to MQTT broker: {broker_url}")
        # Connectez-vous au broker MQTT ici

        # Créer l'entrée de configuration
        config_entry = await self.async_create_entry(
            title=self.device_name,
            data={
                CONF_NAME: self.device_name,
                CONF_ID: self.id_site,
                "room": self.room,
                CONF_EMAIL: self.email,
                CONF_PASSWORD: self.password,
                "mqtt_broker": broker_url,
            },
        )

        # Créer un appareil et l'associer à une pièce
        await self._create_device_in_home_assistant(config_entry, self.room)

        return config_entry

    async def _get_rooms(self, hass: HomeAssistant):
        """Récupérer les chambres disponibles dans Home Assistant."""
        rooms = []
        # Chercher toutes les entités de type zone qui représentent des pièces
        for entity_id in hass.states.async_entity_ids("zone"):
            state = hass.states.get(entity_id)
            if state:
                rooms.append(state.name)  # Utiliser le nom de la zone (chambre)
        return rooms

    async def _get_data_schema(self, hass: HomeAssistant):
        """Retourner un schéma de formulaire pour l'entrée utilisateur avec des pièces dynamiques."""
        rooms = await self._get_rooms(hass)  # Récupérer les pièces dynamiquement

        # Retourner un schéma avec les pièces récupérées
        return {
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_ID): str,
            vol.Required("room"): selector.selector(
                {
                    "select": {
                        "options": rooms  # Liste des pièces dynamique
                    }
                }
            ),
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
        }

    async def _create_device_in_home_assistant(self, config_entry, room):
        """Créer un appareil dans Home Assistant et l'associer à la pièce choisie."""

        # Obtenir les registres des entités et des appareils
        device_registry = await async_get_device_registry(self.hass)
        entity_registry = await async_get_entity_registry(self.hass)

        # Créer un appareil dans le registre des appareils
        device = device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            name=config_entry.title,
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Victron",
            model="Victron Device",
            sw_version="1.0",  # Exemple de version de l'appareil
        )

        # Créer une entité et l'associer à l'appareil
        entity_id = f"sensor.{config_entry.entry_id}_sensor"
        entity = entity_registry.async_get_or_create(
            "sensor",  # Type d'entité, ici un capteur
            DOMAIN,
            config_entry.entry_id,
            name=f"{config_entry.title} Sensor",
            device_id=device.id,
        )

        # Associer l'entité à la zone (pièce) choisie
        state = self.hass.states.get(entity_id)
        if state:
            await self.hass.services.async_call(
                "zone", "set_zone", {"entity_id": entity_id, "zone": room}
            )
        else:
            _LOGGER.error(f"L'entité {entity_id} n'a pas été trouvée.")
