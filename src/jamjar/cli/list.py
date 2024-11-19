#!/usr/bin/env python

"""
A command-line interface (CLI) tool for listing playlists and tracks present in the
JamJar database.

This module allows users to list all playlists stored in the JamJar database,
or to list all tracks in a specific playlist, by fetching data from the database
and displaying it in a structured format.
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
    Manages the logic for listing playlists and tracks.

    This class provides methods to list all playlists stored in the database
    or to list all tracks within a specific playlist. It formats the output
    into JSON for easy display.
    """

    def __init__(self, db: Database):
        """
        Initialize the DiffManager with the necessary database instance.

        :param db: Database instance for fetching playlist and track data.
        """

        self.db = db

    def list_playlists(self):
        """
        Retrieves and displays all playlists stored in the database.

        Fetches all playlists from the database and prints their details, including
        the playlist's name, ID, owner, track count, and more. If no playlists are found,
        a message is displayed indicating that no playlists are available.
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
        Retrieves and displays all tracks in a specific playlist.

        Fetches all tracks from a specified playlist ID and prints their details,
        such as track name, artist, album, popularity, and more. If no tracks are
        found for the given playlist ID, a message is displayed indicating no tracks.

        :param playlist_id: The ID or URL of the playlist to list tracks from.
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
                "track_uri",
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
                    "track_uri": track.track_uri,
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
    Lists all playlists or tracks in a specific playlist.

    When no playlist option is provided, this command lists all playlists in the
    database. If the --playlist option is provided with a valid playlist ID or URL,
    it will list all tracks in that specific playlist.

    :param playlist: Optional ID or URL of a playlist to list tracks from.
    """

    db = Database(CONFIG)
    list_manager = ListManager(db)

    if playlist:
        list_manager.list_tracks(playlist)
    else:
        list_manager.list_playlists()
