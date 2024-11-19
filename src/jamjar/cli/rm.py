#!/usr/bin/env python

"""
CLI command removing playlists or tracks from the JamJar database.

This module provides functionality to:
1. Remove a playlist and all its associated tracks from the database.
2. Remove a specific track from a playlist in the database.
3. Optionally, remove all playlists and tracks from the database.
"""

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


class RemoveManager:
    """
    Manages the removal of playlists or tracks from the database.

    Provides methods to:
    - Remove an entire playlist along with all its associated tracks.
    - Remove a specific track from a playlist.
    """

    def __init__(self, db: Database):
        """
        Initialize the RemoveManager with a database instance.

        :param db: Instance of the Database class for performing database operations.
        """

        self.db = db

    def remove_playlist(self, playlist_id):
        """
        Remove a playlist and all its associated tracks from the database.

        :param playlist_id: The unique identifier of the playlist to remove.
        :raises RuntimeError: If an error occurs during playlist removal.
        """

        try:
            playlist = self.db.fetch_playlists(playlist_id)
            if not playlist:
                print(f"Playlist with ID '{playlist_id.playlist_id}' not found.")
                return

            print(f"Removing playlist with ID {playlist_id}...")

            self.db.delete_playlist(playlist_id)
            print(f"Playlist '{playlist.playlist_name}' (ID: {playlist_id}) removed successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to remove playlist: {e}") from e

    def remove_track(self, playlist_id, track_id):
        """
        Remove a specific track from a playlist in the database.

        :param playlist_id: The unique identifier of the playlist containing the track.
        :param track_id: The unique identifier of the track to remove.
        :raises RuntimeError: If an error occurs during track removal.
        """

        try:
            track = self.db.fetch_track_by_id(playlist_id, track_id)
            if not track:
                print(f"Track with ID '{track_id}' not found in playlist '{playlist_id}'.")
                return

            self.db.delete_track(track_id, playlist_id)
            print(f"Removed track '{track.track_name}' by '{track.artist_name}'.")
        except Exception as e:
            raise RuntimeError(f"Failed to remove track: {e}") from e


# pylint: disable=redefined-builtin
@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id", required=False)
@click.option("--track-id", "-t", help="ID of the track to remove.")
@click.option("--all", "-a", is_flag=True, help="Remove all playlists and tracks.")
@click.option("--force", "-f", is_flag=True, help="Force removal without confirmation.")
def rm(playlist_id=None, track_id=None, all=False, force=False):
    """
    Remove playlists or tracks from the database.

    Either a single playlist, track within a playlist, or all playlists and tracks
    can be removed.

    :param playlist_id: The unique identifier of the playlist to remove (optional).
    :param track_id: The unique identifier of the track to remove (optional).
    :param all: Flag to remove all playlists and tracks.
    :param force: Flag to force removal without confirmation (only for --all).
    :raises click.BadParameter: If neither playlist_id nor --all is provided.
    """

    if not playlist_id and not all:
        raise click.BadParameter("Please provide a playlist ID or use the --all option.")

    db = Database(CONFIG)
    remove_manager = RemoveManager(db)
    if all:
        if not force:
            prompt = "Are you sure you want to remove all playlists and tracks? (y/N): "
            confirmation = input(prompt)
            if confirmation.lower() != "y":
                print("Aborted.")
                return
        db.delete_all_playlists()
        print("All playlists and tracks removed successfully.")
    elif track_id:
        remove_manager.remove_track(playlist_id, track_id)
    else:
        remove_manager.remove_playlist(playlist_id)
