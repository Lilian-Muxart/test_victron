import logging
import dataclasses  # Assurez-vous d'importer dataclasses
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Configuration version
CONFIG_VERSION = 1

# Plateformes que l'intégration supporte
_PLATFORMS = {"sensor", "switch", "light"}  # Exemple de plateformes à intégrer

# Constantes de configuration
CONF_DEVICE_ID: Final = "device_id"
CONF_DEVICE_NAME: Final = "device_name"
CONF_DEVICE_AREA: Final = "device_area"
CONF_EMAIL: Final = "email"
CONF_PASSWORD: Final = "password"

# Structure de données pour les appareils
@dataclasses.dataclass
class DeviceData:
    device_id: str
    name: str
    area: str
    email: str
    password: str

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurer l'intégration à partir de l'entrée de configuration."""
    if entry.version != CONFIG_VERSION:
        _LOGGER.warning("Migration nécessaire pour la version de configuration.")
        return False

    _LOGGER.info("Configuration de l'entrée: %s", entry.title)

    # Extraire les informations de l'appareil
    device_id = entry.data[CONF_DEVICE_ID]
    device_name = entry.data[CONF_DEVICE_NAME]
    device_area = entry.data[CONF_DEVICE_AREA]
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]

    # Créer un objet DeviceData
    device_data = DeviceData(device_id, device_name, device_area, email, password)

    # Sauvegarder les informations dans hass.data pour un accès ultérieur
    if "victron_integration" not in hass.data:
        hass.data["victron_integration"] = {}

    hass.data["victron_integration"][entry.entry_id] = device_data

    _LOGGER.info("Appareil configuré: %s, Zone: %s", device_name, device_area)

    # Ajouter les plateformes comme des services de Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    # Eventuellement, effectuer des actions supplémentaires pour configurer l'appareil
    # Par exemple, se connecter à une API externe pour initialiser l'appareil

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Supprimer l'entrée de configuration."""
    if "victron_integration" not in hass.data or entry.entry_id not in hass.data["victron_integration"]:
        return False

    _LOGGER.info("Suppression de la configuration pour l'entrée: %s", entry.title)

    # Supprimer les données de l'appareil stockées
    del hass.data["victron_integration"][entry.entry_id]

    # Décharger les plateformes associées
    await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)

    return True
