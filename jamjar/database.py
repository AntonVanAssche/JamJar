#!/usr/bin/env python

import sqlite3
from pathlib import Path
from typing import List, Tuple

from jamjar.config import Config


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    pass


class Database:
    def __init__(self, config: Config):
        self.db_path = Path(config.db_path).expanduser()
        self.connection = None
        self._initialize_database()

    def _connect(self):
        """Establish a connection to the SQLite database."""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def _initialize_database(self):
        """Initialize the database with required tables if they don't exist."""
        self._connect()
        try:
            with self.connection:
                self.connection.execute(
                    """
                CREATE TABLE IF NOT EXISTS playlists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    description TEXT,
                    url TEXT NOT NULL
                )
                """
                )
                self.connection.execute(
                    """
                CREATE TABLE IF NOT EXISTS tracks (
                    id TEXT PRIMARY KEY,
                    playlist_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    url TEXT NOT NULL,
                    user_added TEXT NOT NULL,
                    time_added TIMESTAMP NOT NULL,
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE
                )
                """
                )
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def add_playlist(self, playlist_id: str, name: str, owner: str, description: str, url: str):
        """Add a playlist to the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO playlists (id, name, owner, description, url)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (playlist_id, name, owner, description, url),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def update_playlist(self, playlist_id: str, name: str, owner: str, description: str, url: str):
        """Update an existing playlist."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    UPDATE playlists
                    SET name = ?, owner = ?, description = ?, url = ?
                    WHERE id = ?
                    """,
                    (playlist_id, name, owner, description, url),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def add_track(
        self, playlist_id: str, track_id: str, name: str, artist: str, url: str, user_added: str, time_added: str
    ):
        """Add a track to the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO tracks (id, playlist_id, name, artist, url, user_added, time_added)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (track_id, playlist_id, name, artist, url, user_added, time_added),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def delete_track(self, track_id: str, track_name: str, track_artist: str):
        """Delete a track from the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    DELETE FROM tracks
                    WHERE id = ?
                    """,
                    (track_id,),
                )
            print(f"Track {track_id} ({track_name} - {track_artist}) deleted.")
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def fetch_playlists(self) -> List[Tuple]:
        """Fetch all playlists from the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT * FROM playlists
                    """
                ).fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def fetch_playlist_by_id(self, playlist_id: str) -> List[Tuple]:
        """Fetch a specific playlist specified by the id."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT * FROM playlists
                    WHERE id = ?
                    """,
                    (playlist_id,),
                ).fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def fetch_playlist_tracks(self, playlist_id: str) -> List[Tuple]:
        """Fetch all tracks for a specific playlist."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT * FROM tracks
                    WHERE playlist_id = ?
                    """,
                    (playlist_id,),
                ).fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(e)

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
