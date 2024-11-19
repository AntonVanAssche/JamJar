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
from jamjar.dataclasses import Track
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

    def _fetch_spotify_playlist_tracks(self, playlist_id: str):
        """
        Fetch all tracks from a Spotify playlist.
        :param playlist_id: Spotify playlist ID.
        :return: List of Track objects from Spotify.
        """
        try:
            response = self.spotify_api.get_playlist_tracks(playlist_id)
            items = response.get("items", [])
            tracks = []

            # pylint: disable=line-too-long
            for item in items:
                track = Track(
                    track_id=item["track"]["id"],
                    track_name=item["track"]["name"],
                    track_url=item["track"]["external_urls"].get("spotify", None),
                    track_uri=item["track"]["uri"],
                    preview_url=item["track"].get("preview_url"),
                    track_popularity=item["track"]["popularity"],
                    album_id=item["track"]["album"]["id"],
                    album_name=item["track"]["album"]["name"],
                    album_url=item["track"]["album"].get("external_urls", {}).get("spotify", None),
                    artist_id=item["track"]["artists"][0]["id"],
                    artist_name=item["track"]["artists"][0]["name"],
                    artist_url=item["track"]["artists"][0].get("external_urls", {}).get("spotify", None),
                    is_explicit=item["track"]["explicit"],
                    is_local=item["track"].get("is_local", False),
                    disc_number=item["track"].get("disc_number", 1),
                    isrc_code=item["track"].get("external_ids", {}).get("isrc", ""),
                    playlist_id=playlist_id,
                    user_added=item.get("added_by", {}).get("id", ""),
                    time_added=item["added_at"],
                )
                tracks.append(track)
            return tracks
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Spotify playlist tracks: {e}") from e

    def _fetch_database_playlist_tracks(self, playlist_id: str):
        """
        Fetch all tracks from a playlist stored in the database.
        :param playlist_id: Playlist ID.
        :return: List of Track objects from the database.
        """
        try:
            db_tracks = self.db.fetch_playlist_tracks(playlist_id)
            return db_tracks
        except Exception as e:
            raise RuntimeError(f"Failed to fetch database playlist tracks: {e}") from e

    def _generate_diff_json(self, db_tracks, spotify_tracks):
        """
        Generate a JSON-like diff between two track lists.
        :param db_tracks: List of Track objects from the database.
        :param spotify_tracks: List of Track objects from Spotify.
        :return: JSON diff with 'added' and 'removed' sections.
        """
        try:
            db_track_ids = {track.track_id for track in db_tracks}
            spotify_track_ids = {track.track_id for track in spotify_tracks}

            added_track_ids = spotify_track_ids - db_track_ids
            removed_track_ids = db_track_ids - spotify_track_ids

            added_tracks = [track for track in spotify_tracks if track.track_id in added_track_ids]
            removed_tracks = [track for track in db_tracks if track.track_id in removed_track_ids]

            return {
                "added": [track.__dict__ for track in added_tracks],
                "removed": [track.__dict__ for track in removed_tracks],
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate diff: {e}") from e

    def _generate_playlist_metadata_diff(self, db_playlist, spotify_playlist):
        """
        Generate a JSON-like diff for metadata differences between two playlists.
        :param db_playlist: Playlist object from the database.
        :param spotify_playlist: Playlist metadata from Spotify.
        :return: JSON diff with 'metadata_changed' section.
        """
        try:
            db_values = {
                "playlist_id": db_playlist.playlist_id,
                "playlist_name": db_playlist.playlist_name,
                "owner_id": db_playlist.owner_id,
                "owner_name": db_playlist.owner_name,
                "owner_url": db_playlist.owner_url,
                "playlist_url": db_playlist.playlist_url,
                "description": db_playlist.description,
                "public": db_playlist.public,
                "followers_total": db_playlist.followers_total,
                "snapshot_id": db_playlist.snapshot_id,
                "playlist_image_url": db_playlist.playlist_image_url,
                "track_count": db_playlist.track_count,
                "colaborative": db_playlist.colaborative,
            }

            spotify_values = {
                "playlist_id": spotify_playlist.playlist_id,
                "playlist_name": spotify_playlist.playlist_name,
                "owner_id": spotify_playlist.owner_id,
                "owner_name": spotify_playlist.owner_name,
                "owner_url": spotify_playlist.owner_url,
                "playlist_url": spotify_playlist.playlist_url,
                "description": spotify_playlist.description,
                "public": spotify_playlist.public,
                "followers_total": spotify_playlist.followers_total,
                "snapshot_id": spotify_playlist.snapshot_id,
                "playlist_image_url": spotify_playlist.playlist_image_url,
                "track_count": spotify_playlist.track_count,
                "colaborative": spotify_playlist.colaborative,
            }

            metadata_diff = {}
            for key, value in db_values.items():
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
            db_playlist = self.db.fetch_playlist_by_id(playlist_id)
            spotify_playlist = self.spotify_api.get_playlist(playlist_id)

            db_tracks = self._fetch_database_playlist_tracks(playlist_id)
            spotify_tracks = self._fetch_spotify_playlist_tracks(playlist_id)

            _diff = self._generate_diff_json(db_tracks, spotify_tracks)

            if detailed:
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
