#!/usr/bin/env python

"""
CLI command to list playlists or tracks in a specific playlist.

This module handles listing all playlists stored in the JamJar database,
and listing all tracks in a specific playlist.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database
from jamjar.utils import extract_playlist_id, format_json_output

CONFIG = Config()


# pylint: disable=too-few-public-methods
class ListManager:
    """
    Handles the logic for listing playlists and tracks.

    This includes fetching playlists and tracks from the database and
    formatting the output for display.
    """

    def __init__(self, db: Database):
        self.db = db

    def list_playlists(self):
        """
        List all playlists stored in the database.
        """
        try:
            playlists = self.db.fetch_playlists()
            if not playlists:
                print(json.dumps({"message": "No playlists found."}, indent=2))
                return

            headers = ["ID", "Name", "Description", "Owner", "URL"]
            print(format_json_output("Playlists", headers, playlists))
        except Exception as e:
            raise RuntimeError(f"Failed to list playlists: {e}") from e

    def list_tracks(self, playlist_id):
        """
        List all tracks in a specific playlist.
        """
        try:
            playlist_id = extract_playlist_id(playlist_id)
            tracks = self.db.fetch_playlist_tracks(playlist_id)
            if not tracks:
                # pylint: disable=line-too-long
                print(json.dumps({"message": f"No tracks found for playlist ID '{playlist_id}'."}, indent=2))
                return

            headers = ["Playlist", "Track ID", "Name", "Artist", "Added by User", "Added on"]
            print(format_json_output("Tracks", headers, tracks))
        except Exception as e:
            raise RuntimeError(f"Failed to list tracks: {e}") from e


# pylint: disable=redefined-builtin
@click.command()
@click.help_option("--help", "-h")
@click.option("--playlist", "-p", help="ID, or URL, of the playlist to list tracks for.")
def list(playlist=None):
    """
    List playlists or tracks in a specific playlist.

    Without options, lists all playlists.
    Use --playlist to list tracks in a specific playlist.
    """
    db = Database(CONFIG)
    list_manager = ListManager(db)

    if playlist:
        list_manager.list_tracks(playlist)
    else:
        list_manager.list_playlists()
