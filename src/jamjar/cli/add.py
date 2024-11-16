#!/usr/bin/env python

"""
CLI command for adding a playlist to the database.

This module handles adding a playlist (by URL or ID) to the JamJar database,
including all of its tracks.
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
    Handles the logic for adding a Spotify playlist and its tracks to the database.

    This includes extracting playlist information and adding both the playlist and
    its tracks to the database.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def _get_playlist_data(self, playlist_id):
        """
        Fetches the playlist details from Spotify using the playlist ID.
        """
        return self.spotify_api.get_playlist(playlist_id)

    def add_tracks(self, db: Database, playlist_id: str, tracks_data: str, action="Added"):
        """
        Adds tracks from a playlist to the database.
        """
        for track_item in tracks_data["items"]:
            track = track_item["track"]
            track_id = track.get("id")
            if not track_id:
                continue

            track_name = track.get("name", "Unknown Track")
            track_artist = ", ".join(artist["name"] for artist in track["artists"])
            track_url = track["external_urls"]["spotify"]
            track_user_added = track_item.get("added_by", {}).get("id", "Unknown User")
            track_time_added = track_item.get("added_at")

            db.add_track(
                playlist_id,
                track_id,
                track_name,
                track_artist,
                track_url,
                track_user_added,
                track_time_added,
            )
            print(f"{action} track '{track_name}' by '{track_artist}'.")

    def _add_playlist_to_db(self, playlist_id, playlist_data):
        """
        Adds the playlist's data to the database.
        """
        name = playlist_data.get("name", "Unknown Playlist")
        owner = playlist_data.get("owner", {}).get("id", "Unknown User")
        description = playlist_data.get("description", "")
        url = playlist_data["external_urls"]["spotify"]

        self.db.add_playlist(playlist_id, name, owner, description, url)

    def add_playlist(self, playlist_identifier):
        """
        AddManager a playlist to the database.

        Accepts either a full Spotify playlist URL or just a playlist ID.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            print("Adding playlist to the database...")

            playlist_data = self._get_playlist_data(playlist_id)
            self._add_playlist_to_db(playlist_id, playlist_data)

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            self.add_tracks(self.db, playlist_id, tracks_data)

            playlist_name = playlist_data.get("name", "Unknown Playlist")
            print(f"Playlist '{playlist_name}' added with tracks successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to add playlist: {e}") from e


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def add(playlist):
    """
    Command for adding a playlist to the database.

    Accepts either a Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    add_manager = AddManager(db, spotify_api)

    add_manager.add_playlist(playlist)
