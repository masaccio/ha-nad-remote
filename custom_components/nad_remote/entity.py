"""NADEntity class"""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_NAME

from .const import DOMAIN, NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)


class NADEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": f"{self.config_entry.title} ({self.zone})",
            "model": self.model,
            "manufacturer": NAME,
        }
