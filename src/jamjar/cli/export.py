#!/usr/bin/env python

"""
CLI command to export a playlist's data to a JSON file.

This module handles exporting a playlist's metadata and its associated tracks
to a JSON file.
"""

import json

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


# pylint: disable=too-few-public-methods
class Export:
    """
    Handles the logic for exporting a playlist's data to a JSON file.

    This includes fetching the playlist and its associated tracks from the database
    and writing the data to a JSON file.
    """

    def __init__(self, db: Database):
        self.db = db

    def export_playlist(self, playlist_identifier, output_file=None):
        """
        Export a playlist's data to a JSON file.

        The data includes playlist metadata and its associated tracks.
        """
        try:
            playlist = self.db.fetch_playlist_by_id(playlist_identifier)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_identifier} not found.")

            tracks = self.db.fetch_playlist_tracks(playlist_identifier)
            if not tracks:
                print(f"No tracks found for playlist ID {playlist_identifier}.")
                return

            export_data = {
                "metadata": playlist._asdict(),
                "tracks": [track._asdict() for track in tracks],
            }

            if not output_file:
                safe_name = "".join(c if c.isalnum() else "_" for c in playlist.playlist_name)
                output_file = f"{safe_name}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)

            print(f"Playlist data exported to {output_file}.")
        except Exception as e:
            raise RuntimeError(f"Failed to export playlist: {e}") from e


@click.command()
@click.help_option("--help", "-h")
@click.argument("identifier")
@click.option("--output", "-o", help="Output file for the playlist data.")
def export(identifier, output):
    """
    Export a playlist's data to a JSON file.

    Accepts a playlist ID or a URL.
    """
    db = Database(CONFIG)
    export_manager = Export(db)

    export_manager.export_playlist(identifier, output)
