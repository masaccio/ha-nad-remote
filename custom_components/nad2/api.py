"""Sample API Client."""
import logging
from asyncio import TimeoutError
from async_timeout import timeout

from zeroconf import Zeroconf, ServiceStateChange, IPVersion
from zeroconf.asyncio import (
    AsyncServiceBrowser,
    AsyncServiceInfo,
    AsyncZeroconf,
)

API_TIMEOUT = 10
DISCOVERY_TIMEOUT = 5


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NADApiClient:
    def __init__(self, ip_address: str = None) -> None:
        """Sample API Client."""
        _LOGGER.debug("API init")
        self._ip_address = ip_address

    async def async_get_data(self) -> dict:
        """Get tank data from the API"""
        try:
            async with timeout(API_TIMEOUT):
                pass
        # except APIError as e:
        #     _LOGGER.error("API error connectiong to %s: %s", self.ip_address, str(e))
        except TimeoutError:
            _LOGGER.error("Timeout error connecting to %s", self.ip_address)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Unhandled error connecting to %s: %s", self.ip_address, e)

    def service_change_hander(
        self,
        zeroconf: Zeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        _LOGGER.debug(
            "Service %s of type %s state changed: %s", name, service_type, state_change
        )
        self._ip_address = "DISCOVER"

    async def async_autodiscover(self):
        try:
            _LOGGER.debug("Starting auto-discovery")
            async with timeout(DISCOVERY_TIMEOUT):
                aio_zeroconf = await AsyncZeroconf(ip_version=IPVersion.V4Only)
                browser = await AsyncServiceBrowser(
                    aio_zeroconf.zeroconf,
                    ["_telnet._tcp.local."],
                    handlers=[self.service_change_hander],
                )
                # await asyncio.sleep(5)
                # browser.async_cancel()
                # aio_zeroconf.async_close()
                return "foo"
        except TimeoutError:
            _LOGGER.error("Timeout error in auto-discovery")
