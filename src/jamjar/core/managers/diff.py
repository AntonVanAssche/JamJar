#!/usr/bin/env python

"""
CLI command for comparing the contents of a playlist in the database with the current
state of the playlist on Spotify.

This modules allows users to compare the playlist data between the JamJar database
and the actual Spotify playlist. It generates a JSON diff of the differences in
tracks and metadata.
"""

from jamjar.core.database import Database
from jamjar.core.dataclasses import Playlist, Track
from jamjar.core.spotify import SpotifyAPI
from jamjar.core.utils import extract_playlist_id


class DiffError(Exception):
    """Exception raised for errors in the DiffManager."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# pylint: disable=too-few-public-methods
class DiffManager:
    """
    Manages the comparison of playlist data between the JamJar database and Spotify.

    This class handles:
    - Fetching playlist and track data from both Spotify and the database.
    - Generating a diff between the two sources.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        """
        Initialize the DiffManager with the necessary database and Spotify API instances.
        """
        self.db = db
        self.spotify_api = spotify_api

    def _fetch_spotify_playlist_tracks(self, playlist_id: str) -> list[Track]:
        """
        Fetch all tracks from a Spotify playlist using the provided playlist ID.

        :param playlist_id: The ID of the Spotify playlist to fetch tracks for.
        :return: A list of Track objects representing the tracks in the playlist.
        """

        try:
            response = self.spotify_api.get_playlist_tracks(playlist_id)
            items = response.get("items", [])
            return [
                Track(
                    track_id=item["track"]["id"],
                    track_name=item["track"]["name"],
                    track_url=item["track"]["external_urls"].get("spotify"),
                    track_uri=item["track"]["uri"],
                    preview_url=item["track"].get("preview_url"),
                    track_popularity=item["track"]["popularity"],
                    album_id=item["track"]["album"]["id"],
                    album_name=item["track"]["album"]["name"],
                    album_url=item["track"]["album"].get("external_urls", {}).get("spotify"),
                    artist_id=item["track"]["artists"][0]["id"],
                    artist_name=item["track"]["artists"][0]["name"],
                    artist_url=item["track"]["artists"][0].get("external_urls", {}).get("spotify"),
                    is_explicit=item["track"]["explicit"],
                    is_local=item["track"].get("is_local", False),
                    disc_number=item["track"].get("disc_number", 1),
                    isrc_code=item["track"].get("external_ids", {}).get("isrc", ""),
                    playlist_id=playlist_id,
                    user_added=item.get("added_by", {}).get("id", ""),
                    time_added=item["added_at"],
                )
                for item in items
            ]
        except Exception as e:
            raise DiffError(f"Error fetching Spotify playlist tracks: {e}") from e

    def _fetch_spotify_playlist_metadata(self, playlist_id: str) -> Playlist:
        """
        Fetch metadata for a Spotify playlist using the provided playlist ID.

        :param playlist_id: The ID of the Spotify playlist to fetch metadata for.
        :return: A Playlist object with the playlist metadata.
        """

        try:
            response = self.spotify_api.get_playlist(playlist_id)
            return Playlist(
                playlist_id=response["id"],
                playlist_name=response["name"],
                owner_id=response["owner"]["id"],
                owner_name=response["owner"]["display_name"],
                owner_url=response["owner"]["external_urls"].get("spotify"),
                playlist_url=response["external_urls"].get("spotify"),
                description=response["description"],
                public=response["public"],
                followers_total=response["followers"]["total"],
                snapshot_id=response["snapshot_id"],
                playlist_image_url=response["images"][0]["url"] if response["images"] else None,
                track_count=response["tracks"]["total"],
                colaborative=response["collaborative"],
            )
        except Exception as e:
            raise DiffError(f"Error fetching Spotify playlist metadata: {e}") from e

    def _fetch_database_playlist_tracks(self, playlist_id: str) -> list:
        """
        Fetch all tracks from a playlist stored in the JamJar database.

        :param playlist_id: The ID of the playlist to fetch tracks for.
        :return: A list of Track objects representing the tracks in the playlist.
        """

        try:
            return self.db.fetch_tracks(playlist_id)
        except Exception as e:
            raise DiffError(f"Error fetching database playlist tracks: {e}") from e

    def _fetch_database_playlist_metadata(self, playlist_id: str):
        """
        Fetch metadata for a playlist stored in the JamJar database.

        :param playlist_id: The ID of the playlist to fetch metadata for.
        :return: A Playlist object with the playlist metadata.
        """

        try:
            return self.db.fetch_playlists(playlist_id)
        except Exception as e:
            raise DiffError(f"Error fetching database playlist metadata: {e}") from e

    def _generate_tracks_diff(self, db_tracks: list[Track], spotify_tracks: list[Track]) -> dict:
        """
        Generate a dictionary containing the differences between tracks in the database
        and tracks in the Spotify playlist.

        :param db_tracks: A list of Track objects from the database.
        :param spotify_tracks: A list of Track objects from Spotify.
        :return: A dictionary containing the added and removed tracks.
        """

        try:
            db_track_ids = {track.track_id for track in db_tracks}
            spotify_track_ids = {track.track_id for track in spotify_tracks}

            added_tracks = []
            removed_tracks = []
            for track in spotify_tracks:
                if track.track_id not in db_track_ids:
                    added_tracks.append(track._asdict())

                if track.track_id not in spotify_track_ids:
                    removed_tracks.append(track._asdict())

            return {"added": added_tracks, "removed": removed_tracks}
        except Exception as e:
            raise DiffError(f"Error generating tracks diff: {e}") from e

    def _generate_metadata_diff(self, db_playlist: Playlist, spotify_playlist: Playlist) -> dict:
        """
        Generate a dictionary containing the state differences between a playlist in
        the database and its current state on Spotify.

        :param db_playlist: A Playlist object from the database.
        :param spotify_playlist: A Playlist object from Spotify.
        :return: A dictionary containing the metadata differences.
        """

        try:
            metadata_diff = {}
            db_values = db_playlist._asdict()
            spotify_values = spotify_playlist._asdict()

            for key in db_values:
                if db_values[key] != spotify_values[key]:
                    metadata_diff[key] = {"db": db_values[key], "spotify": spotify_values[key]}

            # pylint: disable=line-too-long
            return {"metadata_changed": metadata_diff} if metadata_diff else {"metadata_changed": None}
        except Exception as e:
            raise DiffError(f"Error generating metadata diff: {e}") from e

    def diff_playlist(self, playlist_identifier: str, detailed: bool = False) -> dict:
        """
        Compare a playlist in the database with its current state on Spotify.

        :param playlist_identifier: The Spotify playlist ID or URL to compare.
        :param detailed: Flag to indicate whether detailed metadata differences should be shown.
        :return: A dictionary containing the differences between the two playlists.
        """

        try:
            playlist_id = extract_playlist_id(playlist_identifier)
            db_playlist = self._fetch_database_playlist_metadata(playlist_id)
            spotify_playlist = self._fetch_spotify_playlist_metadata(playlist_id)
            db_tracks = self._fetch_database_playlist_tracks(playlist_id)
            spotify_tracks = self._fetch_spotify_playlist_tracks(playlist_id)
            generated_diff = self._generate_tracks_diff(db_tracks, spotify_tracks)

            if detailed:
                metadata_diff = self._generate_metadata_diff(db_playlist, spotify_playlist)
                generated_diff.update(metadata_diff)

            return generated_diff
        except Exception as e:
            raise DiffError(f"Error comparing playlist: {e}") from e
