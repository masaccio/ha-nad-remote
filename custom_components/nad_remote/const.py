"""Constants for NAD Amplifer remote control."""
from datetime import timedelta

NAME = "NAD Amplifer remote control"
DOMAIN = "nad_remote"

SCAN_INTERVAL = timedelta(seconds=5)

DEFAULT_MIN_VOLUME = -92
DEFAULT_MAX_VOLUME = -20
VOLUME_INCREMENT = 0.05

ZONE2_NAME = "Zone2"
MAIN_NAME = "Main"

LISTENING_MODES = [
    "None",
    "AnalogBypass",
    "DolbySurround",
    "EARS",
    "EnhancedStereo",
    "NEO6Music",
    "NEO6Cinema",
    "PLIIMovie",
    "PLIIMusic",
    "ProLogic",
    "SurroundEX",
    "StereoDownmix",
]
