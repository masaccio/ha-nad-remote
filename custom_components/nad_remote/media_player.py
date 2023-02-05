"""Media Player Platform for NAD Remote"""
import logging
from datetime import timedelta

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_MAX_VOLUME, CONF_MIN_VOLUME
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
        zones = ["Main", "Zone2"]
    else:
        zones = ["Main"]
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
        super().__init__(coordinator, config_entry)

        self._source_dict = coordinator.api.get_sources()
        self._reverse_mapping = {value: key for key, value in self._source_dict.items()}

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data.get("name") + " [" + self.zone + "]"

    def turn_off(self) -> None:
        """Turn the media player off."""
        self.coordinator.receiver.main_power("=", "Off")

    def turn_on(self) -> None:
        """Turn the media player on."""
        self.coordinator.receiver.main_power("=", "On")

    def volume_up(self) -> None:
        """Volume up the media player."""
        self.coordinator.receiver.main_volume("+")

    def volume_down(self) -> None:
        """Volume down the media player."""
        self.coordinator.receiver.main_volume("-")


# """Support for interfacing with NAD receivers through Telnet"""

# # This must be reimplemented -- origincal is Apache


# from __future__ import annotations

# import homeassistant.helpers.config_validation as cv
# import voluptuous as vol
# from homeassistant.components.media_player import (
#     PLATFORM_SCHEMA,
#     MediaPlayerDeviceClass,
#     MediaPlayerEntity,
#     MediaPlayerEntityFeature,
#     MediaPlayerState,
# )
# from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# from nad_receiver import NADReceiver, NADReceiverTCP, NADReceiverTelnet
# from .entity import NADEntity

# DEFAULT_NAME = "NAD Receiver"
# DEFAULT_MIN_VOLUME = -92
# DEFAULT_MAX_VOLUME = -20
# DEFAULT_VOLUME_STEP = 4


# CONF_MIN_VOLUME = "min_volume"
# CONF_MAX_VOLUME = "max_volume"
# CONF_VOLUME_STEP = "volume_step"  # for NADReceiverTCP
# CONF_SOURCE_DICT = "sources"  # for NADReceiver

# # Max value based on a C658 with an MDC HDM-2 card installed
# SOURCE_DICT_SCHEMA = vol.Schema({vol.Range(min=1, max=12): cv.string})

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Optional(CONF_HOST): cv.string,
#         vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
#         vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#         vol.Optional(CONF_MIN_VOLUME, default=DEFAULT_MIN_VOLUME): int,
#         vol.Optional(CONF_MAX_VOLUME, default=DEFAULT_MAX_VOLUME): int,
#         vol.Optional(CONF_SOURCE_DICT, default={}): SOURCE_DICT_SCHEMA,
#         vol.Optional(CONF_VOLUME_STEP, default=DEFAULT_VOLUME_STEP): int,
#     }
# )


# class NAD(NADEntity, MediaPlayerEntity):
#     """NAD Receiver Entity"""

#     _attr_icon = "mdi:speaker-multiple"
#     _attr_device_class = MediaPlayerDeviceClass.RECEIVER
#     _attr_supported_features: MediaPlayerEntityFeature = (
#         MediaPlayerEntityFeature.VOLUME_SET
#         | MediaPlayerEntityFeature.VOLUME_MUTE
#         | MediaPlayerEntityFeature.VOLUME_STEP
#         | MediaPlayerEntityFeature.TURN_ON
#         | MediaPlayerEntityFeature.TURN_OFF
#         | MediaPlayerEntityFeature.SELECT_SOURCE
#         | MediaPlayerEntityFeature.SELECT_SOUND_MODE
#     )

#     def __init__(self, coordinator: DataUpdateCoordinator, node: NexaNode):
#         _LOGGER.info("Found media player %s: %s", node.id, node.name)
#         super().__init__(node, coordinator)
#         self.id = node.id
#         self._attr_native_value = None
#         self._attr_unique_id = f"media_player_{node.id}"
#         self._attr_name = node.name or node.id

#     def turn_off(self) -> None:
#         """Turn the media player off."""
#         self.coordinator.main_power("=", "Off")

#     def turn_on(self) -> None:
#         """Turn the media player on."""
#         self.coordinator.main_power("=", "On")

#     def volume_up(self) -> None:
#         """Volume up the media player."""
#         self.coordinator.main_volume("+")

#     def volume_down(self) -> None:
#         """Volume down the media player."""
#         self.coordinator.main_volume("-")

#     def set_volume_level(self, volume: float) -> None:
#         """Set volume level, range 0..1."""
#         self.coordinator.main_volume("=", self.calc_db(volume))

#     def mute_volume(self, mute: bool) -> None:
#         """Mute (true) or unmute (false) media player."""
#         if mute:
#             self.coordinator.main_mute("=", "On")
#         else:
#             self.coordinator.main_mute("=", "Off")

#     def select_source(self, source: str) -> None:
#         """Select input source."""
#         self.coordinator.main_source("=", self._reverse_mapping.get(source))

#     @property
#     def source_list(self):
#         """List of available input sources."""
#         return sorted(self._reverse_mapping)

#     @property
#     def available(self) -> bool:
#         """Return if device is available."""
#         return self.state is not None

#     def update(self) -> None:
#         """Retrieve latest state."""
#         power_state = self.coordinator.main_power("?")
#         if not power_state:
#             self._attr_state = None
#             return
#         self._attr_state = (
#             MediaPlayerState.ON
#             if self.coordinator.main_power("?") == "On"
#             else MediaPlayerState.OFF
#         )

#         if self.state == MediaPlayerState.ON:
#             self._attr_is_volume_muted = self.coordinator.main_mute("?") == "On"
#             volume = self.coordinator.main_volume("?")
#             # Some receivers cannot report the volume, e.g. C 356BEE,
#             # instead they only support stepping the volume up or down
#             self._attr_volume_level = self.calc_volume(volume) if volume is not None else None
#             self._attr_source = self._source_dict.get(self.coordinator.main_source("?"))

#     def calc_volume(self, decibel):
#         """
#         Calculate the volume given the decibel.

#         Return the volume (0..1).
#         """
#         return abs(self._min_volume - decibel) / abs(self._min_volume - self._max_volume)

#     def calc_db(self, volume):
#         """
#         Calculate the decibel given the volume.

#         Return the dB.
#         """
#         return self._min_volume + round(abs(self._min_volume - self._max_volume) * volume)
