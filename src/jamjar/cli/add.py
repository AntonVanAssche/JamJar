#!/usr/bin/env python

"""
CLI command for adding a Spotify playlist to the JamJar database.

This module facilitates adding a Spotify playlist (via URL or ID) and its tracks
to the JamJar database, ensuring all playlist metadata and tracks are properly stored.
"""

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.add import AddManager
from jamjar.core.managers.auth import Auth
from jamjar.core.spotify import SpotifyAPI

CONFIG = Config()


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def add(playlist):
    """
    Add a Spotify playlist to the database.

    This command accepts a Spotify playlist URL or ID and stores its metadata
    and tracks in the JamJar database.

    :param playlist: The Spotify playlist URL or ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    add_manager = AddManager(db, spotify_api)

    result = add_manager.add_playlist(playlist)

    if result["status"] == "created":
        print("Playlist added successfully.")
        print(f"Playlist: {result['playlist_summary']['playlist']['name']}")
        print(f"Tracks added: {len(result['tracks_summary']['added_tracks'])}")
    else:
        print("Error: Unexpected result: Add incomplete.")
