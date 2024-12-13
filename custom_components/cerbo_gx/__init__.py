from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .config_flow import VictronConfigFlow
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Initialiser l'intégration Victron."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Configurer l'entrée de l'intégration Victron."""
    # Vous pouvez ajouter une logique pour configurer des entités ici
    return True

def _get_vrm_broker_url(id_site):
    """Calculer l'URL du serveur MQTT basé sur l'ID du site."""
    sum = 0
    for character in id_site.lower().strip():
        sum += ord(character)
    broker_index = sum % 128
    return f"mqtt{broker_index}.victronenergy.com"
