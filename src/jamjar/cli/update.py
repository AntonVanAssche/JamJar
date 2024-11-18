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
            # pylint: disable=duplicate-code
            add_manager = AddManager(self.db, self.spotify_api)
            playlist_id = extract_playlist_id(playlist_identifier)
            print(f"Updating playlist with ID {playlist_id}...")

            action = "Updated"
            playlist_data = self.spotify_api.get_playlist(playlist_id)
            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)

            add_manager.add_playlist_to_db(playlist_id, playlist_data, action)
            add_manager.add_tracks_to_db(playlist_id, tracks_data, action)

            # pylint: disable=line-too-long
            print(f"Playlist '{playlist_data.get("name", "Unknown Playlist")}' updated successfully.")
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
