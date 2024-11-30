#!/usr/bin/env python

"""
JamJar CLI - "seal" the history of your Spotify playlists.

Initialize the core package for JamJar, which includes the core functionality for
the CLI commands and the underlying data structures and utilities.
"""

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.dataclasses import Playlist, Track
from jamjar.core.spotify import SpotifyAPI
from jamjar.core.utils import *

__all__ = [
    "Config",
    "Database",
    "Playlist",
    "SpotifyAPI",
    "Track",
    "extract_playlist_id",
]
