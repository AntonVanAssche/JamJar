#!/usr/bin/env python

"""
Handles the logic for pushing a playlist to Spotify.

This module provides a PushManager class that interacts with the Spotify
API to create a new playlist, add tracks to it, and set a cover image.
"""

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.auth import Auth
from jamjar.core.managers.push import PushManager
from jamjar.core.spotify import SpotifyAPI

CONFIG = Config()


@click.command()
@click.help_option("--help", "-h")
@click.option("--name", "-n", help="Name for the playlist.")
@click.option("--description", "-d", help="Description for the playlist.")
@click.option("--public", "-p", is_flag=True, help="Make the playlist public.")
@click.option("--image", "-i", help="Path to an image file for the playlist cover.")
@click.argument("playlist_id")
def push(playlist_id, name, description, public, image):
    """
    Push a playlist to Spotify.

    :param playlist: The Spotify playlist URL or ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    push_manager = PushManager(db, spotify_api)

    if not name:
        prompt = "Enter a name for the new playlist"
        name = click.prompt(prompt, type=str)

    try:
        result = push_manager.push_playlist(playlist_id, name, description, public, image)
        print(f"Playlist created: {result['playlist_url']}")
        print(f"Tracks added: {result['track_count']}")
        print(f"Public: {result['public']}")
        print(f"Cover image uploaded: {result['image_uploaded']}")
    except RuntimeError as e:
        print(f"Error: {e}")
