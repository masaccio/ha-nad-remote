"""Constants for NAD Amplifer remote control."""

from datetime import timedelta

# Base component constants
NAME = "NAD Amplifer remote control"
DOMAIN = "nad_remote"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/masaccio/nad_remote/issues"

SCAN_INTERVAL = timedelta(seconds=30)

CONF_MIN_VOLUME = "min_volume"
CONF_MAX_VOLUME = "max_volume"

DEFAULT_MIN_VOLUME = -92
DEFAULT_MAX_VOLUME = -20

ZONE2_NAME = "Zone2"
MAIN_NAME = "Main"
