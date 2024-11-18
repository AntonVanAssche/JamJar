#!/usr/bin/env python

"""
Module for utility functions used in the JamJar CLI.
"""

import json
from typing import List


def extract_playlist_id(playlist_identifier):
    """
    Extracts the playlist ID from a URL or uses the ID directly if given.
    """
    if "/" in playlist_identifier:
        return playlist_identifier.split("/")[-1].split("?")[0]
    return playlist_identifier


def format_json_output(entity_name: str, headers: List[str], data: List[dict]) -> str:
    """
    Format the given data into a JSON object with a custom structure.

    :param title: The title for the output, which will be the key in the JSON object.
    :param headers: List of column headers.
    :param rows: List of rows (each row is a tuple of column values).
    :return: JSON-formatted string of the data.
    """
    json_data = {entity_name: []}
    for item in data:
        json_data[entity_name].append({header: item.get(header, "") for header in headers})

    return json.dumps(json_data, indent=2)
