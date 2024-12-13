from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .config_flow import VictronConfigFlow
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Initialiser l'intégration Victron."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Configurer l'entrée de l'intégration Victron."""
    # Vous pouvez ajouter une logique pour configurer des entités ici
    return True
