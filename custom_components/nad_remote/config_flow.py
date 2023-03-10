"""Adds config flow for NAD Amplifer remote control."""
import logging
import re
import socket

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
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
            description="NAD Amplifer Remote",
            data={
                CONF_NAME: self._name,
                CONF_HOST: self._host,
                CONF_PORT: self._port,
            },
        )

    async def _set_uid_and_abort(self):
        await self.async_set_unique_id(self._unique_id)
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_NAME: self._name,
            }
        )

    def _discovered_hostname(self, discovery_info: DiscoveryInfoType) -> str:
        """Return the hostname or IP address of the discovered device"""
        hostname = discovery_info.hostname[:-1]
        try:
            socket.gethostbyname(hostname)
            return hostname
        except socket.gaierror:
            # Fallback on IP address
            return discovery_info.addresses[0]

    def _discovered_service_name(self, discovery_info: DiscoveryInfoType) -> str:
        """Return the name of the discovered device"""
        if "." in discovery_info.name:
            return discovery_info.name.split(".")[0]
        else:
            return discovery_info.name

    def _config_schema(self):
        return vol.Schema(
            {
                vol.Optional(
                    CONF_NAME, description="Name of the NAD receiver", default=self._name
                ): str,
                vol.Required(
                    CONF_HOST, description="Hostname of the NAD receiver", default=self._host
                ): str,
                vol.Required(
                    CONF_PORT, description="Port number for the NAD received", default=self._port
                ): int,
            }
        )

    async def _async_check_connection(self, host: str, port: int) -> bool:
        """Return true if host is a NAD amplifier"""
        try:
            api = NADApiClient(host, port)
            model = api.get_model()
            if model is not None:
                return True
            else:
                _LOGGER.warning("'%s' is not a NAD amplifier", host)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.warning("connection check failed: %s", e)
        return False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            # Validate user input
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._name = user_input[CONF_NAME]
            valid = await self._async_check_connection(self._host, self._port)
            if valid:
                _LOGGER.debug(
                    "created media player '%s' for %s:%d", self._name, self._host, self._port
                )
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
            else:
                _LOGGER
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=self._config_schema(),
            errors={},
        )

    async def async_step_zeroconf(self, discovery_info: DiscoveryInfoType) -> FlowResult:
        """Handle a flow initialized by Zeroconf discovery."""
        if discovery_info is None:
            return self.async_abort(reason="cannot_connect")

        self._host = self._discovered_hostname(discovery_info)
        self._name = self._discovered_service_name(discovery_info)
        # Remove hex id, for example 'NAD T758 (98FDE018)'
        self._name = re.sub(r"\s+\(\w+\)", "", self._name)
        self._port = discovery_info.port
        self._unique_id = format_mac(discovery_info.addresses[-1])

        # # Abort if this device has already been configured
        # self._async_abort_entries_match({CONF_HOST: self._host, CONF_NAME: self._name})

        _LOGGER.debug(
            "discovered device: host=%s, port=%s, name=%s, unique_id=%s",
            self._host,
            self._port,
            self._name,
            self._unique_id,
        )

        await self._set_uid_and_abort()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user-confirmation of discovered node."""
        errors = {}
        if user_input is not None:
            try:
                valid = await self._async_check_connection(self._host, self._port)
                if valid:
                    return self._async_get_entry()
                else:
                    errors["base"] = "cannot_connect"
                    return self.async_abort(reason="cannot_connect")
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.error("error getting receiver model for host %s: %s", self._host, e)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={CONF_NAME: self._name},
            data_schema=self._config_schema(),
            errors=errors,
        )
