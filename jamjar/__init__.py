#!/usr/bin/env python

__version__ = "0.1.0"

import json
import os

import click

from jamjar.cli.add import add
from jamjar.cli.auth import auth
from jamjar.cli.export import export
from jamjar.cli.list import list
from jamjar.cli.remove import remove
from jamjar.cli.sync import sync
from jamjar.cli.update import update


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Display the version of JamJar.")
def cli():
    """JamJar CLI - "seal" the history of your Spotify playlists."""
    pass


cli.add_command(add)
cli.add_command(auth)
cli.add_command(export)
cli.add_command(list)
cli.add_command(remove)
cli.add_command(sync)
cli.add_command(update)

if __name__ == "__main__":
    cli()
