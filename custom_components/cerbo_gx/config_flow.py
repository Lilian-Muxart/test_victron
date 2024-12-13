import logging
from homeassistant import config_entries
from homeassistant.const import CONF_ID, CONF_NAME, CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import selector
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get_registry as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get_registry as async_get_entity_registry
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
        self.device_user_name = None  # Nouveau champ pour le nom de l'appareil

    async def async_step_user(self, user_input=None):
        """Handle the user input in the configuration flow."""
        if user_input is None:
            return await self.async_show_form(step_id="user", data_schema=self._get_data_schema())

        # Enregistrer les informations d'entrée de l'utilisateur
        self.device_user_name = user_input["device_name"]  # Le nom de l'appareil
        self.device_name = user_input[CONF_NAME]  # Le nom de la personne (peut-être un label)
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
            title=self.device_user_name,  # Utiliser le nom de l'appareil donné par l'utilisateur
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
        await self._create_device_in_home_assistant(config_entry, self.room, self.device_user_name)

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
            vol.Required("device_name"): str,  # Nom de l'appareil
            vol.Required(CONF_NAME): str,      # Nom du dispositif ou étiquette
            vol.Required(CONF_ID): str,        # ID de l'appareil
            vol.Required("room"): selector.selector(
                {
                    "select": {
                        "options": rooms  # Liste des pièces dynamique
                    }
                }
            ),
            vol.Required(CONF_EMAIL): str,     # Email
            vol.Required(CONF_PASSWORD): str,  # Mot de passe
        }

    async def _create_device_in_home_assistant(self, config_entry, room, device_user_name):
        """Créer un appareil dans Home Assistant et l'associer à la pièce choisie."""

        # Obtenir les registres des entités et des appareils
        device_registry = await async_get_device_registry(self.hass)
        entity_registry = await async_get_entity_registry(self.hass)

        # Créer un appareil dans le registre des appareils avec les informations nécessaires
        device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},  # Identifiant unique pour cet appareil
            "name": device_user_name,  # Utiliser le nom de l'appareil donné par l'utilisateur
            "manufacturer": "Victron",
            "model": "Victron Device",
            "sw_version": "1.0",  # Exemple de version
            "suggested_area": room,  # La pièce où l'appareil est situé
        }

        device = device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            **device_info
        )

        # Créer une entité et l'associer à l'appareil
        entity_id = f"sensor.{config_entry.entry_id}_sensor"
        entity = entity_registry.async_get_or_create(
            "sensor",  # Type d'entité, ici un capteur
            DOMAIN,
            config_entry.entry_id,
            name=f"{device_user_name} Sensor",  # Utiliser le nom donné par l'utilisateur
            device_id=device.id,
        )

        _LOGGER.info(f"Device {device_user_name} créé avec succès et lié à la zone {room}")
