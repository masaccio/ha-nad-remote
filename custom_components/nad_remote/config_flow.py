"""Adds config flow for NAD Amplifer remote control."""
import logging
import re
import socket

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.typing import DiscoveryInfoType

from .api import NADApiClient
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class NADFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for nad_remote."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._host = None
        self._port = None
        self._errors = {}

    @callback
    def _async_get_entry(self):
        return self.async_create_entry(
            title=self._name,
            data={
                CONF_NAME: self._name,
                CONF_HOST: self._host,
                CONF_PORT: self._port,
            },
        )

    async def _set_uid_and_abort(self):
        if not hasattr(self, "_unique_id"):
            _LOGGER.warning("Device already exists but no config defined")
            return False

        await self.async_set_unique_id(self._unique_id)
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_NAME: self._name,
            }
        )

    def _discovered_hostname(self, discovery_info: DiscoveryInfoType) -> str:
        """return the hostname or IP address of the discovered device"""
        hostname = discovery_info.hostname[:-1]
        try:
            socket.gethostbyname(hostname)
            return hostname
        except socket.gaierror:
            # Fallback on IP address
            return discovery_info.addresses[0]

    async def async_step_zeroconf(self, discovery_info: DiscoveryInfoType):
        """Handle zeroconf discovery."""
        _LOGGER.debug("Initiating zeroconf discovery")
        if discovery_info is None:
            return self.async_abort(reason="cannot_connect")

        self._host = self._discovered_hostname(discovery_info)
        self._port = discovery_info.port
        self._name = re.sub(r"[.]_telnet.*", "", discovery_info.name)

        # Abort if this device has already been configured
        self._async_abort_entries_match({CONF_HOST: self._host})

        _LOGGER.debug("Zeroconf: addresses=%s", discovery_info.addresses)
        if len(discovery_info.addresses) < 2:
            _LOGGER.error("No MAC address found: addresses=%s", discovery_info.addresses)
            self._unique_id = None
        else:
            self._unique_id = format_mac(discovery_info.addresses[1])

        _LOGGER.debug(
            "Zeroconf discovery info: host=%s, port=%s, name=%s, unique_id=%s",
            self._host,
            self._port,
            self._name,
            self._unique_id,
        )

        await self._set_uid_and_abort()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input=None):
        """Handle user-confirmation of discovered node."""
        _LOGGER.debug("Confirming discovery user_input=%s", user_input)
        if user_input is not None:
            try:
                _LOGGER.debug("Confirming discovery information")
                valid = await self._async_check_connection(self._host, self._port)
                if valid:
                    _LOGGER.debug("Successful connection to %s", self._name)
                    return self._async_get_entry()
                else:
                    return self.async_abort(reason="cannot_connect")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception checking NAD connection")
                self._errors["base"] = "unknown"

        return self.async_show_form(
            step_id="discovery_confirm", description_placeholders={"name": self._name}, errors={}
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        _LOGGER.debug("User step started: user_input=%s", user_input)

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._name = user_input[CONF_NAME]
            _LOGGER.debug("User step testing connection: host=%s", self._host)
            valid = await self._async_check_connection(self._host, self._port)
            if valid:
                _LOGGER.debug("Successful connection to %s", self._name)
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
            else:
                self._errors["base"] = "connection"

        # if not errors:
        #     await self._set_uid_and_abort()
        #     return self._async_get_entry()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_HOST): cv.string,
                    vol.Required(CONF_PORT, default=23): cv.positive_int,
                }
            ),
            errors=errors,
        )

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     return NADOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        _LOGGER.debug("Show config form: user_input=%s", user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str, vol.Required(CONF_PORT): str}),
            errors=self._errors,
        )

    async def _async_check_connection(self, host: str, port: int):
        """Return true if credentials is valid."""
        try:
            _LOGGER.debug("Checking connection to amplifier: host=%s port=%s", host, port)
            api = NADApiClient(host, port)
            model = await api.async_get_model()
            if model is not None:
                _LOGGER.debug("Amplifier model=%s", model)
                return True
            else:
                _LOGGER.error("Amplifier model not supported")
                return False
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.warning("Connection check failed: %s", e)
        return False


# class NADOptionsFlowHandler(config_entries.OptionsFlow):
#     """Config flow options handler for nad_remote."""

#     def __init__(self, config_entry):
#         """Initialize HACS options flow."""
#         self.config_entry = config_entry
#         self.options = dict(config_entry.options)

#     async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
#         """Manage the options."""
#         return await self.async_step_user()

#     async def async_step_user(self, user_input=None):
#         """Handle a flow initialized by the user."""
#         if user_input is not None:
#             self.options.update(user_input)
#             return await self._update_options()

#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required(x, default=self.options.get(x, True)): bool
#                     for x in sorted(PLATFORMS)
#                 }
#             ),
#         )

#     async def _update_options(self):
#         """Update config entry options."""
#         return self.async_create_entry(
#             title=self.config_entry.data.get(CONF_HOST), data=self.options
#         )