#!/usr/bin/env python

"""
CLI command for adding a Spotify playlist to the JamJar database.

This module facilitates adding a Spotify playlist (via URL or ID) and its tracks
to the JamJar database, ensuring all playlist metadata and tracks are properly stored.
"""

from jamjar.core.database import Database
from jamjar.core.spotify import SpotifyAPI
from jamjar.core.utils import extract_playlist_id


class AddError(Exception):
    """Exception raised for errors in the AddManager class."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


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

    def add_tracks_to_db(self, playlist_id: str, tracks_data: str) -> dict:
        """
        Add tracks from a Spotify playlist to the database.

        :param playlist_id: The Spotify playlist ID.
        :param tracks_data: A dictionary containing track data fetched from Spotify.
        :return: A summary of the operation.
        """

        added_tracks = []
        for track_item in tracks_data.get("items", []):
            track = track_item.get("track")
            if not track or not track.get("id"):
                continue

            track_info = {
                "track_id": track["id"],
                "track_name": track["name"],
                "artist_name": track["artists"][0]["name"],
                "album_name": track["album"]["name"],
                "url": track["external_urls"]["spotify"],
            }

            try:
                self.db.add_track(
                    track_id=track_info["track_id"],
                    track_name=track_info["track_name"],
                    track_url=track_info["url"],
                    track_uri=track["uri"],
                    preview_url=track.get("preview_url", ""),
                    track_popularity=track.get("popularity", 0),
                    album_id=track["album"]["id"],
                    album_name=track_info["album_name"],
                    album_url=track["album"]["external_urls"]["spotify"],
                    artist_id=track["artists"][0]["id"],
                    artist_name=track_info["artist_name"],
                    artist_url=track["artists"][0]["external_urls"]["spotify"],
                    is_explicit=track.get("explicit", False),
                    is_local=track.get("is_local", False),
                    disc_number=track.get("disc_number", 0),
                    isrc_code=track.get("external_ids", {}).get("isrc", ""),
                    playlist_id=playlist_id,
                    user_added=track_item.get("added_by", {}).get("id", ""),
                    time_added=track_item.get("added_at", ""),
                )

                added_tracks.append(track_info)
            except Exception as e:
                raise AddError(f"Failed to add track '{track_info['track_name']}': {e}") from e

        return {"status": "success", "added_tracks": added_tracks}

    def add_playlist_to_db(self, playlist_id: str, playlist_data: dict) -> dict:
        """
        Add playlist metadata to the database.

        :param playlist_id: The Spotify playlist ID.
        :param playlist_data: A dictionary containing playlist metadata fetched from Spotify.
        :return: A summary of the operation.
        """

        try:
            playlist_info = {
                "playlist_id": playlist_id,
                "name": playlist_data.get("name", "Unknown Playlist"),
                "description": playlist_data.get("description", ""),
                "owner_name": playlist_data.get("owner", {}).get("display_name", "Unknown Owner"),
                "url": playlist_data["external_urls"]["spotify"],
                "track_count": playlist_data.get("tracks", {}).get("total", 0),
            }

            # pylint: disable=line-too-long
            self.db.add_playlist(
                playlist_id=playlist_id,
                name=playlist_info["name"],
                owner_id=playlist_data.get("owner", {}).get("id", ""),
                owner_name=playlist_info["owner_name"],
                owner_url=playlist_data.get("owner", {}).get("external_urls", {}).get("spotify", ""),
                description=playlist_info["description"],
                url=playlist_info["url"],
                snapshot_id=playlist_data.get("snapshot_id", ""),
                playlist_image_url=playlist_data.get("images", [{}])[0].get("url", ""),
                followers_total=playlist_data.get("followers", {}).get("total", 0),
                track_count=playlist_info["track_count"],
                public=playlist_data.get("public", False),
                colaborative=playlist_data.get("collaborative", False),
            )

            return {"status": "success", "playlist": playlist_info}
        except Exception as e:
            raise AddError(f"Failed to add playlist metadata: {e}") from e

    def add_playlist(self, playlist_identifier: str) -> dict:
        """
        Add a Spotify playlist to the database by URL or ID.

        :param playlist_identifier: A Spotify playlist URL or ID.
        :return: A summary of the operation.
        :raises AddError: If an error occurs during the addition process.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            playlist_data = self._get_playlist_data(playlist_id)

            playlist_summary = self.add_playlist_to_db(playlist_id, playlist_data)
            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            tracks_summary = self.add_tracks_to_db(playlist_id, tracks_data)

            return {
                "status": "created",
                "playlist_summary": playlist_summary,
                "tracks_summary": tracks_summary,
            }
        except Exception as e:
            raise AddError(f"Failed to add playlist '{playlist_identifier}': {e}") from e
