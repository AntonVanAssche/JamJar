#!/usr/bin/env python

"""
CLI command for exporting playlist data to a JSON file.

This module facilitates the export of a playlist's metadata and associated tracks
from a database to a structured JSON file.
"""

import json

from jamjar.core.database import Database


class DumpError(Exception):
    """Exception raised for errors in the dump process."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# pylint: disable=too-few-public-methods
class DumpManager:
    """
    Handles the logic for exporting playlist data to a JSON file.

    This class interacts with the database using the Database object,
    to fetch playlist metadata and associated tracks, then formats
    and writes the data to a JSON file.
    """

    def __init__(self, db: Database):
        """
        Initialize the DumpManager with a database instance.

        :param db: An instance of the Database class.
        """

        self.db = db

    def dump_playlist(self, playlist_identifier: str, output_file: str = None) -> dict:
        """
        Export a playlist's data to a JSON file.

        Fetches the playlist metadata and associated tracks from the database,
        then writes the information to a JSON file.

        :param playlist_identifier: The unique identifier for the playlist.
        :param output_file: The optional file path for the exported JSON data.
                            If not provided, a sanitized version of the playlist
                            name will be used to create the file name.
        :return: A dictionary containing the status and message of the export process.
        :raises ValueError: If the playlist is not found in the database.
        :raises RuntimeError: If the export process fails.
        """

        try:
            playlist = self.db.fetch_playlists(playlist_identifier)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_identifier} not found.")

            tracks = self.db.fetch_tracks(playlist_identifier)
            if not tracks:
                raise ValueError(f"No tracks found for playlist with ID {playlist_identifier}.")

            export_data = {
                "metadata": playlist._asdict(),
                "tracks": [track._asdict() for track in tracks],
            }

            if not output_file:
                safe_name = "".join(c if c.isalnum() else "_" for c in playlist.playlist_name)
                output_file = f"{safe_name}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)

            return {
                "status": "success",
                "output_file": output_file,
            }
        except Exception as e:
            raise DumpError(f"Failed to export playlist: {e}") from e
