"""
Custom integration to integrate NAD Amplifer remote control with Home Assistant.

For more details about this integration, please refer to
https://github.com/masaccio/nad_remote
"""
import asyncio
import logging
from datetime import timedelta
from dataclasses import dataclass, field

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


@dataclass
class NADState:
    # Dict entry for each available zone
    power_state: dict = field(default_factory=dict)
    source: dict = field(default_factory=dict)
    source_list: dict = field(default_factory=dict)
    is_volume_muted: dict = field(default_factory=dict)
    volume_level: dict = field(default_factory=dict)
    # Sound mode applies to all zones
    sound_mode: str = None


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
        self.model = None
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self) -> NADState:
        """Fetch and cache data from the API"""
        try:
            if 
            if self.api.has_zone2:
                zones = [MAIN_NAME, ZONE2_NAME]
            else:
                zones = [MAIN_NAME]
            update = False
            data = NADState()
            for zone in zones:
                data.power_state[zone] = self.api.get_power_state(zone)
                if data.power_state[zone] == MediaPlayerState.ON:
                    data.volume_level[zone] = self.api.get_volume_level(zone)
                    data.is_volume_muted[zone] = self.api.muted(zone)
                    data.source[zone] = self.api.get_source(MAIN_NAME)
                    update = True
            if update:
                data.source_list = self.api.get_sources()
                data.sound_mode = self.api.get_listening_mode(MAIN_NAME)
            return data
        except Exception as e:
            raise UpdateFailed(f"Error fetching data from API: {e}")


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
