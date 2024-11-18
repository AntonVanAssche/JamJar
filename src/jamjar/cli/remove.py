#!/usr/bin/env python

"""
CLI command to remove a playlist or a specific track from a playlist.

This module handles removing a playlist from the JamJar database, as well as
removing a specific track from a playlist in the database.
"""

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


# pylint: disable=too-few-public-methods
class RemoveManager:
    """
    Handles the logic for removing a playlist or a specific track from a playlist.

    This includes removing a playlist and all associated tracks from the database,
    as well as removing a specific track from a playlist.
    """

    def __init__(self, db: Database):
        self.db = db

    def remove_playlist(self, playlist_id):
        """
        Remove a playlist and all associated tracks from the database.
        """
        try:
            playlist = self.db.fetch_playlist_by_id(playlist_id)
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
        """
        try:
            track = self.db.fetch_track_by_id(playlist_id, track_id)
            if not track:
                print(f"Track with ID '{track_id}' not found in playlist '{playlist_id}'.")
                return

            # pylint: disable=line-too-long
            self.db.delete_track(track_id, playlist_id)
            print(
                f"Track '{track.track_name}' by '{track.artist_name}' removed from playlist '{playlist_id}' successfully."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to remove track: {e}") from e


# pylint: disable=redefined-builtin
@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id", required=False)
@click.option("--track-id", "-t", help="ID of the track to remove.")
@click.option("--all", "-a", is_flag=True, help="Remove all playlists and tracks.")
@click.option("--force", "-f", is_flag=True, help="Force removal without confirmation.")
def remove(playlist_id=None, track_id=None, all=False, force=False):
    """
    Remove a playlist or a specific track from a playlist.

    \b
    Examples:
        - Remove an entire playlist: jamjar remove <playlist_id>
        - Remove a specific track: jamjar remove <playlist_id> --track-id <track_id>
        - Remove all playlists and tracks: jamjar remove --all
        - Remove all playlists and tracks without confirmation: jamjar remove --all --force
    """

    if not playlist_id and not all:
        raise click.BadParameter("Please provide a playlist ID or use the --all option.")

    db = Database(CONFIG)
    remove_manager = RemoveManager(db)
    if all:
        if not force:
            # pylint: disable=line-too-long
            confirmation = input("Are you sure you want to remove all playlists and tracks? (y/N): ")
            if confirmation.lower() != "y":
                print("Aborted.")
                return
        db.delete_all_playlists()
        print("All playlists and tracks removed successfully.")
    elif track_id:
        remove_manager.remove_track(playlist_id, track_id)
    else:
        remove_manager.remove_playlist(playlist_id)
