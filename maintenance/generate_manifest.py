#! /usr/bin/env poetry run python3
import json
import toml

MANIFEST = "custom_components/nad_remote/manifest.json"

pyproject = toml.load("pyproject.toml")
API_VERSION = pyproject["tool"]["poetry"]["dependencies"]["nad_receiver"]

manifest = {
    "domain": "nad_remote",
    "name": "NAD Amplifer Remote",
    "codeowners": ["@masaccio"],
    "config_flow": True,
    "documentation": "https://github.com/masaccio/ha-nad-remote",
    "iot_class": "local_polling",
    "issue_tracker": "https://github.com/masaccio/ha-nad-remote/issues",
    # "requirements": [f"nad_receiver=={API_VERSION}"],
    "version": pyproject["tool"]["poetry"]["version"],
    "zeroconf": ["_telnet._tcp.local."],
}

with open(MANIFEST, "w") as fh:
    json.dump(manifest, fh, indent=2)
