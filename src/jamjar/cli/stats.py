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

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.stats import StatsManager

CONFIG = Config()


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
        top_tracks_data = stats_manager.get_top_tracks()
        print(json.dumps(top_tracks_data, indent=2))
        return

    if top_artists:
        top_artists_data = stats_manager.get_top_artists()
        print(json.dumps(top_artists_data, indent=2))
        return

    if top_users:
        top_users_data = stats_manager.get_top_users()
        print(json.dumps(top_users_data, indent=2))
        return

    if recent_tracks:
        recent_tracks_data = stats_manager.get_recent_tracks()
        print(json.dumps(recent_tracks_data, indent=2))
        return

    if not any([top_tracks, top_artists, top_users, recent_tracks]):
        stats_data = stats_manager.get_stats()
        print(json.dumps(stats_data, indent=2))
        return
