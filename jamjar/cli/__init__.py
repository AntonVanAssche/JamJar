#!/usr/bin/env python

"""
JamJar CLI - "seal" the history of your Spotify playlists.

CLI commands for adding, removing, syncing, exporting, and
managing playlists in the JamJar database.
"""

from jamjar.cli.add import add
from jamjar.cli.auth import auth
from jamjar.cli.export import export
from jamjar.cli.list import list as list_command
from jamjar.cli.remove import remove
from jamjar.cli.sync import sync
from jamjar.cli.update import update
