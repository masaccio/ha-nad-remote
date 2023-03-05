"""Tests for NAD Home Assistant API."""

import asyncio
import pytest

from datetime import timezone
from unittest.mock import MagicMock, patch

from custom_components.nad_remote.api import NADApiClient
from .const import MOCK_HOSTNAME, MOCK_MODEL


from .const import MOCK_MODEL, MOCK_STATUS_ALL

MOCK_RX_STATE = {
    "main_mute": "Off",
    "main_power": "Off",
    "main_volume": -30,
    "zone2_mute": "Off",
    "zone2_power": "Off",
    "zone2_volume": -30,
    "main_source": "Test Source 1",
    "zone2_source": "Test Source 1",
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


# with patch("custom_components.nad_remote.nad_receiver.NADReceiverTelnet") as mock_rx:
# with patch("custom_components.nad_remote.api.NADApiClient.NADReceiverTelnet") as mock_rx:


@pytest.mark.asyncio
@patch.multiple(
    "custom_components.nad_remote.nad_receiver.NADReceiverTelnet",
    main_model=MagicMock(return_value=MOCK_MODEL),
    status_all=MagicMock(return_value=MOCK_STATUS_ALL),
    main_mute=MagicMock(side_effect=mock_main_mute),
    main_power=MagicMock(side_effect=mock_main_power),
    main_source=MagicMock(side_effect=mock_main_source),
    main_volume=MagicMock(side_effect=mock_main_volume),
    main_listeningmode=MagicMock(side_effect=mock_main_listeningmode),
    zone2_mute=MagicMock(side_effect=mock_zone2_mute),
    zone2_power=MagicMock(side_effect=mock_zone2_power),
    zone2_source=MagicMock(side_effect=mock_zone2_source),
    zone2_volume=MagicMock(side_effect=mock_zone2_volume),
)
async def test_api(hass):
    """Test API calls."""
    api = NADApiClient(MOCK_HOSTNAME, 23)
    assert api.get_model() == MOCK_MODEL
