from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import voluptuous as vol

class AppareilConfigFlow(config_entries.ConfigFlow, domain="appareil_integration"):
    """Gère la configuration de l'intégration Appareil."""
    
    def __init__(self):
        """Initialisation du flow."""
        self.device_id = None
        self.device_name = None
        self.area_name = None

    async def async_step_user(self, user_input=None):
        """Affiche le formulaire pour l'utilisateur."""
        if user_input is not None:
            # Si l'utilisateur a fourni des informations, on les enregistre
            self.device_id = user_input["device_id"]
            self.device_name = user_input["device_name"]
            self.area_name = user_input["area_name"]
            
            # Ajouter l'appareil et l'affecter à la pièce
            await ajouter_appareil(self.hass, self.device_id, self.device_name, self.area_name)
            
            return self.async_create_entry(
                title=self.device_name,
                data={"device_id": self.device_id, "device_name": self.device_name}
            )

        # Recherche des pièces existantes dans Home Assistant
        zones = []
        for zone_entity in self.hass.states.async_all('zone'):
            zones.append(zone_entity.name)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_id"): str,
                vol.Required("device_name"): str,
                vol.Required("area_name"): vol.In(zones)  # Liste des pièces existantes
            })
        )
