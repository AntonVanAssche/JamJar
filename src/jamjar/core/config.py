#!/usr/bin/env python

"""
This module handles the configuration for the JamJar CLI.

This includes reading the configuration file and retrieving the client_id,
client_secret, redirect_uri, database path, and token file path.
"""

import json
import os
from pathlib import Path


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class Config:
    """
    Handles the configuration for the JamJar CLI.

    This includes reading the configuration file and retrieving the client_id,
    client_secret, redirect_uri, database path, and token file path.
    """

    def __init__(self):
        config_file = self.config_file
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found at {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            self.config_data = json.load(f)

    def get(self, key, default=None):
        """Get a configuration value by key."""

        try:
            if key not in self.config_data:
                if default is None:
                    raise ConfigError(f"Configuration key '{key}' not found")
            return self.config_data.get(key, default)
        except Exception as e:
            raise ConfigError(f"Unable to retrieve config value: {e}") from e

    @property
    def client_id(self):
        """Retrieve the client_id from the config."""

        try:
            return self.get("client_id")
        except Exception as e:
            raise ConfigError(f"Unable to set client ID: {e}") from e

    @property
    def client_secret(self):
        """Retrieve the client_secret from the config."""

        try:
            return self.get("client_secret")
        except Exception as e:
            raise ConfigError(f"Unable to set client secret: {e}") from e

    @property
    def redirect_uri(self):
        """Retrieve the redirect URI from the config."""

        try:
            return self.get("redirect_uri", "http://localhost:5000/callback")
        except Exception as e:
            raise ConfigError(f"Unable to set redirect URI: {e}") from e

    @property
    def config_file(self):
        """Retrieve the config file path."""

        try:
            if os.name == "nt":
                base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
                return base_dir / "JamJar" / "config.json"

            return Path.home() / ".config" / "jamjar" / "config.json"
        except Exception as e:
            raise ConfigError(f"Unable to set config file path: {e}") from e

    @property
    def db_path(self):
        """Retrieve the database path."""

        try:
            if os.name == "nt":
                base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
                return base_dir / "JamJar" / "jamjar.db"

            return Path.home() / ".local" / "share" / "jamjar" / "jamjar.db"
        except Exception as e:
            raise ConfigError(f"Unable to set database path: {e}") from e

    @property
    def token_file(self):
        """Retrieve the token file path."""

        try:
            if os.name == "nt":
                base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
                return base_dir / "JamJar" / "token.json"

            return Path.home() / ".config" / "jamjar" / "token.json"
        except Exception as e:
            raise ConfigError(f"Unable to set token file path: {e}") from e
