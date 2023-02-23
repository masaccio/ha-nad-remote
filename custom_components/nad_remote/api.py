"""NAD Amplifiler API Client for Home Assistant"""
import logging
import re
import sys
from typing import Tuple

_LOGGER: logging.Logger = logging.getLogger(__package__)

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_MAX_VOLUME, DEFAULT_MIN_VOLUME, DOMAIN, MAIN_NAME, ZONE2_NAME

# Use local implementation of NAD client rather than upstream
from .nad_receiver import NADReceiverTelnet


class NADApiClient:
    def __init__(self, host: str, port: int) -> None:
        """NAD API Client."""
        self._host = host
        self._port = port
        self._receiver = NADReceiverTelnet(host, port)
        self._capabilities = self.get_capabilities()
        _ = self.get_sources()
        self._source_name_to_id = {v: k for k, v in self._sources.items()}
        self._volume_range = {}
        self._volume_range[MAIN_NAME] = self.volume_range(MAIN_NAME)
        if self.has_zone2:
            self._volume_range[ZONE2_NAME] = self.volume_range(ZONE2_NAME)
        _LOGGER.debug("self._volume_range=%s", self._volume_range)

    def get_model(self):
        try:
            response = self._receiver.main_model("?")
            if not re.match(r"^\w+\d+", response):
                _LOGGER.debug("Amplifier model '%s' not recognised", response)
                return None
            else:
                _LOGGER.debug("Amplifier model='%s'", response)
                return response
        except Exception as e:
            _LOGGER.error("Error checking amplifier model: %s", e)

    def get_capabilities(self) -> dict | None:
        """Fetch status of amplifier to get capabilities"""
        if hasattr(self, "_capabilities"):
            return self._capabilities
        try:
            self._capabilities = self._receiver.status_all()
            if self._capabilities is None:
                _LOGGER.error("Error fetching amplifier capabilities: no reuslts")
            return self._capabilities
        except Exception as e:
            _LOGGER.error("Error fetching amplifier capabilities: %s", e)

    def get_sources(self) -> dict | None:
        """Discover list of sources"""
        if not hasattr(self, "_sources"):
            try:
                self._sources = {}
                for source_id in range(1, 20):
                    s_en = f"source{source_id}_enabled"
                    s_name = f"source{source_id}_name"
                    if s_en in self._capabilities:
                        if self._capabilities[s_en] == "No":
                            self._sources[source_id] = None
                        else:
                            self._sources[source_id] = self._capabilities[s_name]
            except Exception as e:
                _LOGGER.error("Error fetching capabilities: %s", e)

        source_list = [v for k, v in self._sources.items() if v is not None]
        _LOGGER.debug("get_sources sources=%s", source_list)
        return source_list

    def volume_to_ha(self, zone: str, volume: float) -> float:
        volume_range = self._volume_range[zone][1] - self._volume_range[zone][0]
        volume_min = self._volume_range[zone][0]
        return abs(volume - volume_min) / volume_range

    def volume_from_ha(self, zone: str, volume: float) -> float:
        volume_range = self._volume_range[zone][1] - self._volume_range[zone][0]
        volume_min = self._volume_range[zone][0]
        return volume * volume_range - volume_min

    @property
    def has_zone2(self) -> bool:
        try:
            _ = self._receiver.zone2_source("?")
            return True
        except ValueError:
            return False

    def get_power_state(self, zone: str) -> str:
        if zone == ZONE2_NAME:
            status = self._receiver.zone2_power("?")
        else:
            status = self._receiver.main_power("?")
        if status == "On":
            _LOGGER.debug("ON: state: zone=%s, status=%s", zone, status)
            return STATE_ON
        elif status == "Off":
            _LOGGER.debug("OFF: state: zone=%s, status=%s", zone, status)
            return STATE_OFF
        else:
            _LOGGER.warning("UNKNOWN: state: zone=%s, status=%s", zone, status)
            return STATE_UNKNOWN

    def get_source(self, zone: str) -> str | None:
        try:
            if zone == ZONE2_NAME:
                source = self._receiver.zone2_source("?")
            else:
                source = self._receiver.main_source("?")
            if source is not None and source in self._sources:
                _LOGGER.debug("get_source: zone='%s' source='%s'", zone, self._sources[source])
                return self._sources[source]
            else:
                _LOGGER.error("get_source: zone='%s', unknown source '%s'", zone, source)
        except Exception as e:
            _LOGGER.error("source: error: %s", e)

    def set_source(self, zone: str, source: str) -> None:
        try:
            if source is None or source not in self._source_name_to_id:
                _LOGGER.error("zone '%s' unknown source in selected '%s'", zone, source)
                return None
            _LOGGER.debug("set_source: zone='%s' source='%s'", zone, source)
            if zone == ZONE2_NAME:
                source = self._receiver.zone2_source("=", self._source_name_to_id[source])
            else:
                source = self._receiver.main_source("=", self._source_name_to_id[source])
        except Exception as e:
            _LOGGER.error("power: error: %s", e)

    def power(self, zone: str, state: str) -> None:
        try:
            _LOGGER.debug("power: zone=%s, state=%s", zone, state)
            if zone == ZONE2_NAME:
                if state == STATE_ON:
                    self._receiver.zone2_power("=", "On")
                else:
                    self._receiver.zone2_power("=", "Off")
            else:
                if state == STATE_ON:
                    self._receiver.main_power("=", "On")
                else:
                    self._receiver.main_power("=", "Off")
        except Exception as e:
            _LOGGER.error("power: error: %s", e)

    def get_volume_level(self, zone: str) -> float:
        try:
            if zone == ZONE2_NAME:
                status = self._receiver.zone2_volume("?")
            else:
                status = self._receiver.main_volume("?")
            volume = self.volume_to_ha(zone, float(status))
            _LOGGER.debug("get_volume_level: zone=%s, dB=%s, ha-volume=%s", zone, status, volume)
        except Exception as e:
            _LOGGER.error("get_volume_level: error: %s", e)

    def set_volume_level(self, zone: str, volume: float) -> None:
        try:
            if zone == ZONE2_NAME:
                status = self._receiver.zone2_volume("=", self.volume_from_ha(zone, volume))
            else:
                status = self._receiver.main_volume("=", self.volume_from_ha(zone, volume))
            _LOGGER.debug("set_volume_level: zone=%s, dB=%s, ha-volume=%s", zone, status, volume)
        except Exception as e:
            _LOGGER.error("set_volume_level: error: %s", e)

    def muted(self, zone: str) -> bool:
        try:
            if zone == ZONE2_NAME:
                status = self._receiver.zone2_mute("?")
            else:
                status = self._receiver.main_mute("?")
            _LOGGER.debug("is_volume_muted: zone=%s, mute=%s", zone, status)
            if status == "Off":
                return False
            else:
                return True
        except Exception as e:
            _LOGGER.error("is_volume_muted: error: %s", e)

    def mute(self, zone: str, mute: bool) -> bool:
        try:
            if zone == ZONE2_NAME:
                status = self._receiver.zone2_mute("=", "On" if mute else "Off")
            else:
                status = self._receiver.main_mute("=", "On" if mute else "Off")
            _LOGGER.debug("mute: zone=%s, mute=%s", zone, mute)
        except Exception as e:
            _LOGGER.error("mute: error: %s", e)

    def volume_range(self, zone: str) -> Tuple[int, int]:
        try:
            capabilities = self.get_capabilities()
            if zone == ZONE2_NAME:
                min_vol = self._capabilities.get("zone2_volume_min", DEFAULT_MIN_VOLUME)
                max_vol = self._capabilities.get("zone2_volume_max", DEFAULT_MAX_VOLUME)
            else:
                min_vol = self._capabilities.get("main_volume_min", DEFAULT_MIN_VOLUME)
                max_vol = self._capabilities.get("main_volume_max", DEFAULT_MAX_VOLUME)
            _LOGGER.debug("volume_range: min=%s, max=%s", min_vol, max_vol)
            return (float(min_vol), float(max_vol))
        except Exception as e:
            _LOGGER.error("Error fetching capabilities: %s", e)
            raise UpdateFailed() from e
