#!/usr/bin/env python

import click

from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI

CONFIG = Config()


class Update:
    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def update_playlist(self, playlist_identifier):
        """
        Update an existing playlist in the database.

        Accepts either a full Spotify playlist URL or just a playlist ID.
        """
        try:
            if "/" in playlist_identifier:
                playlist_id = playlist_identifier.split("/")[-1].split("?")[0]
            else:
                playlist_id = playlist_identifier

            print(f"Updating playlist with ID {playlist_id}...")

            playlist_data = self.spotify_api.get_playlist(playlist_id)
            name = playlist_data.get("name", "Unknown Playlist")
            owner = playlist_data.get("owner", {}).get("id", "Unknown User")
            description = playlist_data.get("description", "")
            url = playlist_data["external_urls"]["spotify"]

            self.db.update_playlist(playlist_id, name, owner, description, url)

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            for track_item in tracks_data["items"]:
                track = track_item["track"]
                track_id = track.get("id")
                if not track_id:
                    continue

                track_name = track.get("name", "Unknown Track")
                track_artist = ", ".join(artist["name"] for artist in track["artists"])
                track_url = track["external_urls"]["spotify"]
                track_user_added = track_item.get("added_by", {}).get("id", "Unknown User")
                track_time_added = track_item.get("added_at")

                self.db.add_track(
                    playlist_id,
                    track_id,
                    track_name,
                    track_artist,
                    track_url,
                    track_user_added,
                    track_time_added,
                )
                print(f"Updated track '{track_name}' by '{track_artist}'.")

            print(f"Playlist '{name}' updated successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to update playlist: {e}")


@click.command()
@click.help_option("--help", "-h")
@click.argument("playlist")
def update(playlist):
    """
    Update an existing playlist in the database.

    Accepts either a Spotify playlist URL or just a playlist ID.
    """
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    update_manager = Update(db, spotify_api)

    update_manager.update_playlist(playlist)
