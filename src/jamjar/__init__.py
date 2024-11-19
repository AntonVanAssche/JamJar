#!/usr/bin/env python

"""
JamJar CLI - "seal" the history of your Spotify playlists.

This module sets up the CLI commands for adding, removing,
syncing, exporting, and managing playlists in the JamJar database.
"""

__version__ = "0.4.0"

import json
import os

import click

from jamjar.cli.add import add
from jamjar.cli.auth import auth
from jamjar.cli.diff import diff
from jamjar.cli.dump import dump
from jamjar.cli.list import list as list_command
from jamjar.cli.rm import rm
from jamjar.cli.stats import stats
from jamjar.cli.sync import sync
from jamjar.cli.update import update


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Display the version of JamJar.")
def cli():
    """JamJar CLI - "seal" the history of your Spotify playlists."""


cli.add_command(add)
cli.add_command(auth)
cli.add_command(diff)
cli.add_command(dump)
cli.add_command(list_command)
cli.add_command(rm)
cli.add_command(stats)
cli.add_command(sync)
cli.add_command(update)

if __name__ == "__main__":
    cli()
