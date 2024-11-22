#!/usr/bin/env python

"""
CLI command for adding a Spotify playlist to the JamJar database.

This module facilitates adding a Spotify playlist (via URL or ID) and its tracks
to the JamJar database, ensuring all playlist metadata and tracks are properly stored.
"""

import click

from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI
from jamjar.utils import extract_playlist_id

CONFIG = Config()


class AddManager:
    """
    Handles adding Spotify playlists and tracks to the JamJar database.

    This class provides methods to:
    - Fetch playlist and track data from Spotify.
    - Add playlist metadata to the database.
    - Add individual tracks from a playlist to the database.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        """
        Initialize the AddManager with database and Spotify API instances.

        :param db: An instance of the Database class for database operations.
        :param spotify_api: An instance of the SpotifyAPI class for Spotify interactions.
        """

        self.db = db
        self.spotify_api = spotify_api

    def _get_playlist_data(self, playlist_id):
        """
        Fetch details of a Spotify playlist using its ID.

        :param playlist_id: The Spotify playlist ID.
        :return: A dictionary containing playlist details fetched from Spotify.
        """

        return self.spotify_api.get_playlist(playlist_id)

    # pylint: disable=too-many-locals
    def add_tracks_to_db(self, playlist_id: str, tracks_data: str, action="Added"):
        """
        Add tracks from a Spotify playlist to the database.

        :param playlist_id: The Spotify playlist ID.
        :param tracks_data: A dictionary containing track data fetched from Spotify.
        :param action: A string describing the action being performed (default: "Added").
        """

        for track_item in tracks_data["items"]:
            track_id = track_item["track"]["id"]
            if not track_id:
                continue

            track_name = track_item["track"]["name"]
            track_url = track_item["track"]["external_urls"]["spotify"]
            track_uri = track_item["track"]["uri"]
            preview_url = track_item["track"].get("preview_url", "")
            track_popularity = track_item["track"].get("popularity", 0)
            album_id = track_item["track"]["album"]["id"]
            album_name = track_item["track"]["album"]["name"]
            album_url = track_item["track"]["album"]["external_urls"]["spotify"]
            artist_id = track_item["track"]["artists"][0]["id"]
            artist_name = track_item["track"]["artists"][0]["name"]
            artist_url = track_item["track"]["artists"][0]["external_urls"]["spotify"]
            is_explicit = track_item["track"].get("explicit", False)
            is_local = track_item["track"].get("is_local", False)
            disc_number = track_item["track"].get("disc_number", 0)
            isrc_code = track_item["track"].get("external_ids", {}).get("isrc", "")
            user_added = track_item.get("added_by", {}).get("id", "")
            time_added = track_item.get("added_at", "")

            self.db.add_track(
                track_id,
                track_name,
                track_url,
                track_uri,
                preview_url,
                track_popularity,
                album_id,
                album_name,
                album_url,
                artist_id,
                artist_name,
                artist_url,
                is_explicit,
                is_local,
                disc_number,
                isrc_code,
                playlist_id,
                user_added,
                time_added,
            )

            print(f"{action} track '{track_name}' by '{artist_name}'.")

    def add_playlist_to_db(self, playlist_id, playlist_data, action="Added"):
        """
        Add playlist metadata to the database.

        :param playlist_id: The Spotify playlist ID.
        :param playlist_data: A dictionary containing playlist metadata fetched from Spotify.
        :param action: A string describing the action being performed (default: "Added").
        """

        name = playlist_data.get("name", "Unknown Playlist")
        owner_id = playlist_data.get("owner", {}).get("id", "unknown_owner_owner")
        owner_name = playlist_data.get("owner", {}).get("display_name", "Unknown Owner")
        owner_url = playlist_data.get("owner", {}).get("external_urls", {}).get("spotify", "")
        description = playlist_data.get("description", "")
        url = playlist_data["external_urls"]["spotify"]
        public = playlist_data.get("public", False)
        followers_total = playlist_data.get("followers", {}).get("total", 0)
        snapshot_id = playlist_data.get("snapshot_id", "")
        playlist_image_url = playlist_data.get("images", [{}])[0].get("url", "")
        track_count = playlist_data.get("tracks", {}).get("total", 0)
        colaborative = playlist_data.get("collaborative", False)

        self.db.add_playlist(
            playlist_id,
            name,
            owner_id,
            owner_name,
            owner_url,
            description,
            url,
            snapshot_id,
            playlist_image_url,
            followers_total,
            track_count,
            public,
            colaborative,
        )

        print(f"{action} metadata of playlist '{name}' to database.")

    def add_playlist(self, playlist_identifier):
        """
        Add a Spotify playlist to the database by URL or ID.

        Fetches playlist metadata and tracks from Spotify, then stores them in the database.

        :param playlist_identifier: A Spotify playlist URL or ID.
        :raises RuntimeError: If an error occurs during the addition process.
        """

        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            print("Adding playlist to the database...")

            playlist_data = self._get_playlist_data(playlist_id)
            self.add_playlist_to_db(playlist_id, playlist_data)

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            self.add_tracks_to_db(playlist_id, tracks_data)

            playlist_name = playlist_data.get("name", "Unknown Playlist")
            print(f"Playlist '{playlist_name}' added with tracks successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to add playlist: {e}") from e


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def add(playlist):
    """
    Add a Spotify playlist to the database.

    This command accepts a Spotify playlist URL or ID and stores its metadata
    and tracks in the JamJar database.

    :param playlist: The Spotify playlist URL or ID.
    """

    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    add_manager = AddManager(db, spotify_api)

    add_manager.add_playlist(playlist)
