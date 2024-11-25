#!/usr/bin/env python

"""
This module defines the dataclasses used in the JamJar CLI.
"""

from dataclasses import dataclass


@dataclass
class Playlist:
    """Dataclass for storing playlist information."""

    playlist_id: str
    playlist_name: str
    owner_id: str
    owner_name: str
    owner_url: str
    playlist_url: str
    description: str
    public: bool
    followers_total: int
    snapshot_id: str
    playlist_image_url: str
    track_count: int
    colaborative: bool

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

    track_id: str
    track_name: str
    track_url: str
    track_uri: str
    preview_url: str
    track_popularity: int
    album_id: str
    album_name: str
    album_url: str
    artist_id: str
    artist_name: str
    artist_url: str
    is_explicit: bool
    is_local: bool
    disc_number: int
    isrc_code: str
    playlist_id: str
    user_added: str
    time_added: str

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
