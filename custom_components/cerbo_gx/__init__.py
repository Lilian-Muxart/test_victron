import logging
from homeassistant.helpers import device_registry as dr
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.components import zone

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Appareil Integration."""
    _LOGGER.info("L'intégration Appareil est configurée.")

async def ajouter_appareil(hass: HomeAssistant, device_id: str, device_name: str, area_name: str):
    """Ajoute un appareil et l'affecte à une pièce existante."""

    # Récupérer le registre des appareils
    device_registry = dr.async_get(hass)

    # Vérifier si la pièce existe déjà parmi les zones définies
    area = None
    for zone_entity in hass.states.async_all('zone'):
        if zone_entity.name == area_name:
            area = zone_entity
            break

    if not area:
        _LOGGER.error(f"La pièce '{area_name}' n'existe pas.")
        return

    # Créer l'appareil dans le device registry
    device_registry.async_get_or_create(
        identifiers={(device_id, device_name)},
        name=device_name,
        manufacturer="Unknown",  # À remplacer par le fabricant si nécessaire
        model="Unknown",  # À remplacer par le modèle si nécessaire
        sw_version="1.0",  # À remplacer par la version du firmware si nécessaire
        suggested_area=area_name  # L'assignation de la pièce
    )

    # Assigner l'appareil à la pièce
    device_registry.async_update_device(device_id, area_id=area.entity_id)
    _LOGGER.info(f"Appareil '{device_name}' ajouté à la pièce '{area_name}'.")
