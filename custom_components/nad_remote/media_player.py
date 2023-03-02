"""Media Player Platform for NAD Remote"""
import logging
from datetime import timedelta

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, MAIN_NAME, ZONE2_NAME, VOLUME_INCREMENT
from .entity import NADEntity


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup Media Player platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    if coordinator.api.has_zone2:
        zones = [MAIN_NAME, ZONE2_NAME]
    else:
        zones = [MAIN_NAME]
    _LOGGER.debug("NAD media player zones: %s", ", ".join(zones))
    entities = [NADPlayer(zone, coordinator, config_entry) for zone in zones]
    async_add_entities(entities)


class NADPlayer(NADEntity, MediaPlayerEntity):
    """NAD Receiver Entity"""

    _attr_icon = "mdi:speaker-multiple"
    _attr_device_class = MediaPlayerDeviceClass.RECEIVER

    def __init__(self, zone: str, coordinator: DataUpdateCoordinator, config_entry: ConfigEntry):
        self.zone = zone
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.zone = zone
        super().__init__(coordinator, config_entry)

    @property
    def supported_features(self):
        features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
        if self.zone == MAIN_NAME:
            features |= MediaPlayerEntityFeature.SELECT_SOUND_MODE
        return features

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data.get("name") + " (" + self.zone + ")"

    @property
    def name(self):
        return self.unique_id

    def update(self) -> None:
        self._attr_state = self.coordinator.api.get_power_state(self.zone)
        self._attr_source = self.coordinator.api.get_source(self.zone)

    @property
    def source_list(self) -> list[str] | None:
        """Get a list of available sources for the receiver"""
        return self.coordinator.api.get_sources()

    @property
    def source(self) -> str | None:
        """Get the zone's current source"""
        return self.coordinator.api.get_source(self.zone)

    def select_source(self, source: str) -> None:
        """Select a source in the receiver"""
        self.coordinator.api.set_source(self.zone, source)

    def turn_off(self) -> None:
        """Turn the receiver zone off."""
        self.coordinator.api.power(self.zone, STATE_OFF)

    def turn_on(self) -> None:
        """Turn the receiver zone on."""
        self.coordinator.api.power(self.zone, STATE_ON)

    def toggle(self) -> None:
        """Toggle the power on the receiver"""
        state = self.coordinator.api.get_power_state(self.zone)
        if state == STATE_OFF:
            self.turn_on()
        else:
            self.turn_off()

    @property
    def volume_level(self) -> float | None:
        return self.coordinator.api.get_volume_level(self.zone)

    def set_volume_level(self, volume: float) -> None:
        self.coordinator.api.set_volume_level(self.zone, volume)

    @property
    def is_volume_muted(self) -> bool | None:
        return self.coordinator.api.muted(self.zone)

    def mute_volume(self, mute: bool) -> None:
        """Toggle the mute setting"""
        self.coordinator.api.mute(self.zone, not self.is_volume_muted)

    def volume_up(self) -> None:
        """Volume up the media player."""
        volume_level = min(0.0, self.volume_level - VOLUME_INCREMENT)
        self.set_volume_level(volume_level)

    def volume_down(self) -> None:
        """Volume down the media player."""
        volume_level = (self.volume_level + VOLUME_INCREMENT) % 1.0
        self.set_volume_level(volume_level)

    @property
    def sound_mode(self) -> str | None:
        if self.zone == MAIN_NAME:
            return self.coordinator.api.get_listening_mode(self.zone)
        else:
            return None

    def select_sound_mode(self, sound_mode: str) -> None:
        self.coordinator.api.set_listening_mode(self.zone, sound_mode)
