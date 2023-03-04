"""
Custom integration to integrate NAD Amplifer remote control with Home Assistant.

For more details about this integration, please refer to
https://github.com/masaccio/nad_remote
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.components.media_player import MediaPlayerState
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NADApiClient
from .const import DOMAIN, SCAN_INTERVAL, MAIN_NAME, ZONE2_NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    try:
        api = NADApiClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    except Exception as e:
        raise ConfigEntryNotReady(f"NAD API initialisation failed: {e}") from e

    coordinator = NADDataUpdateCoordinator(hass, client=api)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, platform))

    entry.add_update_listener(async_reload_entry)
    return True


class NADDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NADApiClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []
        self.power_state = {}
        self.volume_level = {}
        self.source = None
        self.source_list = {}
        self.volume_level = {}
        self.is_volume_muted = {}
        self.sound_mode = None
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via API."""
        try:
            _LOGGER.debug("updating data via coordinator")
            if self.api.has_zone2:
                zones = [MAIN_NAME, ZONE2_NAME]
            else:
                zones = [MAIN_NAME]
            update = False
            for zone in zones:
                self.power_state[zone] = self.api.get_power_state(zone)
                if self.power_state[zone] == MediaPlayerState.ON:
                    update = True
                    self.volume_level[zone] = self.api.get_volume_level(zone)
                    self.is_volume_muted[zone] = self.api.muted(zone)
            if update:
                self.source_list = self.api.get_sources()
                self.source = self.api.get_source(MAIN_NAME)
                self.sound_mode = self.api.get_listening_mode(MAIN_NAME)
            return self
        except Exception as e:
            _LOGGER.error("Error updating state: %s", e)
            raise UpdateFailed() from e


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
