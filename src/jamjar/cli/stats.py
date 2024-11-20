#!/usr/bin/env python

"""
CLI command for fetching statistics about playlists, tracks, and users in the database.

This module provides functionality for fetching and displaying statistics such as the top
tracks, top artists, top users, and the most recent tracks in the database. When no specific
options are provided, general statistics (total counts) for playlists, tracks, artists, and
users are displayed.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


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
        print(json.dumps({"top_tracks": data}, indent=2))

    def get_top_artists(self):
        """Fetch and display the top artists in the database."""

        data = self.db.fetch_top_artists()
        print(json.dumps({"top_artists": data}, indent=2))

    def get_top_users(self):
        """Fetch and display the top users in the database."""

        data = self.db.fetch_top_users()
        print(json.dumps({"top_users": data}, indent=2))

    def get_recent_tracks(self):
        """Fetch and display the most recent tracks added to the database."""

        data = self.db.fetch_recent_tracks()
        print(json.dumps({"recent_tracks": data}, indent=2))

    def get_stats(self):
        """Fetch and display general statistics about the database."""

        total_playlists = self.db.count_playlists()
        total_tracks = self.db.count_tracks()
        unique_tracks = self.db.count_unique_tracks()
        total_artists = self.db.count_artists()
        unique_artists = self.db.count_unique_artists()
        total_users = self.db.count_users()
        json_data = {
            "total_playlists": total_playlists,
            "total_tracks": total_tracks,
            "unique_tracks": unique_tracks,
            "total_artists": total_artists,
            "unique_artists": unique_artists,
            "total_users": total_users,
        }
        print(json.dumps(json_data, indent=2))


@click.command()
@click.help_option("--help", "-h")
@click.option("--top-tracks", is_flag=True, help="Get the top tracks in the database.")
@click.option("--top-artists", is_flag=True, help="Get the top artists in the database.")
@click.option("--top-users", is_flag=True, help="Get the top users in the database.")
@click.option("--recent-tracks", is_flag=True, help="Get the most recent tracks in the database.")
def stats(top_tracks, top_artists, top_users, recent_tracks):
    """
    Display statistics on playlists, tracks, and users.

    Use this command to display:
    - General statistics (e.g., total number of playlists, tracks, artists, users)
    - Top tracks, top artists, or top users
    - Most recent tracks added to the database

    If no options are specified, general statistics will be displayed.
    """
    db = Database(CONFIG)
    stats_manager = StatsManager(db)

    if top_tracks:
        stats_manager.get_top_tracks()
        return

    if top_artists:
        stats_manager.get_top_artists()
        return

    if top_users:
        stats_manager.get_top_users()
        return

    if recent_tracks:
        stats_manager.get_recent_tracks()
        return

    if not any([top_tracks, top_artists, top_users, recent_tracks]):
        stats_manager.get_stats()
        return
