#!/usr/bin/env python

import json

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


class Export:
    def __init__(self, db: Database):
        self.db = db

    def export_playlist(self, playlist_identifier, output_file=None):
        """
        Export a playlist's data to a JSON file.

        The data includes playlist metadata and its associated tracks.
        """
        try:
            # Fetch playlist from the database
            playlist = self.db.fetch_playlist_by_id(playlist_identifier)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_identifier} not found.")

            # Fetch associated tracks
            tracks = self.db.fetch_playlist_tracks(playlist_identifier)
            if not tracks:
                print(f"No tracks found for playlist ID {playlist_identifier}.")
                return

            # Prepare data for export
            playlist = playlist[0]
            export_data = {
                "id": playlist[0],
                "name": playlist[1],
                "owner": playlist[2],
                "description": playlist[3],
                "url": playlist[4],
                "tracks": [
                    {
                        "id": track[1],
                        "name": track[2],
                        "artist": track[3],
                        "url": track[4],
                        "user_added": track[5],
                        "time_added": track[6],
                    }
                    for track in tracks
                ],
            }

            # Determine output filename if not specified
            if not output_file:
                safe_name = "".join(c if c.isalnum() else "_" for c in playlist[1])
                output_file = f"{safe_name}.json"

            # Write data to file
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=4)

            print(f"Playlist data exported to {output_file}.")
        except Exception as e:
            raise RuntimeError(f"Failed to export playlist: {e}")


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
