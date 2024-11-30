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

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.list import ListManager

CONFIG = Config()


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
