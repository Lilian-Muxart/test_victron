import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import async_get_registry as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get_registry as async_get_entity_registry
from .const import DOMAIN
from .config_flow import VictronConfigFlow

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Initialiser l'intégration Victron."""
    _LOGGER.info(f"Setting up Victron integration with domain: {DOMAIN}")
    
    # Enregistrer l'intégration dans hass.data
    hass.data[DOMAIN] = {}

    # Enregistrer le flow de configuration pour l'intégration
    hass.config_entries.async_register_domain(DOMAIN, VictronConfigFlow)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurer l'entrée de l'intégration Victron et créer un appareil."""
    _LOGGER.info(f"Setting up Victron entry: {entry.title}")
    
    # Extraire les données de l'entrée
    device_name = entry.data["name"]
    id_site = entry.data["id"]
    room = entry.data["room"]
    mqtt_broker = entry.data["mqtt_broker"]

    # Créer un appareil dans Home Assistant
    device_registry = await async_get_device_registry(hass)

    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, id_site)},  # Utilise l'ID du site comme identifiant
        name=device_name,
        model="Victron Device",  # Vous pouvez mettre un modèle si nécessaire
        manufacturer="Victron Energy",
        suggested_area=room,  # L'appareil est associé à la pièce
    )
    
    # Créer des entités pour l'appareil
    # Par exemple, une entité d'état pour cet appareil
    await create_device_entity(hass, device, mqtt_broker)

    return True

async def create_device_entity(hass: HomeAssistant, device, mqtt_broker: str):
    """Créer une entité liée à l'appareil."""
    # Créer une entité représentant l'état de l'appareil
    entity_registry = await async_get_entity_registry(hass)

    # Exemple d'entité : "device_name" + "_status"
    entity = entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{device.name}_status",  # L'entité aura un nom basé sur le nom de l'appareil
        unique_id=f"{device.id}_status",  # ID unique pour l'entité
        name=f"{device.name} Status",
        icon="mdi:power",
        device_id=device.id,
        state="Unknown",  # L'état initial, cela peut être modifié plus tard via MQTT ou autre
    )

    # Vous pouvez également créer d'autres entités en fonction de ce que vous voulez exposer (consommation, température, etc.)
    # L'entité sera liée à cet appareil, et vous pourrez la contrôler via le MQTT ou d'autres moyens

    # Ajoutez ici des entités supplémentaires si nécessaire

    _LOGGER.info(f"Created entity {entity.name} for device {device.name}")
