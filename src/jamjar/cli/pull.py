#!/usr/bin/env python

"""
CLI command for synchronizing a playlist with Spotify.

This module handles synchronization of a playlist with Spotify, including
updating the database with new tracks and optionally removing tracks no longer
present in the Spotify playlist.
"""

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.auth import Auth
from jamjar.core.managers.pull import PullManager
from jamjar.core.spotify import SpotifyAPI

CONFIG = Config()


# pylint: disable=line-too-long
@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
@click.option("--rm", "-r", is_flag=True, help="Remove tracks that are no longer in the Spotify playlist.")
def pull(playlist, rm=False):
    """
    Pull changes from a playlist and update the database.

    Updates the database with the latest playlist metadata and tracks from Spotify.
    Optionally removes tracks that are no longer in the Spotify playlist.

    :param playlist: The Spotify playlist ID or URL to synchronize.
    :param rm: If provided, removes tracks no longer in the Spotify playlist.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    pull_manager = PullManager(db, spotify_api)

    result = pull_manager.pull_playlist(playlist, rm)

    if result["status"] == "created":
        print("Playlist created in the database.")
        print(f"Playlist: {result['data']['playlist_summary']['playlist']['name']}")
    elif result["status"] == "updated":
        print("Playlist synchronized successfully.")
        print(f"Playlist: {result['playlist']['playlist']['name']}")
        print(f"Tracks updated: {len(result['tracks']['added'])}")

        if rm:
            print(f"Tracks removed: {len(result['tracks']['removed'])}")
    else:
        print("Error: Unexpected result: Sync incomplete.")
