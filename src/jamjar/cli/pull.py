#!/usr/bin/env python

"""
CLI command for synchronizing a playlist with Spotify.

This module handles synchronization of a playlist with Spotify, including
updating the database with new tracks and optionally removing tracks no longer
present in the Spotify playlist.
"""

import click

from jamjar.cli.add import AddManager
from jamjar.cli.auth import Auth
from jamjar.cli.rm import RemoveManager
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI
from jamjar.utils import extract_playlist_id

CONFIG = Config()


# pylint: disable=too-few-public-methods
class PullManager:
    """
    Manages the synchronization of a playlist with Spotify.

    This class updates the database with new playlist metadata and tracks,
    and optionally removes tracks no longer present in the Spotify playlist.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        """
        Initialize the PullManager with database and Spotify API instances.

        :param db: An instance of the Database class for database operations.
        :param spotify_api: An instance of the SpotifyAPI class for Spotify operations.
        """

        self.db = db
        self.spotify_api = spotify_api

    def pull_playlist(self, playlist_identifier: str, rm: bool = False):
        """
        Synchronize a playlist with Spotify.

        Fetches the playlist metadata and tracks from Spotify, updates the database,
        and optionally removes tracks no longer in the Spotify playlist.

        :param playlist_identifier: The Spotify playlist ID or URL to synchronize.
        :param rm: If True, remove tracks from the database that are no longer
                   present in the Spotify playlist.
        :raises ValueError: If the specified playlist cannot be found on Spotify.
        :raises RuntimeError: If the synchronization process fails.
        """

        try:
            add_manager = AddManager(self.db, self.spotify_api)
            playlist_id = extract_playlist_id(playlist_identifier)
            print(f"Pulling changes fo playlist with ID {playlist_id}...")

            spotify_playlist = self.spotify_api.get_playlist(playlist_id)
            if not spotify_playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found on Spotify.")

            if not self.db.fetch_playlists(playlist_id):
                print(f"Playlist with ID {playlist_id} not found in the database.")
                AddManager(self.db, self.spotify_api).add_playlist(playlist_id)
                return

            action = "Pulled"
            playlist_data = self.spotify_api.get_playlist(playlist_id)
            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)

            add_manager.add_playlist_to_db(playlist_id, playlist_data, action)
            add_manager.add_tracks_to_db(playlist_id, tracks_data, action)

            if rm:
                self._remove_deleted_tracks(playlist_id, tracks_data)
        except Exception as e:
            raise RuntimeError(f"Failed to sync playlist: {e}") from e

    def _remove_deleted_tracks(self, playlist_id: str, spotify_tracks: dict):
        """
        Remove tracks from the database that are no longer in the Spotify playlist.

        Compares the tracks in the Spotify playlist with those in the local database,
        and removes tracks from the database that are missing in Spotify.

        :param playlist_id: The Spotify playlist ID.
        :param spotify_tracks: A dictionary of tracks fetched from Spotify.
        :raises RuntimeError: If the track removal process fails.
        """

        try:
            rm_manager = RemoveManager(self.db)
            spotify_track_ids = {item["track"]["id"] for item in spotify_tracks["items"]}
            local_tracks = self.db.fetch_tracks(playlist_id)

            for local_track in local_tracks:
                if local_track.track_id not in spotify_track_ids:
                    rm_manager.remove_track(playlist_id, local_track.track_id)
        except Exception as e:
            raise RuntimeError(f"Failed to remove deleted tracks: {e}") from e


# pylint: disable=line-too-long
@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
@click.option("--rm", "-r", is_flag=True, help="Remove tracks that are no longer in the Spotify playlist.")
def pull(playlist, rm=False):
    """
    Command-line interface to synchronize a playlist with Spotify.

    Updates the database with the latest playlist metadata and tracks from Spotify.
    Optionally removes tracks that are no longer in the Spotify playlist.

    :param playlist: The Spotify playlist ID or URL to synchronize.
    :param rm: If provided, removes tracks no longer in the Spotify playlist.
    """

    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    pull_manager = PullManager(db, spotify_api)

    pull_manager.pull_playlist(playlist, rm)
