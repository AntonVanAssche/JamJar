#!/usr/bin/env python

"""
Basic script to migrate the JamJar database over from v0.4.0 to a new schema
introduced in v0.5.0.
"""
import os
import shutil
import sqlite3
import sys


def add_track_uri_column(database_path):
    """Add a new column 'track_uri' to the 'spotify_tracks' table in the database."""

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        backup_path = f"{database_path}.bak"
        shutil.copy2(database_path, backup_path)

        print("Backup created:", backup_path)
    except:
        # pylint: disable=broad-exception-raised
        raise Exception("Backup failed.") from None

    try:

        cursor.execute(
            """
            ALTER TABLE spotify_tracks
            ADD COLUMN track_uri VARCHAR(255);
        """
        )
        print("Column 'track_uri' added.")

        cursor.execute(
            """
            UPDATE spotify_tracks
            SET track_uri = 'spotify:track:' || track_id;
        """
        )
        print("Column 'track_uri' populated with data.")

        cursor.execute("SELECT COUNT(*) FROM spotify_tracks WHERE track_uri IS NULL;")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            raise ValueError(f"""There are {null_count} NULL values in 'track_uri'. Exiting...""")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS spotify_tracks_temp AS
            SELECT
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
            FROM spotify_tracks;
        """
        )
        cursor.execute("DROP TABLE spotify_tracks;")

        # pylint: disable=line-too-long
        cursor.execute(
            """
            CREATE TABLE spotify_tracks (
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
        cursor.execute(
            """
            INSERT INTO spotify_tracks SELECT * FROM spotify_tracks_temp;
        """
        )
        cursor.execute("DROP TABLE spotify_tracks_temp;")
        print("Column 'track_uri' is now NOT NULL.")

        connection.commit()

    except Exception as e:
        connection.rollback()
        raise RuntimeError(f"Migration failed: {e}") from e

    finally:
        connection.close()


if __name__ == "__main__":
    db_path = sys.argv[1]
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}.")

    add_track_uri_column(db_path)
