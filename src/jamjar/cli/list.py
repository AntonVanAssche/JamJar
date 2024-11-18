#!/usr/bin/env python

"""
CLI command to list playlists or tracks in a specific playlist.

This module handles listing all playlists stored in the JamJar database,
and listing all tracks in a specific playlist.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database
from jamjar.utils import extract_playlist_id, format_json_output

CONFIG = Config()


# pylint: disable=too-few-public-methods
class ListManager:
    """
    Handles the logic for listing playlists and tracks.

    This includes fetching playlists and tracks from the database and
    formatting the output for display.
    """

    def __init__(self, db: Database):
        self.db = db

    def list_playlists(self):
        """
        List all playlists stored in the database with specific fields.
        """
        try:
            playlists = self.db.fetch_playlists()
            if not playlists:
                print(json.dumps({"message": "No playlists found."}, indent=2))
                return

            headers = [
                "playlist_id",
                "playlist_name",
                "owner_id",
                "owner_name",
                "owner_url",
                "playlist_url",
                "description",
                "public",
                "followers_total",
                "snapshot_id",
                "playlist_image_url",
                "track_count",
                "colaborative",
            ]
            playlists_data = [
                {
                    "playlist_id": playlist.playlist_id,
                    "playlist_name": playlist.playlist_name,
                    "owner_id": playlist.owner_id,
                    "owner_name": playlist.owner_name,
                    "owner_url": playlist.owner_url,
                    "playlist_url": playlist.playlist_url,
                    "description": playlist.description,
                    "public": playlist.public,
                    "followers_total": playlist.followers_total,
                    "snapshot_id": playlist.snapshot_id,
                    "playlist_image_url": playlist.playlist_image_url,
                    "track_count": playlist.track_count,
                    "colaborative": playlist.colaborative,
                }
                for playlist in playlists
            ]

            print(format_json_output("playlists", headers, playlists_data))
        except Exception as e:
            raise RuntimeError(f"Failed to list playlists: {e}") from e

    def list_tracks(self, playlist_id):
        """
        List all tracks in a specific playlist with specific fields.
        """
        try:
            playlist_id = extract_playlist_id(playlist_id)
            tracks = self.db.fetch_playlist_tracks(playlist_id)
            if not tracks:
                # pylint: disable=line-too-long
                print(json.dumps({"message": f"No tracks found for playlist ID '{playlist_id}'."}, indent=2))
                return

            headers = [
                "track_id",
                "track_name",
                "track_url",
                "preview_url",
                "track_popularity",
                "album_id",
                "album_name",
                "album_url",
                "artist_id",
                "artist_name",
                "artist_url",
                "is_explicit",
                "is_local",
                "disc_number",
                "isrc_code",
                "playlist_id",
                "user_added",
                "time_added",
            ]
            tracks_data = [
                {
                    "track_id": track.track_id,
                    "track_name": track.track_name,
                    "track_url": track.track_url,
                    "preview_url": track.preview_url,
                    "track_popularity": track.track_popularity,
                    "album_id": track.album_id,
                    "album_name": track.album_name,
                    "album_url": track.album_url,
                    "artist_id": track.artist_id,
                    "artist_name": track.artist_name,
                    "artist_url": track.artist_url,
                    "is_explicit": track.is_explicit,
                    "is_local": track.is_local,
                    "disc_number": track.disc_number,
                    "isrc_code": track.isrc_code,
                    "playlist_id": track.playlist_id,
                    "user_added": track.user_added,
                    "time_added": track.time_added,
                }
                for track in tracks
            ]

            print(format_json_output("tracks", headers, tracks_data))
        except Exception as e:
            raise RuntimeError(f"Failed to list tracks: {e}") from e


# pylint: disable=redefined-builtin
@click.command()
@click.help_option("--help", "-h")
@click.option("--playlist", "-p", help="ID, or URL, of the playlist to list tracks for.")
def list(playlist=None):
    """
    List playlists or tracks in a specific playlist.

    Without options, lists all playlists.
    Use --playlist to list tracks in a specific playlist.
    """
    db = Database(CONFIG)
    list_manager = ListManager(db)

    if playlist:
        list_manager.list_tracks(playlist)
    else:
        list_manager.list_playlists()
