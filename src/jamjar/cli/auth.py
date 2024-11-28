#!/usr/bin/env python

"""
CLI command for authenticating with Spotify.

This module handles the Spotify authentication flow, including
logging in, refreshing the access token, and storing the token.
"""

from datetime import datetime

import click

from jamjar.core.config import Config
from jamjar.core.managers.auth import Auth

CONFIG = Config()


@click.group()
@click.help_option("--help", "-h")
def auth():
    """Manage Spotify authentication."""


@auth.command()
@click.help_option("--help", "-h")
def login():
    """Log in to Spotify."""
    auth_instance = Auth(CONFIG)
    auth_url = auth_instance.generate_auth_url()
    print(f"Please visit the following URL to authorize:\n{auth_url}\n")
    print("After authorizing, the app will handle the callback and complete authentication.")
    token_info = auth_instance.start_http_server()

    if token_info:
        username = auth_instance.verify_token(token_info).get("display_name", "Unknown User")
        print(f"Authentication successful. Logged in as {username}.")
    else:
        print("Authentication failed. Please try again.")


@auth.command()
@click.help_option("--help", "-h")
def status():
    """Display authentication status."""
    auth_instance = Auth(CONFIG)
    token_info = auth_instance.load_token()

    if not token_info:
        print("Not logged in.")
    elif datetime.now().timestamp() > token_info["expires_at"]:
        print("Access token expired. Please log in again.")
    else:
        username = auth_instance.verify_token(token_info).get("display_name", "Unknown User")
        expires_at = datetime.fromtimestamp(token_info["expires_at"]).replace(microsecond=0)
        print(f"Logged in as {username}.")
        print(f"Access token expires at {expires_at}.")


@auth.command()
@click.help_option("--help", "-h")
def clean():
    """Remove the saved access token."""
    auth_instance = Auth(CONFIG)
    result = auth_instance.clean_token()
    if "error" in result:
        print(result["error"])
    else:
        print("Access token removed successfully.")
