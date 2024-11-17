#!/usr/bin/env python

"""
Module for utility functions used in the JamJar CLI.
"""

import json


def extract_playlist_id(playlist_identifier):
    """
    Extracts the playlist ID from a URL or uses the ID directly if given.
    """
    if "/" in playlist_identifier:
        return playlist_identifier.split("/")[-1].split("?")[0]
    return playlist_identifier


def format_json_output(title, headers, rows):
    """
    Format the given data into a JSON object with a custom structure.

    :param title: The title for the output, which will be the key in the JSON object.
    :param headers: List of column headers.
    :param rows: List of rows (each row is a tuple of column values).
    :return: JSON-formatted string of the data.
    """
    formatted_rows = [dict(zip(headers, row)) for row in rows]
    result = {title: formatted_rows}
    return json.dumps(result, indent=2)
