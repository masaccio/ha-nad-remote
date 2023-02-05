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

from .const import DOMAIN, CONF_MAX_VOLUME, CONF_MIN_VOLUME, MAIN_NAME, ZONE2_NAME
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
    _LOGGER.debug("NAD media player zones: %s", ",".join(zones))
    entities = [NADPlayer(zone, coordinator, config_entry) for zone in zones]
    async_add_entities(entities)


class NADPlayer(NADEntity, MediaPlayerEntity):
    """NAD Receiver Entity"""

    _attr_icon = "mdi:speaker-multiple"
    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features: MediaPlayerEntityFeature = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )

    def __init__(self, zone: str, coordinator: DataUpdateCoordinator, config_entry: ConfigEntry):
        self.zone = zone
        self.coordinator = coordinator
        self.config_entry = config_entry
        self.zone = zone
        self._update_success = True
        super().__init__(coordinator, config_entry)

        self._source_dict = coordinator.api.get_sources()
        self._reverse_mapping = {value: key for key, value in self._source_dict.items()}

    @property
    def name(self):
        return self.unique_id

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data.get("name") + " [" + self.zone + "]"

    def __getattr__(self, attr):
        if self.zone == MAIN_NAME:
            _LOGGER.debug("main zone undefined funxtion attr=%s", attr)
        raise AttributeError()

    @property
    def state(self):
        if self.zone == ZONE2_NAME:
            status = self.coordinator.api.receiver.zone2_power("?")
        else:
            status = self.coordinator.api.receiver.main_power("?")
        if status == "On":
            _LOGGER.debug("ON: state: zone=%s, status=%s", self.zone, status)
            return STATE_ON
        elif status == "Off":
            _LOGGER.debug("OFF: state: zone=%s, status=%s", self.zone, status)
            return STATE_OFF
        else:
            _LOGGER.debug("UNKNOWN: state: zone=%s, status=%s", self.zone, status)
            return STATE_UNKNOWN

    def update(self) -> None:
        _LOGGER.debug("update zone=%s", self.zone)

    @property
    def source(self) -> str | None:
        try:
            if self.zone == ZONE2_NAME:
                source = self.coordinator.api.receiver.zone2_source("?")
            else:
                source = self.coordinator.api.receiver.main_source("?")
            _LOGGER("Source=%s '%s'", source, self._reverse_mapping[source])
            return self._reverse_mapping[source]
        except Exception as e:
            _LOGGER.debug("source: error: %s", e)

    def select_source(self, source: str) -> None:
        _LOGGER("Set source=%s '%s'", source, self._source_dict[source])
        if self.zone == ZONE2_NAME:
            source = self.coordinator.api.receiver.zone2_source("=", self._source_dict[source])
        else:
            source = self.coordinator.api.receiver.main_source("=", self._source_dict[source])

    def turn_off(self) -> None:
        """Turn the media player off."""
        self.coordinator.api.receiver.main_power("=", "Off")

    def turn_on(self) -> None:
        """Turn the media player on."""
        self.coordinator.api.receiver.main_power("=", "On")

    @property
    def volume_level(self) -> float | None:
        try:
            if self.zone == ZONE2_NAME:
                status = self.coordinator.api.receiver.zone2_volume("?")
            else:
                status = self.coordinator.api.receiver.main_volume("?")
            _LOGGER.debug("volume_level: zone=%s, volume=%s", self.zone, status)
            return float(status)
        except Exception as e:
            _LOGGER.debug("volume_level: error: %s", e)

    @property
    def is_volume_muted(self) -> bool | None:
        try:
            if self.zone == ZONE2_NAME:
                status = self.coordinator.api.receiver.zone2_mute("?")
            else:
                status = self.coordinator.api.receiver.main_mute("?")
            _LOGGER.debug("is_volume_muted: zone=%s, mute=%s", self.zone, status)
            if status == "Off":
                return False
            else:
                return True
        except Exception as e:
            _LOGGER.debug("is_volume_muted: error: %s", e)

    def volume_up(self) -> None:
        """Volume up the media player."""
        if self.zone == ZONE2_NAME:
            self.coordinator.api.receiver.zone2_volume("+")
        else:
            self.coordinator.api.receiver.main_volume("-")

    def volume_down(self) -> None:
        """Volume down the media player."""
        if self.zone == ZONE2_NAME:
            self.coordinator.api.receiver.zone2_volume("-")
        else:
            self.coordinator.api.receiver.main_volume("-")
