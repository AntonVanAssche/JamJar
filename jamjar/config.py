#!/usr/bin/env python

import json
import os

CONFIG_FILE = os.path.expanduser("~/.jamjar_config.json")


class Config:
    def __init__(self):
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Configuration file not found at {CONFIG_FILE}")

        with open(CONFIG_FILE, "r") as f:
            self.config_data = json.load(f)

    def get(self, key, default=None):
        """Get a configuration value by key."""
        if key not in self.config_data:
            if default is None:
                raise KeyError(f"Configuration key '{key}' not found")
        return self.config_data.get(key, default)

    def save(self):
        """Save updated configuration to the config file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)

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
    def db_path(self):
        """Retrieve the database path from the config."""
        return self.get("db_path", "~/.jamjar.db")

    @property
    def token_file(self):
        """Retrieve the token file path from the config."""
        return self.get("token_file", "~/.jamjar_token.json")
