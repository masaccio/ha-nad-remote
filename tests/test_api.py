"""Tests for NAD Home Assistant API."""

import asyncio
import pytest

from datetime import timezone
from unittest.mock import patch, MagicMock

from homeassistant.components.media_player import MediaPlayerState
from custom_components.nad_remote.api import NADApiClient
from custom_components.nad_remote.const import ZONE2_NAME, MAIN_NAME
from .const import MOCK_HOSTNAME, MOCK_MODEL, MOCK_MODEL, MOCK_STATUS_ALL, MOCK_STATUS_ONE_ZONE

MOCK_RX_STATE = {
    "main_mute": "Off",
    "main_power": "Off",
    "main_volume": -30.0,
    "zone2_mute": "Off",
    "zone2_power": "Off",
    "zone2_volume": -30.0,
    "main_source": 1,
    "zone2_source": 1,
    "main_listeningmode": "Stereo",
}


def mock_rx_func(name: str, op: str, arg: str):
    if op == "?":
        return MOCK_RX_STATE[name]
    else:
        MOCK_RX_STATE[name] = arg


def mock_main_mute(op: str, arg: str = None):
    return mock_rx_func("main_mute", op, arg)


def mock_zone2_mute(op: str, arg: str = None):
    return mock_rx_func("zone2_mute", op, arg)


def mock_main_power(op: str, arg: str = None):
    return mock_rx_func("main_power", op, arg)


def mock_zone2_power(op: str, arg: str = None):
    return mock_rx_func("zone2_power", op, arg)


def mock_main_source(op: str, arg: str = None):
    return mock_rx_func("main_source", op, arg)


def mock_main_volume(op: str, arg: str = None):
    return mock_rx_func("main_volume", op, arg)


def mock_main_listeningmode(op: str, arg: str = None):
    return mock_rx_func("main_listeningmode", op, arg)


def mock_zone2_source(op: str, arg: str = None):
    return mock_rx_func("zone2_source", op, arg)


def mock_zone2_volume(op: str, arg: str = None):
    return mock_rx_func("zone2_volume", op, arg)


MOCK_MAP = {
    "main_model": MagicMock(return_value=MOCK_MODEL),
    "main_mute": MagicMock(side_effect=mock_main_mute),
    "main_power": MagicMock(side_effect=mock_main_power),
    "main_source": MagicMock(side_effect=mock_main_source),
    "main_volume": MagicMock(side_effect=mock_main_volume),
    "main_listeningmode": MagicMock(side_effect=mock_main_listeningmode),
    "zone2_mute": MagicMock(side_effect=mock_zone2_mute),
    "zone2_power": MagicMock(side_effect=mock_zone2_power),
    "zone2_source": MagicMock(side_effect=mock_zone2_source),
    "zone2_volume": MagicMock(side_effect=mock_zone2_volume),
}


@pytest.mark.asyncio
async def test_api(hass):
    """Test API calls."""
    with patch.multiple(
        "custom_components.nad_remote.nad_receiver.NADReceiverTelnet",
        status_all=MagicMock(return_value=MOCK_STATUS_ALL),
        **MOCK_MAP
    ):
        api = NADApiClient(MOCK_HOSTNAME, 23)
        assert api.get_model() == MOCK_MODEL
        assert round(api.get_volume_level(MAIN_NAME), 1) == 0.6
        assert round(api.get_volume_level(ZONE2_NAME), 1) == 0.6
        api.set_volume_level(MAIN_NAME, 0.5)
        api.set_volume_level(ZONE2_NAME, 0.5)
        assert round(api.get_volume_level(MAIN_NAME), 1) == 0.5
        assert round(api.get_volume_level(ZONE2_NAME), 1) == 0.5
        assert api.muted(MAIN_NAME) == False
        assert api.muted(ZONE2_NAME) == False
        api.mute(MAIN_NAME, True)
        api.mute(ZONE2_NAME, True)
        assert api.muted(MAIN_NAME) == True
        assert api.muted(ZONE2_NAME) == True
        assert api.get_power_state(MAIN_NAME) == MediaPlayerState.OFF
        assert api.get_power_state(ZONE2_NAME) == MediaPlayerState.OFF
        api.power(MAIN_NAME, MediaPlayerState.ON)
        api.power(ZONE2_NAME, MediaPlayerState.ON)
        assert api.get_power_state(MAIN_NAME) == MediaPlayerState.ON
        assert api.get_power_state(ZONE2_NAME) == MediaPlayerState.ON
        assert api.get_source(MAIN_NAME) == "Test Source 1"
        assert api.get_source(ZONE2_NAME) == "Test Source 1"
        api.set_source(MAIN_NAME, "Test Source 2")
        api.set_source(ZONE2_NAME, "Test Source 2")
        assert api.get_source(MAIN_NAME) == "Test Source 2"
        assert api.get_source(ZONE2_NAME) == "Test Source 2"

    # def get_listening_mode(self, zone: str) -> str | None:
    # def set_listening_mode(self, zone: str, mode: str) -> None:


@pytest.mark.asyncio
async def test_api_single_zone(hass):
    """Test API calls."""
    with patch.multiple(
        "custom_components.nad_remote.nad_receiver.NADReceiverTelnet",
        status_all=MagicMock(return_value=MOCK_STATUS_ONE_ZONE),
        **MOCK_MAP
    ):
        api = NADApiClient(MOCK_HOSTNAME, 23)
        assert api.get_model() == MOCK_MODEL
        api.set_volume_level(MAIN_NAME, 0.5)
        assert round(api.get_volume_level(MAIN_NAME), 1) == 0.5
        api.mute(MAIN_NAME, True)
        assert api.muted(MAIN_NAME) == True
        api.power(MAIN_NAME, MediaPlayerState.ON)
        assert api.get_power_state(MAIN_NAME) == MediaPlayerState.ON
        api.set_source(MAIN_NAME, "Test Source 1")
        assert api.get_source(MAIN_NAME) == "Test Source 1"
