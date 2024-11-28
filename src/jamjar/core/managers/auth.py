#!/usr/bin/env python

"""
CLI command for authenticating with Spotify.

This module handles the Spotify authentication flow, including
logging in, refreshing the access token, and storing the token.
"""

import json
import os
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

from jamjar.core.config import Config


class Auth:
    """
    Handles the Spotify authentication flow.

    This includes logging in, refreshing the access token, and
    storing the token for future use.
    """

    def __init__(self, config: Config):
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.base_url = "https://api.spotify.com/v1"
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        self.token_file = os.path.expanduser(config.token_file)

    def generate_auth_url(self) -> str:
        """Generates the Spotify authorization URL."""
        scope = (
            "user-read-private "
            "user-read-email "
            "playlist-read-private "
            "playlist-read-collaborative "
            "playlist-modify-private "
            "playlist-modify-public "
            "ugc-image-upload"
        )
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "show_dialog": True,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def start_http_server(self) -> dict:
        """Starts a local HTTP server to handle the Spotify callback."""
        try:

            class CallbackHandler(BaseHTTPRequestHandler):
                """Handles the Spotify callback and exchanges the code for an access token."""

                # pylint: disable=invalid-name
                def do_GET(self) -> None:
                    """Handle the GET request from the Spotify callback."""
                    try:
                        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

                        if "code" in query:
                            code = query["code"][0]
                            token_info = self.server.auth.get_token(code)
                            success_msg = "Authentication successful! You can close this window."
                            self.server.auth.save_token(token_info)
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(success_msg.encode())
                            self.server.token_info = token_info

                        elif "error" in query:
                            error_message = query["error"][0]
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(b"Authentication failed. Please try again.")
                            self.server.token_info = {"error": error_message}
                            raise RuntimeError(f"Authentication error received: {error_message}")

                    except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        raise RuntimeError(f"Failed to handle callback request: {e}") from e

                # pylint: disable=redefined-builtin
                def log_message(self, format, *args) -> None:
                    """Suppress log messages."""
                    return

            server = HTTPServer(("localhost", 5000), CallbackHandler)
            server.auth = self
            server.handle_request()
            return getattr(server, "token_info", None)
        except Exception as e:
            raise RuntimeError(f"Failed to start HTTP server: {e}") from e

    def get_token(self, code: str) -> dict:
        """Exchanges the authorization code for an access token."""
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_url, data=body, timeout=10)
        response.raise_for_status()
        token_info = response.json()
        token_info["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]
        return token_info

    def refresh_token(self) -> dict:
        """Refreshes the access token if it has expired."""
        token_info = self.load_token()
        if not token_info or "refresh_token" not in token_info:
            return {"error": "Refresh token not found. Please log in again."}

        if datetime.now().timestamp() < token_info["expires_at"]:
            return token_info

        body = {
            "grant_type": "refresh_token",
            "refresh_token": token_info["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_url, data=body, timeout=10)
        response.raise_for_status()
        new_token_info = response.json()
        new_token_info["refresh_token"] = token_info["refresh_token"]
        new_token_info["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]
        self.verify_token(new_token_info)
        self.save_token(new_token_info)
        return new_token_info

    def verify_token(self, token_info: dict) -> dict:
        """Verifies the validity of the access token."""
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        response = requests.get(f"{self.base_url}/me", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def save_token(self, token_info: dict):
        """Saves token info to a file."""
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(token_info, f)

    def load_token(self) -> dict:
        """Loads token info from a file."""
        if not os.path.exists(self.token_file):
            return None
        with open(self.token_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_access_token(self) -> str:
        """Returns the access token."""
        token_info = self.load_token()
        if not token_info:
            raise RuntimeError("Access token not found. Please log in.")
        if datetime.now().timestamp() > token_info["expires_at"]:
            token_info = self.refresh_token()
        return token_info["access_token"]

    def clean_token(self) -> dict:
        """Removes the saved access token."""
        if not os.path.exists(self.token_file):
            raise RuntimeError("Access token not found.")

        os.remove(self.token_file)
        return {"status": "success"}
