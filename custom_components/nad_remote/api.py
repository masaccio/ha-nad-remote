"""Sample API Client."""
import logging
import re
from nad_receiver import NADReceiverTelnet


API_TIMEOUT = 10
DISCOVERY_TIMEOUT = 5


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NADApiClient:
    def __init__(self, host: str, port: int) -> None:
        """Sample API Client."""
        _LOGGER.debug("API init: host=%s, port=%s", host, port)
        self._host = host
        self._port = port
        self._receiver = NADReceiverTelnet(host, port)

    async def async_get_model(self):
        try:
            _LOGGER.debug("API get model: host=%s, port=%s", self._host, self._port)
            response = self._receiver.exec_command("main", "model", "?")
            if not re.match(r"^\w+\d+", response):
                _LOGGER.debug("NAD model not recognised model=%s", response)
                return None
            else:
                _LOGGER.debug("API get model: model=%s", response)
                return response
        except Exception as e:
            _LOGGER.error("Timeout error in auto-discovery - %s", e)

    async def async_get_capabilities(self):
        try:
            _LOGGER.debug("API get capabilities")
            response = self._receiver.transport.communicate("?")
            return response
        except Exception as e:
            _LOGGER.error("Error fetching amplifier capabilities- %s", e)

    async def async_get_data(self):
        _LOGGER.debug("async_get_data")
        return True
