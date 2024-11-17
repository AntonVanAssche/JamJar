#!/usr/bin/env python

"""
CLI command for synchronizing a playlist with Spotify.

This module handles synchronizing a playlist with Spotify, updating the
tracks in the database, and removing tracks that are no longer in the
Spotify playlist.
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
class SyncManager:
    """
    Handles the logic for synchronizing a playlist with Spotify.

    This includes updating the playlist metadata, updating the tracks in the
    database, and removing tracks that are no longer in the Spotify playlist.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def sync_playlist(self, playlist_identifier):
        """
        Synchronize a playlist with Spotify.

        - Updates playlist metadata.
        - Updates tracks in the database.
        - Removes tracks from the database that are no longer in the
          Spotify playlist.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            print(f"Syncing playlist with ID {playlist_id}...")

            spotify_playlist = self.spotify_api.get_playlist(playlist_id)
            if not spotify_playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found on Spotify.")

            if not self.db.fetch_playlist_by_id(playlist_id):
                print(f"Playlist with ID {playlist_id} not found in the database.")
                AddManager(self.db, self.spotify_api).add_playlist(playlist_id)
                return

            name = spotify_playlist.get("name", "Unknown Playlist")
            owner = spotify_playlist.get("owner", {}).get("id", "Unknown User")
            description = spotify_playlist.get("description", "")
            url = spotify_playlist["external_urls"]["spotify"]
            self.db.update_playlist(playlist_id, name, owner, description, url)
            print(f"Synchronizing playlist '{name}' metadata in the database.")

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            add_manager = AddManager(self.db, self.spotify_api)
            add_manager.add_tracks(self.db, playlist_id, tracks_data, action="Synced")

            self._remove_deleted_tracks(playlist_id, tracks_data)

            print(f"Synchronization complete for playlist '{name}'.")
        except Exception as e:
            raise RuntimeError(f"Failed to sync playlist: {e}") from e

    def _remove_deleted_tracks(self, playlist_id, spotify_tracks):
        """
        Removes tracks from the database that are no longer in the Spotify playlist.
        """
        spotify_track_ids = {item["track"]["id"] for item in spotify_tracks["items"]}
        local_tracks = self.db.fetch_playlist_tracks(playlist_id)

        for local_track in local_tracks:
            if local_track[0] not in spotify_track_ids:
                self.db.delete_track(local_track[0])
                print(f"Removed track '{local_track[2]}' by '{local_track[3]}' from the database.")


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def sync(playlist):
    """
    Synchronize a playlist with Spotify.

    Updates playlist metadata and tracks in the database,
    and removes tracks from the database that are no longer in the Spotify
    playlist.

    Accepts either a full Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    sync_manager = SyncManager(db, spotify_api)

    sync_manager.sync_playlist(playlist)
