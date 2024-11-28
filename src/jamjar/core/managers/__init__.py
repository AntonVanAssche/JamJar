#!/usr/bin/env python

"""
JamJar CLI - "seal" the history of your Spotify playlists.

Initialize the core package for JamJar, which includes the core functionality for
the CLI commands and the underlying data structures and utilities.
"""

from jamjar.core.managers.add import AddManager
from jamjar.core.managers.auth import Auth
from jamjar.core.managers.diff import DiffManager
from jamjar.core.managers.dump import DumpManager
from jamjar.core.managers.list import ListManager
from jamjar.core.managers.pull import PullManager
from jamjar.core.managers.push import PushManager
from jamjar.core.managers.rm import RemoveManager
from jamjar.core.managers.stats import StatsManager

__all__ = [
    "AddManager",
    "Auth",
    "DiffManager",
    "DumpManager",
    "ListManager",
    "PullManager",
    "PushManager",
    "RemoveManager",
    "StatsManager",
]
