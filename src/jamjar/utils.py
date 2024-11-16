#!/usr/bin/env python

"""
Module for utility functions used in the JamJar CLI.
"""


def extract_playlist_id(playlist_identifier):
    """
    Extracts the playlist ID from a URL or uses the ID directly if given.
    """
    if "/" in playlist_identifier:
        return playlist_identifier.split("/")[-1].split("?")[0]
    return playlist_identifier
