#!/usr/bin/env python

"""
Handles the logic for pushing a playlist to Spotify.

This module provides a PushManager class that interacts with the Spotify
API to create a new playlist, add tracks to it, and set a cover image.
"""

import base64

import click

from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI

CONFIG = Config()


# pylint: disable=too-few-public-methods
class PushManager:
    """Manages the process of pushing a playlist to Spotify."""

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        """
        Initialize the PushManager with database and Spotify API instances.

        :param db: An instance of the Database class for database operations.
        :param spotify_api: An instance of the SpotifyAPI class for Spotify interactions.
        """

        self.db = db
        self.spotify_api = spotify_api

    def _get_user_id(self):
        """
        Fetch the Spotify user ID.
        :return: The Spotify user ID.
        """

        return self.spotify_api.get_user_id()

    def _get_playlist_data(self, playlist_id):
        """
        Fetch details of a Spotify playlist using its ID.
        :param playlist_id: The Spotify playlist ID.
        :return: A dictionary containing playlist details fetched from Spotify.
        """

        return self.spotify_api.get_playlist(playlist_id)

    def _get_playlist_tracks(self, playlist_id):
        """
        Fetch tracks of a Spotify playlist using its ID.
        :param playlist_id: The Spotify playlist ID.
        :return: A dictionary containing track details fetched from Spotify.
        """

        return self.spotify_api.get_playlist_tracks(playlist_id)

    def _encode_image(self, image_path):
        """
        Encode an image file to base64.
        :param image_path: The path to the image file.
        :return: The base64-encoded image.
        """

        with open(image_path, "rb") as image:
            return base64.b64encode(image.read()).decode("utf-8")

    def _post_playlist(self, user_id, playlist_data):
        """
        Post a playlist to Spotify.
        :param user_id: The Spotify user ID.
        :param playlist_data: A dictionary containing playlist data.
        :return: The response from the Spotify API.
        """

        return self.spotify_api.post_playlist(user_id, playlist_data)

    def _post_playlist_tracks(self, playlist_id, track_uris):
        """
        Add tracks to a Spotify playlist.
        :param playlist_id: The Spotify playlist ID.
        :param track_uris: A list of Spotify track URIs.
        :return: The response from the Spotify API.
        """

        print(track_uris)
        return self.spotify_api.post_tracks(playlist_id, track_uris)

    def _post_image(self, playlist_id, image_data):
        """
        Add a cover image to a Spotify playlist.
        :param playlist_id: The Spotify playlist ID.
        :param image_data: The base64-encoded image data.
        """

        return self.spotify_api.post_image(playlist_id, image_data)

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=line-too-long
    # pylint: disable=too-many-function-args
    # pylint: disable=too-many-locals
    def push_playlist(self, playlist_id: str, name: str, description: str, public: bool, image: str):
        """
        Push a playlist to Spotify.

        :param playlist_id: The unique identifier for the playlist.
        """

        try:
            playlist = self.db.fetch_playlists(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found.")

            tracks = self.db.fetch_tracks(playlist_id)
            if not tracks:
                raise ValueError(f"No tracks found for playlist with ID {playlist_id}.")

            if image:
                image_data = self._encode_image(image)

            user_id = self._get_user_id()
            playlist_data = {
                "name": name,
                "description": description,
                "public": public,
            }

            response_create_playlist = self._post_playlist(user_id, playlist_data)
            if response_create_playlist:
                playlist_id = response_create_playlist["id"]
                playlist_url = response_create_playlist["external_urls"]["spotify"]
                print(f"Playlist created with ID {playlist_id}.")
                print(f"Playlist URL: {playlist_url}")

            track_uris = [track.track_uri for track in tracks]
            response_add_tracks = self._post_playlist_tracks(playlist_id, track_uris)
            if response_add_tracks:
                print(f"Added {len(track_uris)} tracks to the playlist.")

            if image:
                self._post_image(playlist_id, image_data)
                print("Cover image added to the playlist.")

        except Exception as e:
            raise RuntimeError(f"Failed to push playlist: {e}") from e


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

    if not description:
        prompt = "Enter a description for the new playlist"
        description = click.prompt(prompt, type=str)

    push_manager.push_playlist(playlist_id, name, description, public, image)
