from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, area_registry

from .const import DOMAIN  # pylint:disable=unused-import
from .hub import Hub

_LOGGER = logging.getLogger(__name__)

# Define schemas for the input fields
ID_DEVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): str,
    vol.Required("device_name"): str,
    vol.Required("room"): str,
})

MQTT_SCHEMA = vol.Schema({
    vol.Required("email"): str,
    vol.Required("password"): str,
})

# Function to validate the input data
async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    # Example of validating the device connection (add more validation as needed)
    if len(data["device_id"]) < 3:
        raise InvalidDeviceID

    # Simulate connection to the device or MQTT server if necessary
    # In a real implementation, you'd validate the connection here
    hub = Hub(hass, data["device_id"])  # Hypothetical Hub to connect to the device
    result = await hub.test_connection()
    if not result:
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": data["device_name"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                # Validate device input
                info = await validate_input(self.hass, user_input)
                # Store the device-specific data
                device_data = {
                    "device_id": user_input["device_id"],
                    "device_name": user_input["device_name"],
                }

                # Get all available rooms (zones) in Home Assistant
                areas = self.hass.data.get("area_registry").areas
                room_options = {area.name: area.id for area in areas}

                return self.async_show_form(
                    step_id="room_selection",
                    data_schema=vol.Schema({
                        vol.Required("room"): vol.In(room_options)
                    }),
                    errors=errors,
                    description_placeholders=device_data,
                    options={"room_options": room_options},
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidDeviceID:
                errors["device_id"] = "invalid_device_id"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form for the first step (device setup)
        return self.async_show_form(
            step_id="user", data_schema=ID_DEVICE_SCHEMA, errors=errors
        )

    async def async_step_room_selection(self, user_input=None):
        """Handle the room selection step."""
        errors = {}
        if user_input is not None:
            try:
                # Store the room selection
                room = user_input["room"]
                device_data = self.context.get("description_placeholders")
                device_data["room"] = room

                # Move to the next step (asking for MQTT credentials)
                return self.async_show_form(
                    step_id="mqtt_credentials",
                    data_schema=MQTT_SCHEMA,
                    errors=errors,
                    description_placeholders=device_data,
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form for selecting room
        room_options = self.context.get("options", {}).get("room_options", {})
        return self.async_show_form(
            step_id="room_selection",
            data_schema=vol.Schema({
                vol.Required("room"): vol.In(room_options)
            }),
            errors=errors,
        )

    async def async_step_mqtt_credentials(self, user_input=None):
        """Handle the MQTT credentials step."""
        errors = {}
        if user_input is not None:
            try:
                # Validate the MQTT credentials (email and password)
                email = user_input["email"]
                password = user_input["password"]
                
                # Simulate validation of credentials (you would validate it against your server)
                if len(email) < 5 or len(password) < 8:
                    raise InvalidAuth
                
                # Successfully validated, create the entry
                device_data = self.context.get("description_placeholders")
                config_data = {
                    **device_data,  # Device information
                    "email": email,
                    "password": password
                }
                return self.async_create_entry(
                    title=device_data["device_name"], data=config_data
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form for MQTT credentials
        return self.async_show_form(
            step_id="mqtt_credentials", data_schema=MQTT_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidDeviceID(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid device ID."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate invalid authentication."""  
