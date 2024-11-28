#!/usr/bin/env python

"""
CLI command for fetching statistics about playlists, tracks, and users in the database.

This module provides functionality for fetching and displaying statistics such as the top
tracks, top artists, top users, and the most recent tracks in the database. When no specific
options are provided, general statistics (total counts) for playlists, tracks, artists, and
users are displayed.
"""

from jamjar.core.database import Database


class StatsManager:
    """
    Manages the logic for fetching and displaying various statistics about playlists,
    tracks, and users in the database.

    This class includes methods to retrieve information like the top tracks, top artists,
    top users, recent tracks, and overall statistics about the database (e.g., counts of
    playlists, tracks, artists, and users).
    """

    def __init__(self, db: Database):
        """
        Initializes the StatsManager with a given database connection.

        :param db: The Database object used for querying the database.
        """

        self.db = db

    def get_top_tracks(self):
        """Fetch and display the top tracks in the database."""

        data = self.db.fetch_top_tracks()
        return {"top_tracks": data}

    def get_top_artists(self):
        """Fetch and display the top artists in the database."""

        data = self.db.fetch_top_artists()
        return {"top_artists": data}

    def get_top_users(self):
        """Fetch and display the top users in the database."""

        data = self.db.fetch_top_users()
        return {"top_users": data}

    def get_recent_tracks(self):
        """Fetch and display the most recent tracks added to the database."""

        data = self.db.fetch_recent_tracks()
        return {"recent_tracks": data}

    def get_stats(self):
        """Fetch and display general statistics about the database."""

        total_playlists = self.db.count_playlists()
        total_tracks = self.db.count_tracks()
        unique_tracks = self.db.count_unique_tracks()
        total_artists = self.db.count_artists()
        total_users = self.db.count_users()

        return {
            "total_playlists": total_playlists,
            "total_tracks": total_tracks,
            "unique_tracks": unique_tracks,
            "total_artists": total_artists,
            "total_users": total_users,
        }
