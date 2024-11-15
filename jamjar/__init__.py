#!/usr/bin/env python

__version__ = "0.1.0"

import json
import os

import click

from jamjar.cli.auth import auth
from jamjar.cli.playlist import playlist


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Display the version of JamJar.")
def cli():
    """JamJar CLI - Store your Spotify playlist data."""
    pass


cli.add_command(auth)
cli.add_command(playlist)

if __name__ == "__main__":
    cli()
