#!/usr/bin/env python

"""
CLI command for comparing the contents of a playlist in the database with the current
state of the playlist on Spotify.

This modules allows users to compare the playlist data between the JamJar database
and the actual Spotify playlist. It generates a JSON diff of the differences in
tracks and metadata.
"""

import json

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.auth import Auth
from jamjar.core.managers.diff import DiffManager
from jamjar.core.spotify import SpotifyAPI

CONFIG = Config()


# pylint: disable=line-too-long
@click.command()
@click.help_option("--help", "-h")
@click.option("--details", "-d", is_flag=True, help="Show detailed differences, including metadata changes.")
@click.argument("playlist")
def diff(playlist, details):
    """
    Compare a playlist with its current state on Spotify.

    :param playlist: The Spotify playlist URL or ID to compare.
    :param details: Flag to indicate whether detailed metadata differences should be shown.
    """

    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    diff_manager = DiffManager(db, spotify_api)

    diff_data = diff_manager.diff_playlist(playlist, details)
    print(json.dumps(diff_data, indent=2))
