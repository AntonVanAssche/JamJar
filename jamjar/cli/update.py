#!/usr/bin/env python

"""
CLI command for updating an existing playlist in the database.

This module handles updating an existing playlist in the JamJar database,
including all of its tracks.
"""

import click

from jamjar.cli.add import AddManager
from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI
from jamjar.utils import extract_playlist_id

CONFIG = Config()


# pylint: disable=too-few-public-methods
class UpdateManager:
    """
    Handles the logic for updating an existing playlist in the database.

    This includes extracting playlist information and updating both the playlist
    and its tracks in the database.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def update_playlist(self, playlist_identifier):
        """
        Update an existing playlist in the database.

        Accepts either a full Spotify playlist URL or just a playlist ID.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            print(f"Updating playlist with ID {playlist_id}...")

            playlist_data = self.spotify_api.get_playlist(playlist_id)
            name = playlist_data.get("name", "Unknown Playlist")
            owner = playlist_data.get("owner", {}).get("id", "Unknown User")
            description = playlist_data.get("description", "")
            url = playlist_data["external_urls"]["spotify"]
            self.db.update_playlist(playlist_id, name, owner, description, url)

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            add_manager = AddManager(self.db, self.spotify_api)
            add_manager.add_tracks(self.db, playlist_id, tracks_data, action="Updated")

            print(f"Playlist '{name}' updated successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to update playlist: {e}") from e


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def update(playlist):
    """
    Update an existing playlist in the database.

    Accepts either a Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    update_manager = UpdateManager(db, spotify_api)

    update_manager.update_playlist(playlist)
