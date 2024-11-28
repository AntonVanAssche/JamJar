#!/usr/bin/env python

"""
CLI command removing playlists or tracks from the JamJar database.

This module provides functionality to:
1. Remove a playlist and all its associated tracks from the database.
2. Remove a specific track from a playlist in the database.
3. Optionally, remove all playlists and tracks from the database.
"""

from jamjar.core.database import Database

CONFIG = Config()


class RemoveManager:
    """
    Manages the removal of playlists or tracks from the database.

    Provides methods to:
    - Remove an entire playlist along with all its associated tracks.
    - Remove a specific track from a playlist.
    """

    def __init__(self, db: Database):
        """
        Initialize the RemoveManager with a database instance.

        :param db: Instance of the Database class for performing database operations.
        """

        self.db = db

    def remove_playlist(self, playlist_id: str) -> dict:
        """
        Remove a playlist and all its associated tracks from the database.

        :param playlist_id: The unique identifier of the playlist to remove.
        """

        try:
            playlist = self.db.fetch_playlists(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist with ID '{playlist_id}' not found.")

            self.db.delete_playlist(playlist_id)

            return {
                "status": "removed",
                "removed_playlist": playlist.playlist_name,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to remove playlist: {e}") from e

    def remove_track(self, playlist_id: str, track_id: str) -> dict:
        """
        Remove a specific track from a playlist in the database.

        :param playlist_id: The unique identifier of the playlist containing the track.
        :param track_id: The unique identifier of the track to remove.
        """

        try:
            print(playlist_id, track_id)
            track = self.db.fetch_tracks(playlist_id, track_id)
            print(track)
            if not track:
                err_msg = f"Track with ID '{track_id}' not found in playlist '{playlist_id}'."
                raise ValueError(err_msg)

            self.db.delete_track(track_id, playlist_id)

            return {
                "status": "removed",
                "removed_track": track.track_name,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to remove track: {e}") from e
