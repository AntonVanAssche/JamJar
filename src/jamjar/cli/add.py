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

    # pylint: disable=too-many-locals
    def add_tracks_to_db(self, playlist_id: str, tracks_data: str, action="Added"):
        """
        Adds tracks from a playlist to the database.
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
        Adds the playlist's data to the database.
        """
        name = playlist_data.get("name", "Unknown Playlist")
        owner = playlist_data.get("owner", {}).get("", "Unknown Owner")
        owner_id = playlist_data.get("owner", {}).get("id", "unknown_owner_owner")
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
            owner,
            owner_id,
            owner_url,
            description,
            url,
            public,
            followers_total,
            snapshot_id,
            playlist_image_url,
            track_count,
            colaborative,
        )

        print(f"{action} metadata of playlist '{name}' to database.")

    def add_playlist(self, playlist_identifier):
        """
        AddManager a playlist to the database.

        Accepts either a full Spotify playlist URL or just a playlist ID.
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
    Command for adding a playlist to the database.

    Accepts either a Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    add_manager = AddManager(db, spotify_api)

    add_manager.add_playlist(playlist)
