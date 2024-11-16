#!/usr/bin/env python

import click

from jamjar.config import Config
from jamjar.database import Database

CONFIG = Config()


class ListManager:
    def __init__(self, db: Database):
        self.db = db

    def _format_output(self, headers, rows):
        """
        Dynamically format and display tabular data.

        :param headers: List of column headers.
        :param rows: List of rows (each row is a list of column values).
        """
        # Calculate column widths based on the headers and rows
        column_widths = [max(len(str(header)), *(len(str(row[i])) for row in rows)) for i, header in enumerate(headers)]

        # Build the format string for each row
        row_format = " | ".join(f"{{:<{width}}}" for width in column_widths)

        # Print the headers
        print(row_format.format(*headers))
        print("-" * (sum(column_widths) + (len(headers) - 1) * 3))  # Separator line

        # Print each row
        for row in rows:
            print(row_format.format(*row))

    def list_playlists(self):
        """
        List all playlists stored in the database.
        """
        try:
            playlists = self.db.fetch_playlists()
            if not playlists:
                print("No playlists found.")
                return

            headers = ["ID", "Name", "Description"]
            rows = [[playlist[0], playlist[1], playlist[3]] for playlist in playlists]
            self._format_output(headers, rows)
        except Exception as e:
            raise RuntimeError(f"Failed to list playlists: {e}")

    def list_tracks(self, playlist_id):
        """
        List all tracks in a specific playlist.
        """
        try:
            if "/" in playlist_id:
                playlist_id = playlist_id.split("/")[-1].split("?")[0]
            else:
                playlist_id = playlist_id

            playlist = self.db.fetch_playlist_by_id(playlist_id)
            if not playlist:
                print(f"Playlist with ID '{playlist_id}' not found.")
                return

            tracks = self.db.fetch_playlist_tracks(playlist_id)
            if not tracks:
                print("No tracks found in the playlist.")
                return

            headers = ["ID", "Name", "Artist", "User Added", "Time Added"]
            rows = [
                [
                    track[0],
                    track[2],
                    track[3],
                    track[5],
                    track[6],
                ]
                for track in tracks
            ]
            self._format_output(headers, rows)
        except Exception as e:
            raise RuntimeError(f"Failed to list tracks: {e}")


@click.command()
@click.help_option("--help", "-h")
@click.option("--playlist", "-p", help="ID, or URL, of the playlist to list tracks for.")
def list(playlist=None):
    """
    List playlists or tracks in a specific playlist.

    Without options, lists all playlists.
    Use --playlist to list tracks in a specific playlist.
    """
    db = Database(CONFIG)
    list_manager = ListManager(db)

    if playlist:
        list_manager.list_tracks(playlist)
    else:
        list_manager.list_playlists()
