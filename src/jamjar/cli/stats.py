#!/usr/bin/env python

"""
CLI command to get statistics about the playlists and tracks in the database.

This includes fetching the top tracks, artists, and users, as well as the most
recent tracks in the database. When no options are provided, general statistics
such as the total number of playlists, tracks, artists, and users are displayed.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


class StatsManager:
    """
    Handles the logic for displaying statistics about the playlists and tracks
    in the database.
    """

    def __init__(self, db: Database):
        self.db = db

    def get_top_tracks(self):
        """
        Get the top tracks in the database and display them.
        """
        data = self.db.fetch_top_tracks()
        print(json.dumps({"top_tracks": data}, indent=2))

    def get_top_artists(self):
        """
        Get the top artists in the database and display them.
        """
        data = self.db.fetch_top_artists()
        print(json.dumps({"top_artists": data}, indent=2))

    def get_top_users(self):
        """
        Get the top users in the database and display them.
        """
        data = self.db.fetch_top_users()
        print(json.dumps({"top_users": data}, indent=2))

    def get_recent_tracks(self):
        """
        Get the most recent tracks in the database and display them.
        """
        data = self.db.fetch_recent_tracks()
        print(json.dumps({"recent_tracks": data}, indent=2))

    def get_stats(self):
        """
        Get statistics about the playlists and tracks in the database and display them.
        """
        total_playlists = self.db.count_playlists()
        total_tracks = self.db.count_tracks()
        total_artists = self.db.count_artists()
        total_users = self.db.count_users()
        json_data = {
            "total_playlists": total_playlists,
            "total_tracks": total_tracks,
            "total_artists": total_artists,
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
    Get statistics about the playlists and tracks in the database.
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
