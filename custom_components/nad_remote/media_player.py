"""Media Player Platform for NAD Remote"""
import logging
from datetime import timedelta

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, MAIN_NAME, VOLUME_INCREMENT, ZONE2_NAME
from .entity import NADEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup Media Player platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_config_entry_first_refresh()

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            power_state = self.coordinator.data.power_state[self.zone]
            if power_state == MediaPlayerState.ON:
                self._attr_state = power_state
                self._attr_source = self.coordinator.data.source[self.zone]
                self._attr_source_list = self.coordinator.data.source_list
                self._attr_volume_level = self.coordinator.data.volume_level[self.zone]
                self._attr_is_volume_muted = self.coordinator.data.is_volume_muted[self.zone]
                if self.zone == MAIN_NAME:
                    self._attr_sound_mode = self.coordinator.data.sound_mode
                else:
                    self._attr_sound_mode = None
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.warning("data update failed: zone='%s': %s", self.zone, e)

    async def async_select_source(self, source: str) -> None:
        """Select a source in the receiver"""
        self.coordinator.api.set_source(self.zone, source)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the receiver zone off."""
        self.coordinator.api.power(self.zone, STATE_OFF)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the receiver zone on."""
        self.coordinator.api.power(self.zone, STATE_ON)
        await self.coordinator.async_request_refresh()

    async def async_toggle(self) -> None:
        """Toggle the power on the receiver"""
        state = self.coordinator.api.get_power_state(self.zone)
        if state == STATE_OFF:
            await self.async_turn_on()
        else:
            await self.async_turn_off()

    async def async_set_volume_level(self, volume: float) -> None:
        self.coordinator.api.set_volume_level(self.zone, volume)
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Toggle the mute setting"""
        self.coordinator.api.mute(self.zone, not self.is_volume_muted)
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Volume up the media player."""
        volume_level = min(0.0, self.volume_level - VOLUME_INCREMENT)
        await self.set_volume_level(volume_level)
        await self.coordinator.async_request_refresh()

    async def async_volume_down(self) -> None:
        """Volume down the media player."""
        volume_level = (self.volume_level + VOLUME_INCREMENT) % 1.0
        await self.set_volume_level(volume_level)
        await self.coordinator.async_request_refresh()

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        await self.coordinator.api.set_listening_mode(self.zone, sound_mode)
        await self.coordinator.async_request_refresh()
