#!/usr/bin/env python

"""
CLI command for comparing the contents of a playlist in the database with the
current state of the playlist on Spotify.
"""

import json

import click

from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI
from jamjar.utils import extract_playlist_id

CONFIG = Config()


# pylint: disable=too-few-public-methods
class DiffManager:
    """
    Handles the logic for comparing the contents of a playlist in the database
    with the current state of the playlist on Spotify. The diff will be shown
    in JSON, mimicking code changes.
    """

    def __init__(self, db: Database, spotify_api):
        self.db = db
        self.spotify_api = spotify_api

    def _fetch_spotify_playlist_tracks(self, playlist_id):
        """
        Fetch all tracks from a Spotify playlist.
        :param playlist_id: Spotify playlist ID.
        :return: List of track data as tuples (track_id, name, artist).
        """
        try:
            response = self.spotify_api.get_playlist_tracks(playlist_id)
            items = response.get("items", [])
            tracks = [
                {
                    "id": item["track"]["id"],
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "added_by": item["added_by"]["id"],
                    "added_on": item["added_at"],
                }
                for item in items
            ]

            return tracks
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Spotify playlist tracks: {e}") from e

    def _fetch_database_playlist_tracks(self, playlist_id):
        """
        Fetch all tracks from a playlist stored in the database.
        :param playlist_id: Playlist ID.
        :return: List of track data as dictionaries (track_id, name, artist).
        """
        try:
            db_tracks = self.db.fetch_playlist_tracks(playlist_id)
            db_tracks = [
                {
                    "id": track[1],
                    "name": track[2],
                    "artist": track[3],
                    "added_by": track[4],
                    "added_on": track[5],
                }
                for track in db_tracks
            ]

            return db_tracks
        except Exception as e:
            raise RuntimeError(f"Failed to fetch database playlist tracks: {e}") from e

    def _generate_diff_json(self, db_tracks, spotify_tracks):
        """
        Generate a JSON-like diff between two track lists.
        :param db_tracks: List of tracks from the database.
        :param spotify_tracks: List of tracks from Spotify.
        :return: JSON diff with 'added' and 'removed' sections.
        """
        try:
            db_track_ids = {track["id"] for track in db_tracks}
            spotify_track_ids = {track["id"] for track in spotify_tracks}

            added_track_ids = spotify_track_ids - db_track_ids
            removed_track_ids = db_track_ids - spotify_track_ids

            added_tracks = [track for track in spotify_tracks if track["id"] in added_track_ids]
            removed_tracks = [track for track in db_tracks if track["id"] in removed_track_ids]

            return {"added": added_tracks, "removed": removed_tracks}
        except Exception as e:
            raise RuntimeError(f"Failed to generate diff: {e}") from e

    def _generate_playlist_metadata_diff(self, db_playlist, spotify_playlist):
        """
        Generate a JSON-like diff for metadata differences between two playlists.
        :param db_playlist: Playlist metadata from the database.
        :param spotify_playlist: Playlist metadata from Spotify.
        :return: JSON diff with 'metadata_changed' section.
        """
        try:
            db_values = {
                "id": db_playlist[0][0],
                "name": db_playlist[0][1],
                "description": db_playlist[0][2],
                "owner": db_playlist[0][3],
                "url": db_playlist[0][4],
            }

            spotify_values = {
                "id": spotify_playlist["id"],
                "name": spotify_playlist["name"],
                "description": spotify_playlist["description"],
                "owner": spotify_playlist["owner"]["id"],
                "url": spotify_playlist["external_urls"]["spotify"],
            }

            metadata_diff = {}
            for item in db_values.items():
                key, value = item
                if value != spotify_values[key]:
                    metadata_diff[key] = {"db": value, "spotify": spotify_values[key]}

            if metadata_diff:
                return {"metadata_changed": metadata_diff}

            return {"metadata_changed": None}
        except Exception as e:
            raise RuntimeError(f"Failed to generate metadata diff: {e}") from e

    def _format_diff_json(self, _diff):
        """
        Format the diff as a JSON string.
        :param diff: Dictionary with 'added' and 'removed' tracks.
        :return: JSON string.
        """
        try:
            return json.dumps(_diff, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to format diff JSON: {e}") from e

    def diff_playlist(self, playlist_identifier, detailed=False):
        """
        Perform the diff operation for a given playlist and return the results as JSON.
        :param playlist_identifier: Playlist ID or URL.
        :param detailed: Whether to include detailed information in the diff.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            db_tracks = self._fetch_database_playlist_tracks(playlist_id)
            spotify_tracks = self._fetch_spotify_playlist_tracks(playlist_id)
            _diff = self._generate_diff_json(db_tracks, spotify_tracks)

            if detailed:
                db_playlist = self.db.fetch_playlist_by_id(playlist_id)
                spotify_playlist = self.spotify_api.get_playlist(playlist_id)
                metadata_diff = self._generate_playlist_metadata_diff(db_playlist, spotify_playlist)
                _diff.update(metadata_diff)

            return self._format_diff_json(_diff)
        except Exception as e:
            raise RuntimeError(f"Failed to diff playlist: {e}") from e


# pylint: disable=line-too-long
@click.command()
@click.help_option("--help", "-h")
@click.option("--details", "-d", is_flag=True, help="Show detailed differences, including metadata changes.")
@click.argument("playlist")
def diff(playlist, details):
    """
    Compares playlist state between database and Spotify.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    diff_manager = DiffManager(db, spotify_api)
    print(diff_manager.diff_playlist(playlist, details))
