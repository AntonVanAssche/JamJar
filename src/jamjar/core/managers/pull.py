#!/usr/bin/env python

"""
CLI command for synchronizing a playlist with Spotify.

This module handles synchronization of a playlist with Spotify, including
updating the database with new tracks and optionally removing tracks no longer
present in the Spotify playlist.
"""

from jamjar.core.database import Database
from jamjar.core.managers.add import AddManager
from jamjar.core.managers.rm import RemoveManager
from jamjar.core.spotify import SpotifyAPI
from jamjar.core.utils import extract_playlist_id


# pylint: disable=too-few-public-methods
class PullManager:
    """
    Manages the synchronization of a playlist with Spotify.

    This class updates the database with new playlist metadata and tracks,
    and optionally removes tracks no longer present in the Spotify playlist.
    """

    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        """
        Initialize the PullManager with database and Spotify API instances.

        :param db: An instance of the Database class for database operations.
        :param spotify_api: An instance of the SpotifyAPI class for Spotify operations.
        """
        self.db = db
        self.spotify_api = spotify_api
        self.add_manager = AddManager(db, spotify_api)

    def pull_playlist(self, playlist_identifier: str, rm: bool = False) -> dict:
        """
        Synchronize a playlist with Spotify.

        Fetches the playlist metadata and tracks from Spotify, updates the database,
        and optionally removes tracks no longer in the Spotify playlist.

        :param playlist_identifier: The Spotify playlist ID or URL to synchronize.
        :param rm: If True, remove tracks from the database that are no longer
                   present in the Spotify playlist.
        :return: A summary of the synchronization operation.
        """
        try:
            playlist_id = extract_playlist_id(playlist_identifier)

            spotify_playlist = self.spotify_api.get_playlist(playlist_id)
            if not spotify_playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found on Spotify.")

            if not self.db.fetch_playlists(playlist_id):
                add_result = self.add_manager.add_playlist(playlist_identifier)
                return add_result

            playlist_data = self.spotify_api.get_playlist(playlist_id)
            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)

            playlist_result = self.add_manager.add_playlist_to_db(playlist_id, playlist_data)
            added_tracks_result = self.add_manager.add_tracks_to_db(playlist_id, tracks_data)
            return_result = {
                "status": "updated",
                "playlist": playlist_result,
                "tracks": {"added": added_tracks_result["added_tracks"]},
            }

            if rm:
                removed_tracks_result = self._remove_deleted_tracks(playlist_id, tracks_data)
                return_result["tracks"]["removed"] = removed_tracks_result["removed_tracks"]

            return return_result

        except Exception as e:
            raise RuntimeError(f"Failed to sync playlist: {e}") from e

    def _remove_deleted_tracks(self, playlist_id: str, spotify_tracks: dict) -> dict:
        """
        Remove tracks from the database that are no longer in the Spotify playlist.

        Compares the tracks in the Spotify playlist with those in the local database,
        and removes tracks from the database that are missing in Spotify.

        :param playlist_id: The Spotify playlist ID.
        :param spotify_tracks: A dictionary of tracks fetched from Spotify.
        :return: A summary of the track removal operation.
        """
        try:
            rm_manager = RemoveManager(self.db)
            spotify_track_ids = {item["track"]["id"] for item in spotify_tracks.get("items", [])}
            local_tracks = self.db.fetch_tracks(playlist_id)
            removed_tracks = []

            for local_track in local_tracks:
                if local_track.track_id not in spotify_track_ids:
                    removed_track = rm_manager.remove_track(playlist_id, local_track.track_id)
                    removed_tracks.append(removed_track)

            return {"status": "removed", "removed_tracks": removed_tracks}
        except Exception as e:
            raise RuntimeError(f"Failed to remove deleted tracks: {e}") from e
