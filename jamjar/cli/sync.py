#!/usr/bin/env python

import click

from jamjar.cli.add import Add
from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI

CONFIG = Config()


class Sync:
    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def sync_playlist(self, playlist_identifier):
        """
        Synchronize a playlist with Spotify.

        - Updates playlist metadata.
        - Updates tracks in the database.
        - Removes tracks from the database that are no longer in the Spotify playlist.
        """
        try:
            if "/" in playlist_identifier:
                playlist_id = playlist_identifier.split("/")[-1].split("?")[0]
            else:
                playlist_id = playlist_identifier
            print(f"Syncing playlist with ID {playlist_id}...")

            spotify_playlist = self.spotify_api.get_playlist(playlist_id)
            if not spotify_playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found on Spotify.")

            if not self.db.fetch_playlist_by_id(playlist_id):
                print(f"Playlist with ID {playlist_id} not found in the database.")
                Add(self.db, self.spotify_api).add_playlist(playlist_id)
                return

            name = spotify_playlist.get("name", "Unknown Playlist")
            owner = spotify_playlist.get("owner", {}).get("id", "Unknown User")
            description = spotify_playlist.get("description", "")
            url = spotify_playlist["external_urls"]["spotify"]
            self.db.update_playlist(playlist_id, name, owner, description, url)
            print(f"Updated playlist '{name}' metadata in the database.")

            spotify_tracks = self.spotify_api.get_playlist_tracks(playlist_id)
            spotify_track_ids = set()
            for item in spotify_tracks["items"]:
                track = item["track"]
                if not track:
                    continue
                track_id = track["id"]
                if not track_id:
                    continue
                spotify_track_ids.add(track_id)

                track_name = track.get("name", "Unknown Track")
                track_artist = ", ".join(artist["name"] for artist in track["artists"])
                track_url = track["external_urls"]["spotify"]
                user_added = item.get("added_by", {}).get("id", "Unknown User")
                time_added = item.get("added_at")

                self.db.add_track(
                    playlist_id,
                    track_id,
                    track_name,
                    track_artist,
                    track_url,
                    user_added,
                    time_added,
                )
                print(f"Synced track '{track_name}' by '{track_artist}'.")

            local_tracks = self.db.fetch_playlist_tracks(playlist_id)
            for local_track in local_tracks:
                if local_track[0] not in spotify_track_ids:
                    self.db.delete_track(local_track[0], playlist_id, local_track[2])
                    print(f"Removed track '{local_track[2]}' by '{local_track[3]}' from the database.")

            print(f"Synchronization complete for playlist '{name}'.")
        except Exception as e:
            raise RuntimeError(f"Failed to sync playlist: {e}")


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def sync(playlist):
    """
    Synchronize a playlist with Spotify.

    Updates playlist metadata and tracks in the database,
    and removes tracks from the database that are no longer in the Spotify playlist.

    Accepts either a full Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    sync_manager = Sync(db, spotify_api)

    sync_manager.sync_playlist(playlist)
