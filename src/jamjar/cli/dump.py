#!/usr/bin/env python

"""
CLI command for exporting playlist data to a JSON file.

This module facilitates the export of a playlist's metadata and associated tracks
from a database to a structured JSON file.
"""

import click

from jamjar.core.config import Config
from jamjar.core.database import Database
from jamjar.core.managers.dump import DumpManager

CONFIG = Config()


@click.command()
@click.help_option("--help", "-h")
@click.argument("identifier")
@click.option("--output", "-o", help="Output file for the playlist data.")
def dump(identifier, output):
    """
    Export playlist data to a JSON file.

    Fetches metadata and associated tracks for a specified playlist and writes
    them to a JSON file.

    :param identifier: The unique identifier of the playlist to export.
    :param output: The optional file path for the exported JSON data.
    """

    db = Database(CONFIG)
    dump_manager = DumpManager(db)

    result = dump_manager.dump_playlist(identifier, output)
    if result["status"] == "success":
        print(f"Playlist data exported to '{result['output_file']}.'")
