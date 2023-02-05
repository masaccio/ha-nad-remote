"""Switch platform for NAD Amplifer remote control."""
import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .entity import NADEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup Switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_devices([NADBinarySwitch(coordinator, config_entry)])


class NADBinarySwitch(NADEntity, SwitchEntity):
    """nad_remote switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        _LOGGER.debug("switch on")
        # await self.coordinator.api.async_set_title("bar")
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        _LOGGER.debug("switch off")
        # await self.coordinator.api.async_set_title("foo")
        # await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DOMAIN}_test"

    # @property
    # def icon(self):
    #     """Return the icon of this switch."""
    #     return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        _LOGGER.debug("switch is_on")
        return True
        # return self.coordinator.data.get("title", "") == "foo"
