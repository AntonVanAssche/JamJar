#!/usr/bin/env python

import json
import os
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import click
import requests

from jamjar.config import Config

CONFIG = Config()


class Auth:
    def __init__(self, config: Config):
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.base_url = "https://api.spotify.com/v1"
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        self.token_file = os.path.expanduser(config.token_file)

    def login(self):
        """Initiates the login flow."""
        try:
            scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative"
            params = {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "scope": scope,
                "show_dialog": True,
            }
            auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
            print(f"Please visit the following URL to authorize:\n{auth_url}\n")
            print("After authorizing, the app will handle the callback and complete authentication.")
            self._start_http_server()
        except Exception as e:
            print(f"Error initiating login: {e}")
            raise

    def _start_http_server(self):
        """Starts a local HTTP server to handle the Spotify callback."""
        try:

            class CallbackHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    try:
                        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                        if "error" in query:
                            print(f"Error during authorization: {query['error'][0]}")
                        elif "code" in query:
                            print("Authorization successful! Fetching access token...")
                            code = query["code"][0]
                            token_info = self.server.auth.get_token(code)
                            self.server.auth.save_token(token_info)
                            print(
                                f"Authentication complete! You are now logged in as {self.server.auth.display_username(token_info['access_token'])}."
                            )
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"Authentication successful! You can close this window.")
                    except Exception as e:
                        print(f"Error handling callback: {e}")
                        self.send_response(500)
                        self.end_headers()
                        raise

                def log_message(self, format, *args):
                    return  # Suppress HTTP server logs

            server = HTTPServer(("localhost", 5000), CallbackHandler)
            server.auth = self  # Pass the Auth instance to the handler
            print("Waiting for Spotify to redirect back to the app...")
            server.handle_request()

        except Exception as e:
            print(f"Error starting HTTP server: {e}")
            raise

    def get_token(self, code):
        """Exchanges the authorization code for an access token."""
        try:
            body = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = requests.post(self.token_url, data=body)
            response.raise_for_status()  # Raises HTTPError if the response code is 4xx or 5xx
            token_info = response.json()
            token_info["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]
            return token_info
        except requests.exceptions.RequestException as e:
            print(f"Error during token exchange: {e}")
            raise
        except Exception as e:
            print(f"Error processing token exchange response: {e}")
            raise

    def refresh_token(self):
        """Refreshes the access token if it has expired."""
        try:
            token_info = self.load_token()
            if not token_info or "refresh_token" not in token_info:
                raise RuntimeError("Refresh token not found. Please log in again.")

            if datetime.now().timestamp() < token_info["expires_at"]:
                return token_info

            print("Refreshing access token...")
            body = {
                "grant_type": "refresh_token",
                "refresh_token": token_info["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = requests.post(self.token_url, data=body)
            response.raise_for_status()
            new_token_info = response.json()
            new_token_info["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]
            self.save_token(new_token_info)
            return new_token_info

        except requests.exceptions.RequestException as e:
            print(f"Error during token refresh: {e}")
            raise
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise

    def save_token(self, token_info):
        """Saves token info to a file."""
        try:
            with open(self.token_file, "w") as f:
                json.dump(token_info, f)
        except Exception as e:
            print(f"Error saving token: {e}")
            raise

    def load_token(self):
        """Loads token info from a file."""
        try:
            if not os.path.exists(self.token_file):
                return None
            with open(self.token_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading token: {e}")
            raise
        except Exception as e:
            print(f"Error reading token file: {e}")
            raise

    def get_access_token(self):
        """Retrieves a valid access token, refreshing it if necessary."""
        try:
            token_info = self.refresh_token()
            return token_info["access_token"]
        except Exception as e:
            print(f"Error getting access token: {e}")
            raise

    def display_username(self, access_token):
        """Fetches and displays the user's username or display name."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{self.base_url}/me", headers=headers)
            response.raise_for_status()
            user_info = response.json()

            username = user_info.get("display_name", "Unknown User")
            return username
        except requests.exceptions.RequestException as e:
            print(f"Error fetching username: {e}")
            raise
        except Exception as e:
            print(f"Error processing username response: {e}")
            raise

    def status(self):
        """Displays the current authentication status."""
        try:
            token_info = self.load_token()
            if not token_info:
                print("Not logged in.")
                return
            if datetime.now().timestamp() > token_info["expires_at"]:
                print("Access token expired. Run `jamjar --auth` to refresh.")
            else:
                print(f"Logged in as {self.display_username(token_info['access_token'])}.")
                print(f"Access token expires at {datetime.fromtimestamp(token_info['expires_at'])}.")
        except Exception as e:
            print(f"Error displaying status: {e}")
            raise

    def clean(self, config):
        """Removes the saved access token."""
        try:
            token_file = os.path.expanduser("~/.jamjar_token.json")
            if os.path.exists(token_file):
                os.remove(token_file)
                print("Access token removed.")
            else:
                print("No access token found.")
        except Exception as e:
            print(f"Error removing access token: {e}")
            raise


@click.group()
@click.help_option("--help", "-h")
def auth():
    """Manage Spotify authentication."""
    pass


@auth.command()
@click.help_option("--help", "-h")
def login():
    """Log in to Spotify."""
    auth = Auth(CONFIG)
    auth.login()


@auth.command()
@click.help_option("--help", "-h")
def status():
    """Display authentication status."""
    auth = Auth(CONFIG)
    auth.status()


@auth.command()
@click.help_option("--help", "-h")
def clean():
    """Remove the saved access token."""
    auth = Auth(CONFIG)
    auth.clean(CONFIG)
