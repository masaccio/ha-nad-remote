"""Constants for NAD Amplifer remote control."""
# Base component constants
NAME = "NAD Amplifer remote control"
DOMAIN = "nad2"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/masaccio/nad2/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [SWITCH]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_IP_ADDRESS = "ip_address"

# Defaults
DEFAULT_NAME = DOMAIN
