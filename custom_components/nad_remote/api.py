"""NAD Amplifiler API Client for Home Assistant"""
import logging
import re
import sys

_LOGGER: logging.Logger = logging.getLogger(__package__)
sys.path = ["/config/custom_components/nad_remote"] + sys.path

# Use local implementation of NAD client rather than upstream
from .nad_receiver import NADReceiverTelnet
from .const import DOMAIN

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


class NADApiClient:
    def __init__(self, host: str, port: int) -> None:
        """NAD API Client."""
        self._host = host
        self._port = port
        self.capabilities = None
        self.receiver = NADReceiverTelnet(host, port)

    def get_model(self):
        try:
            response = self.receiver.main_model("?")
            if not re.match(r"^\w+\d+", response):
                _LOGGER.debug("Amplifier model '%s' not recognised", response)
                return None
            else:
                _LOGGER.debug("Amplifier model='%s'", response)
                return response
        except Exception as e:
            _LOGGER.error("Error checking amplifier model: %s", e)

    def get_capabilities(self):
        """Fetch status of amplifier to get capabilities"""
        if self.capabilities is not None:
            return self.capabilities
        try:
            self.capabilities = self.receiver.status_all()
            if self.capabilities is None:
                _LOGGER.error("Error fetching amplifier capabilities: no reuslts")
            return self.capabilities
        except Exception as e:
            _LOGGER.error("Error fetching amplifier capabilities: %s", e)

    def get_sources(self):
        """Discover list of sources"""
        sources = {}
        try:
            capabilities = self.get_capabilities()
            source_list = []
            for source_id in range(1, 20):
                s_en = f"source{source_id}_enabled"
                s_name = f"source{source_id}_name"
                if s_en in self.capabilities:
                    if self.capabilities[s_en] == "No":
                        sources[source_id] = None
                    else:
                        sources[source_id] = self.capabilities[s_name]
                        source_list.append(self.capabilities[s_name])
            _LOGGER.debug("Sources discovered: %s", ",".join(source_list))
        except Exception as exception:
            _LOGGER.debug("Error fetching capabilities: %s", exception)
            raise UpdateFailed() from exception
        return sources

    @property
    def has_zone2(self):
        try:
            _ = self.receiver.zone2_source("?")
            return True
        except ValueError:
            return False
