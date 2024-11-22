#!/usr/bin/env python

"""
A command-line interface (CLI) tool for listing playlists and tracks present in the
JamJar database.

This module allows users to list all playlists stored in the JamJar database,
or to list all tracks in a specific playlist, by fetching data from the database
and displaying it in a structured format.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database
from jamjar.utils import extract_playlist_id

CONFIG = Config()


# pylint: disable=too-few-public-methods
class ListManager:
    """
    Manages the logic for listing playlists and tracks.

    This class provides methods to list all playlists stored in the database
    or to list all tracks within a specific playlist. It formats the output
    into JSON for easy display.
    """

    def __init__(self, db: Database):
        """
        Initialize the DiffManager with the necessary database instance.

        :param db: Database instance for fetching playlist and track data.
        """

        self.db = db

    def list_playlists(self) -> dict:
        """
        Retrieves and displays all playlists stored in the database.

        Fetches all playlists from the database and prints their details, including
        the playlist's name, ID, owner, track count, and more. If no playlists are found,
        a message is displayed indicating that no playlists are available.
        """

        try:
            playlists = self.db.fetch_playlists()
            if not playlists:
                raise ValueError("No playlists found in the database.")

            return {"playlists": [playlist._asdict() for playlist in playlists]}

        except Exception as e:
            raise RuntimeError(f"Failed to list playlists: {e}") from e

    def list_tracks(self, playlist_id: str) -> dict:
        """
        Retrieves and displays all tracks in a specific playlist.

        Fetches all tracks from a specified playlist ID and prints their details,
        such as track name, artist, album, popularity, and more. If no tracks are
        found for the given playlist ID, a message is displayed indicating no tracks.

        :param playlist_id: The ID or URL of the playlist to list tracks from.
        """

        try:
            playlist_id = extract_playlist_id(playlist_id)
            tracks = self.db.fetch_tracks(playlist_id)
            if not tracks:
                raise ValueError(f"No tracks found for playlist ID {playlist_id}.")

            return {"tracks": [track._asdict() for track in tracks]}
        except Exception as e:
            raise RuntimeError(f"Failed to list tracks: {e}") from e


# pylint: disable=redefined-builtin
@click.command()
@click.help_option("--help", "-h")
@click.option("--playlist", "-p", help="ID, or URL, of the playlist to list tracks for.")
def list(playlist=None):
    """
    Lists all playlists or tracks in a specific playlist.

    When no playlist option is provided, this command lists all playlists in the
    database. If the --playlist option is provided with a valid playlist ID or URL,
    it will list all tracks in that specific playlist.

    :param playlist: Optional ID or URL of a playlist to list tracks from.
    """

    db = Database(CONFIG)
    list_manager = ListManager(db)

    if playlist:
        playlist_data = list_manager.list_tracks(playlist)
    else:
        playlist_data = list_manager.list_playlists()

    print(json.dumps(playlist_data, indent=2))
