#!/usr/bin/env python

"""
CLI command removing playlists or tracks from the JamJar database.

This module provides functionality to:
1. Remove a playlist and all its associated tracks from the database.
2. Remove a specific track from a playlist in the database.
3. Optionally, remove all playlists and tracks from the database.
"""

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.rm import RemoveManager

CONFIG = Config()


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
            prompt_message = "Are you sure you want to remove all playlists and tracks? (y/N)"
            confirmation = click.prompt(prompt_message, default="n")
            if confirmation.lower() != "y":
                print("Aborted.")
                return
        db.delete_all_playlists()
        print("All playlists and tracks removed successfully.")
    elif track_id:
        result = remove_manager.remove_track(playlist_id, track_id)
        if result["status"] == "removed":
            print(f"Track '{result['removed_track']}' removed successfully.")
    else:
        result = remove_manager.remove_playlist(playlist_id)
        if result["status"] == "removed":
            print(f"Playlist '{result['removed_playlist']}' removed successfully.")
