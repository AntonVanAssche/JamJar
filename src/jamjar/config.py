#!/usr/bin/env python

"""
This module handles the configuration for the JamJar CLI.

This includes reading the configuration file and retrieving the client_id,
client_secret, redirect_uri, database path, and token file path.
"""

import json
import os
from pathlib import Path


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
        if key not in self.config_data:
            if default is None:
                raise KeyError(f"Configuration key '{key}' not found")
        return self.config_data.get(key, default)

    @property
    def client_id(self):
        """Retrieve the client_id from the config."""
        return self.get("client_id")

    @property
    def client_secret(self):
        """Retrieve the client_secret from the config."""
        return self.get("client_secret")

    @property
    def redirect_uri(self):
        """Retrieve the redirect URI from the config."""
        return self.get("redirect_uri", "http://localhost:5000/callback")

    @property
    def config_file(self):
        """Retrieve the config file path."""
        if os.name == "nt":
            base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
            return base_dir / "JamJar" / "config.json"

        return Path.home() / ".jamjar_config.json"

    @property
    def db_path(self):
        """Retrieve the database path."""
        if os.name == "nt":
            base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
            return base_dir / "JamJar" / "jamjar.db"

        return Path.home() / ".jamjar.db"

    @property
    def token_file(self):
        """Retrieve the token file path."""
        if os.name == "nt":
            base_dir = Path(os.getenv("APPDATA", r"~/AppData/Roaming")).expanduser()
            return base_dir / "JamJar" / "token.json"

        return Path.home() / ".jamjar_token.json"
