#!/usr/bin/env python

"""
This module defines the dataclasses used in the JamJar CLI.
"""

from dataclasses import dataclass


@dataclass
class Playlist:
    """Dataclass for storing playlist information."""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    # pylint: disable-msg=too-many-positional-arguments
    def __init__(
        self,
        playlist_id,
        playlist_name,
        owner_id,
        owner_name,
        owner_url,
        playlist_url,
        description,
        public,
        followers_total,
        snapshot_id,
        playlist_image_url,
        track_count,
        colaborative,
    ):
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.owner_url = owner_url
        self.playlist_url = playlist_url
        self.description = description
        self.public = public
        self.followers_total = followers_total
        self.snapshot_id = snapshot_id
        self.playlist_image_url = playlist_image_url
        self.track_count = track_count
        self.colaborative = colaborative

    def _asdict(self):
        """Return the playlist data as a dictionary."""
        return {
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "owner_url": self.owner_url,
            "playlist_url": self.playlist_url,
            "description": self.description,
            "public": self.public,
            "followers_total": self.followers_total,
            "snapshot_id": self.snapshot_id,
            "playlist_image_url": self.playlist_image_url,
            "track_count": self.track_count,
            "colaborative": self.colaborative,
        }


@dataclass
class Track:
    """Dataclass for storing track information."""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    # pylint: disable-msg=too-many-positional-arguments
    # pylint: disable-msg=too-many-locals
    def __init__(
        self,
        track_id,
        track_name,
        track_url,
        track_uri,
        preview_url,
        track_popularity,
        album_id,
        album_name,
        album_url,
        artist_id,
        artist_name,
        artist_url,
        is_explicit,
        is_local,
        disc_number,
        isrc_code,
        playlist_id,
        user_added,
        time_added,
    ):
        self.track_id = track_id
        self.track_name = track_name
        self.track_url = track_url
        self.track_uri = track_uri
        self.preview_url = preview_url
        self.track_popularity = track_popularity
        self.album_id = album_id
        self.album_name = album_name
        self.album_url = album_url
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.artist_url = artist_url
        self.is_explicit = is_explicit
        self.is_local = is_local
        self.disc_number = disc_number
        self.isrc_code = isrc_code
        self.playlist_id = playlist_id
        self.user_added = user_added
        self.time_added = time_added

    def _asdict(self):
        """Return the track data as a dictionary."""
        return {
            "track_id": self.track_id,
            "track_name": self.track_name,
            "track_url": self.track_url,
            "track_uri": self.track_uri,
            "preview_url": self.preview_url,
            "track_popularity": self.track_popularity,
            "album_id": self.album_id,
            "album_name": self.album_name,
            "album_url": self.album_url,
            "artist_id": self.artist_id,
            "artist_name": self.artist_name,
            "artist_url": self.artist_url,
            "is_explicit": self.is_explicit,
            "is_local": self.is_local,
            "disc_number": self.disc_number,
            "isrc_code": self.isrc_code,
            "playlist_id": self.playlist_id,
            "user_added": self.user_added,
            "time_added": self.time_added,
        }
