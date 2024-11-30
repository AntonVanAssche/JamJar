#!/usr/bin/env python

"""
Handles the database operations for JamJar.

This includes adding, updating, and deleting playlists and spotify_tracks, as well as
fetching playlists and spotify_tracks from the database.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Union

from jamjar.core.config import Config
from jamjar.core.dataclasses import Playlist, Track


class DatabaseError(Exception):
    """Exception raised for errors in the Database class."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# pylint: disable=too-many-public-methods
class Database:
    """
    Handles the database operations for JamJar.

    This includes adding, updating, and deleting playlists and spotify_tracks, as well as
    fetching playlists and spotify_tracks from the database.
    """

    def __init__(self, config: Config):
        self.db_path = Path(config.db_path).expanduser()
        self.connection = None
        self._initialize_database()

    def _connect(self):
        """Establish a connection to the SQLite database."""
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def _initialize_database(self):
        """Initialize the database with required tables if they don't exist."""
        self._connect()
        try:
            with self.connection:
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS spotify_playlist (
                        playlist_id VARCHAR(255) PRIMARY KEY NOT NULL,
                        playlist_name VARCHAR(255) NOT NULL,
                        owner_id VARCHAR(255) NOT NULL,
                        owner_name VARCHAR(255) NOT NULL,
                        owner_url VARCHAR(255) NOT NULL,
                        playlist_url VARCHAR(255) NOT NULL,
                        description TEXT,
                        public BOOLEAN NOT NULL DEFAULT FALSE,
                        followers_total INT NOT NULL DEFAULT 0,
                        snapshot_id VARCHAR(255) NOT NULL,
                        playlist_image_url VARCHAR(255) NOT NULL,
                        track_count INT NOT NULL DEFAULT 0,
                        colaborative BOOLEAN NOT NULL DEFAULT FALSE
                    );
                    """
                )

                # pylint: disable=line-too-long
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS spotify_tracks (
                        track_id VARCHAR(255) PRIMARY KEY NOT NULL,
                        track_name VARCHAR(255) NOT NULL,
                        track_url VARCHAR(255) NOT NULL,
                        track_uri VARCHAR(255) NOT NULL,
                        preview_url VARCHAR(255),
                        track_popularity INT NOT NULL DEFAULT 0,
                        album_id VARCHAR(255) NOT NULL,
                        album_name VARCHAR(255) NOT NULL,
                        album_url VARCHAR(255) NOT NULL,
                        artist_id VARCHAR(255) NOT NULL,
                        artist_name VARCHAR(255) NOT NULL,
                        artist_url VARCHAR(255) NOT NULL,
                        is_explicit BOOLEAN NOT NULL DEFAULT FALSE,
                        is_local BOOLEAN NOT NULL DEFAULT FALSE,
                        disc_number INT NOT NULL DEFAULT 1,
                        isrc_code VARCHAR(50),
                        playlist_id VARCHAR(255) NOT NULL,
                        user_added VARCHAR(255) NOT NULL,
                        time_added DATETIME NOT NULL,
                        FOREIGN KEY (playlist_id) REFERENCES spotify_playlist (playlist_id) ON DELETE CASCADE
                    );
                    """
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def add_playlist(
        self,
        playlist_id: str,
        name: str,
        owner_id: str,
        owner_name: str,
        owner_url: str,
        description: str,
        url: str,
        snapshot_id: str,
        playlist_image_url: str,
        followers_total: int = 0,
        track_count: int = 0,
        public: bool = False,
        colaborative: bool = False,
    ):
        """Add a playlist to the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO spotify_playlist (
                        playlist_id, playlist_name, owner_id, owner_name, owner_url,
                        description, playlist_url, public, followers_total,
                        snapshot_id, playlist_image_url, track_count, colaborative
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        playlist_id,
                        name,
                        owner_id,
                        owner_name,
                        owner_url,
                        description,
                        url,
                        public,
                        followers_total,
                        snapshot_id,
                        playlist_image_url,
                        track_count,
                        colaborative,
                    ),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=line-too-long
    # pylint: disable=too-many-locals
    def add_track(
        self,
        track_id: str,
        track_name: str,
        track_url: str,
        track_uri: str,
        preview_url: str,
        track_popularity: int,
        album_id: str,
        album_name: str,
        album_url: str,
        artist_id: str,
        artist_name: str,
        artist_url: str,
        is_explicit: bool,
        is_local: bool,
        disc_number: int,
        isrc_code: str,
        playlist_id: str,
        user_added: str,
        time_added: str,
    ):
        """Add a track to the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO spotify_tracks (
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
                        time_added
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
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
                        bool(is_explicit),
                        bool(is_local),
                        disc_number,
                        isrc_code,
                        playlist_id,
                        user_added,
                        time_added,
                    ),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def delete_track(self, track_id: str, playlist_id: str):
        """Delete a track from the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    DELETE FROM spotify_tracks
                    WHERE track_id = ? AND playlist_id = ?
                    """,
                    (
                        track_id,
                        playlist_id,
                    ),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def delete_playlist(self, playlist_id: str):
        """Delete a playlist and its spotify_tracks from the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    DELETE FROM spotify_playlist
                    WHERE playlist_id = ?
                    """,
                    (playlist_id,),
                )
                self.connection.execute(
                    """
                    DELETE FROM spotify_tracks
                    WHERE playlist_id = ?
                    """,
                    (playlist_id,),
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def delete_all_playlists(self):
        """Delete all playlists and their spotify_tracks from the database."""
        try:
            with self.connection:
                self.connection.execute(
                    """
                    DELETE FROM spotify_playlist
                    """
                )
                self.connection.execute(
                    """
                    DELETE FROM spotify_tracks
                    """
                )
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def fetch_playlists(self, playlist_id: Optional[str] = None) -> Union[Playlist, List[Playlist], None]:
        """
        Fetch all, or a specific playlist from the database.

        :param playlist_id (Optional[str]): The unique identifier of the playlist to fetch.
        :return Union[Playlist, List[Playlist], None]: A single Playlist, a list of Playlists, or None.
        """

        try:
            with self.connection:
                if playlist_id:
                    query = "SELECT * FROM spotify_playlist WHERE playlist_id = ?"
                    params = (playlist_id,)
                else:
                    query = "SELECT * FROM spotify_playlist"
                    params = ()

                rows = self.connection.execute(query, params).fetchall()
                if playlist_id:
                    return self._row_to_playlist(rows[0]) if rows else None

                return [self._row_to_playlist(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def _row_to_playlist(self, row: sqlite3.Row) -> Playlist:
        """Convert a database row to a Playlist object."""
        return Playlist(
            playlist_id=row["playlist_id"],
            playlist_name=row["playlist_name"],
            owner_id=row["owner_id"],
            owner_name=row["owner_name"],
            owner_url=row["owner_url"],
            description=row["description"],
            playlist_url=row["playlist_url"],
            public=bool(row["public"]),
            followers_total=row["followers_total"],
            snapshot_id=row["snapshot_id"],
            playlist_image_url=row["playlist_image_url"],
            track_count=row["track_count"],
            colaborative=bool(row["colaborative"]),
        )

    def fetch_tracks(
        self, playlist_id: Optional[str] = None, track_id: Optional[str] = None
    ) -> Union[Track, List[Track], None]:
        """
        Fetch all, or a specific track from the database.

        :param playlist_id (Optional[str]): The unique identifier of the playlist to fetch tracks from.
        :param track_id (Optional[str]): The unique identifier of the track to fetch.
        :return Union[Track, List[Track], None]: A single Track, a list of Tracks, or None.
        """

        try:
            with self.connection:
                if track_id:
                    query = "SELECT * FROM spotify_tracks WHERE track_id = ? AND playlist_id = ?"
                    params = (track_id, playlist_id)
                elif playlist_id:
                    query = "SELECT * FROM spotify_tracks WHERE playlist_id = ? ORDER BY track_id DESC"
                    params = (playlist_id,)
                else:
                    query = "SELECT * FROM spotify_tracks ORDER BY track_id DESC"
                    params = ()

                rows = self.connection.execute(query, params).fetchall()
                if track_id:
                    return self._row_to_track(rows[0]) if rows else None

                return [self._row_to_track(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def _row_to_track(self, row: sqlite3.Row) -> Track:
        """Convert a database row to a Track object."""

        return Track(
            track_id=row["track_id"],
            track_name=row["track_name"],
            track_url=row["track_url"],
            track_uri=row["track_uri"],
            preview_url=row["preview_url"],
            track_popularity=row["track_popularity"],
            album_id=row["album_id"],
            album_name=row["album_name"],
            album_url=row["album_url"],
            artist_id=row["artist_id"],
            artist_name=row["artist_name"],
            artist_url=row["artist_url"],
            is_explicit=bool(row["is_explicit"]),
            is_local=bool(row["is_local"]),
            disc_number=row["disc_number"],
            isrc_code=row["isrc_code"],
            playlist_id=row["playlist_id"],
            user_added=row["user_added"],
            time_added=row["time_added"],
        )

    def count_playlists(self) -> int:
        """Fetch the total number of playlists in the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT COUNT(*) FROM spotify_playlist
                    """
                ).fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def count_tracks(self) -> int:
        """Fetch the total number of spotify_tracks in the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT COUNT(*) FROM spotify_tracks
                    """
                ).fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def count_artists(self) -> int:
        """Fetch the total number of artists in the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT COUNT(DISTINCT artist_name) FROM spotify_tracks
                    """
                ).fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def count_users(self) -> int:
        """Fetch the total number of users who have added spotify_tracks to the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT COUNT(DISTINCT user_added) FROM spotify_tracks
                    """
                ).fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def count_unique_tracks(self) -> List[str]:
        """Count the number of unique spotify_tracks in the database."""
        try:
            with self.connection:
                return self.connection.execute(
                    """
                    SELECT COUNT(DISTINCT track_name) FROM spotify_tracks
                    """
                ).fetchone()[0]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def fetch_top_tracks(self, limit: int = 10) -> List[dict]:
        """Fetch the top spotify_tracks in the database based on the number of playlists they appear in."""
        try:
            with self.connection:
                rows = self.connection.execute(
                    """
                    SELECT track_name, artist_name, COUNT(*) as occurrences
                    FROM spotify_tracks
                    GROUP BY track_name, artist_name
                    ORDER BY occurrences DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

                return [
                    {
                        "track_name": row[0],
                        "artist_name": row[1],
                        "occurrences": row[2],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def fetch_top_artists(self, limit: int = 10) -> List[dict]:
        """Fetch the top artists in the database based on the number of playlists their tracks appear in."""
        try:
            with self.connection:
                rows = self.connection.execute(
                    """
                    SELECT artist_name, COUNT(*) as occurrences
                    FROM spotify_tracks
                    GROUP BY artist_name
                    ORDER BY occurrences DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

                return [
                    {
                        "artist_name": row[0],
                        "occurrences": row[1],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def fetch_top_users(self, limit: int = 3) -> List[dict]:
        """Fetch the top users in the database based on the number of spotify_tracks they've added."""
        try:
            with self.connection:
                rows = self.connection.execute(
                    """
                    SELECT user_added, COUNT(track_id) AS count
                    FROM spotify_tracks
                    GROUP BY user_added
                    ORDER BY count DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

                return [
                    {
                        "user_added": row[0],
                        "count": row[1],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def fetch_recent_tracks(self, limit: int = 10) -> List[dict]:
        """Fetch the most recently added spotify_tracks in the database across all playlists."""
        try:
            with self.connection:
                rows = self.connection.execute(
                    """
                    SELECT p.playlist_name, t.track_name, t.artist_name, t.user_added, t.time_added
                    FROM spotify_tracks t
                    JOIN spotify_playlist p ON t.playlist_id = p.playlist_id
                    ORDER BY t.time_added DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

                return [
                    {
                        "playlist_name": row[0],
                        "track_name": row[1],
                        "artist_name": row[2],
                        "user_added": row[3],
                        "time_added": row[4],
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise DatabaseError(e) from e

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
