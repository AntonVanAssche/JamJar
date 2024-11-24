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

    def _get_user_id(self) -> str:
        """
        Fetch the Spotify user ID.

        :return: The Spotify user ID.
        """

        return self.spotify_api.get_user_id()

    def _get_playlist_data(self, playlist_id: str) -> dict:
        """
        Fetch details of a Spotify playlist using its ID.

        :param playlist_id: The Spotify playlist ID.
        :return: A dictionary containing playlist details fetched from Spotify.
        """

        return self.spotify_api.get_playlist(playlist_id)

    def _get_playlist_tracks(self, playlist_id: str) -> dict:
        """
        Fetch tracks of a Spotify playlist using its ID.

        :param playlist_id: The Spotify playlist ID.
        :return: A dictionary containing track details fetched from Spotify.
        """

        return self.spotify_api.get_playlist_tracks(playlist_id)

    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64.

        :param image_path: The path to the image file.
        :return: The base64-encoded image.
        """

        with open(image_path, "rb") as image:
            return base64.b64encode(image.read()).decode("utf-8")

    def _post_playlist(self, user_id: str, playlist_data: dict) -> dict:
        """
        Post a playlist to Spotify.

        :param user_id: The Spotify user ID.
        :param playlist_data: A dictionary containing playlist data.
        :return: The response from the Spotify API.
        """

        return self.spotify_api.post_playlist(user_id, playlist_data)

    def _post_playlist_tracks(self, playlist_id: str, track_uris: str) -> dict:
        """
        Add tracks to a Spotify playlist.

        :param playlist_id: The Spotify playlist ID.
        :param track_uris: A list of Spotify track URIs.
        :return: The response from the Spotify API.
        """

        return self.spotify_api.post_tracks(playlist_id, track_uris)

    def _post_image(self, playlist_id: str, image_data: str) -> dict:
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
    def push_playlist(self, playlist_id: str, name: str, description: str, public: bool, image: str) -> dict:
        """
        Push a playlist to Spotify.

        :param playlist_id: The unique identifier for the playlist.
        :param name: The desired name of the playlist on Spotify.
        :param description: A description for the playlist.
        :param public: Whether the playlist should be public.
        :param image: Path to an image file for the playlist cover.
        :return: A dictionary summarizing the actions performed.
        """
        try:
            playlist = self.db.fetch_playlists(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found.")

            tracks = self.db.fetch_tracks(playlist_id)
            if not tracks:
                raise ValueError(f"No tracks found for playlist with ID {playlist_id}.")

            user_id = self._get_user_id()
            playlist_data = {
                "name": name,
                "description": description,
                "public": public,
            }

            response_create_playlist = self._post_playlist(user_id, playlist_data)
            if not response_create_playlist:
                raise RuntimeError("Failed to create playlist on Spotify.")

            playlist_id = response_create_playlist["id"]
            playlist_url = response_create_playlist["external_urls"]["spotify"]

            track_uris = [track.track_uri for track in tracks]
            response_add_tracks = self._post_playlist_tracks(playlist_id, track_uris)
            if not response_add_tracks:
                raise RuntimeError("Failed to add tracks to the playlist.")

            return_message = {
                "playlist_id": playlist_id,
                "playlist_url": playlist_url,
                "track_count": len(track_uris),
                "public": public,
                "image_uploaded": False,
            }

            if image:
                image_data = self._encode_image(image)
                response_add_image = self._post_image(playlist_id, image_data)

                if not response_add_image:
                    raise RuntimeError("Failed to upload cover image to the playlist.")

                return_message["image_uploaded"] = True

            return return_message

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

    try:
        result = push_manager.push_playlist(playlist_id, name, description, public, image)
        print(f"Playlist created: {result['playlist_url']}")
        print(f"Tracks added: {result['track_count']}")
        print(f"Public: {result['public']}")
        print(f"Cover image uploaded: {result['image_uploaded']}")
    except RuntimeError as e:
        print(f"Error: {e}")
