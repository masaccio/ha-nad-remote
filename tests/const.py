"""Constants for NAD Amplifer remote control tests."""
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT

MOCK_HOSTNAME = "test_hostname"
MOCK_CONFIG = {CONF_HOST: MOCK_HOSTNAME, CONF_PORT: 9023, CONF_NAME: "NAD Test"}

MOCK_STATUS_ALL = {
    "source1_name": "Test Source 1",
    "source1_enabled": "Yes",
    "source2_name": "Test Source 2",
    "source2_enabled": "Yes",
    "source3_name": "Test Source 3",
    "source3_enabled": "No",
    "main_volume_min": "-90",
    "main_volume_max": "5",
    "zone2_volume_min": "-100",
    "zone2_volume_max": "10",
    "main_source": "1",
    "zone2_source": "1",
}
MOCK_STATUS_ONE_ZONE = {
    "source1_name": "Test Source 1",
    "source1_enabled": "Yes",
    "source2_name": "Test Source 2",
    "source2_enabled": "Yes",
    "source3_name": "Test Source 3",
    "source3_enabled": "No",
    "main_volume_min": "-90",
    "main_volume_max": "5",
    "main_source": "1",
}
MOCK_MODEL = "T1234"
