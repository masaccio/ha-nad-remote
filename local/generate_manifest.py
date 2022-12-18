#! /usr/bin/env poetry run python3
import json
import toml

MANIFEST = "custom_components/nad2/manifest.json"

pyproject = toml.load("pyproject.toml")
API_VERSION = pyproject["tool"]["poetry"]["dependencies"]["nad_receiver"]

manifest = {
    "domain": "nad2",
    "name": "NAD Amplifer",
    "documentation": "https://github.com/masaccio/nad2",
    "iot_class": "local_polling",
    "issue_tracker": "https://github.com/masaccio/nad2/issues",
    "config_flow": True,
    "version": pyproject["tool"]["poetry"]["version"],
    "codeowners": ["@masaccio"],
    "requirements": [f"nad_receiver=={API_VERSION}"],
}

with open(MANIFEST, "w") as fh:
    json.dump(manifest, fh, indent=2)
