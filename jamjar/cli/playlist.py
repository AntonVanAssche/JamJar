#!/usr/bin/env python

import json

import click

from jamjar.cli.auth import Auth
from jamjar.config import Config
from jamjar.database import Database
from jamjar.spotify import SpotifyAPI

CONFIG = Config()


class Playlist:
    def __init__(self, db: Database, spotify_api: SpotifyAPI):
        self.db = db
        self.spotify_api = spotify_api

    def save_playlist(self, playlist_url):
        """Save the playlist and tracks to the database."""
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        try:
            playlist_data = self.spotify_api.get_playlist(playlist_id)
            name = playlist_data.get("name", "Unknown Playlist")
            owner = playlist_data.get("owner", {}).get("id", "Unknown User")
            description = playlist_data.get("description", "")
            url = playlist_data["external_urls"]["spotify"]

            self.db.add_playlist(playlist_id, name, owner, description, url)

            tracks_data = self.spotify_api.get_playlist_tracks(playlist_id)
            for track_item in tracks_data["items"]:
                track = track_item["track"]
                track_id = track.get("id")
                if not track_id:
                    continue

                track_name = track.get("name", "Unknown Track")
                track_artist = ", ".join(artist["name"] for artist in track["artists"])
                track_url = track["external_urls"]["spotify"]
                user_added = track_item.get("added_by", {}).get("id", "Unknown User")
                time_added = track_item.get("added_at")

                self.db.add_track(playlist_id, track_id, track_name, track_artist, track_url, user_added, time_added)

            print(f"Playlist '{name}' and tracks saved to the database.")
        except Exception as e:
            raise RuntimeError(f"Failed to save playlist: {e}")

    def update_playlist(self, playlist_id):
        """Update an existing playlist in the DB."""
        try:
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

            print(f"Playlist '{name}' updated.")
        except Exception as e:
            raise RuntimeError(f"Failed to update playlist: {e}")

    def clean_playlist(self, playlist_url):
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        try:
            tracks_data_api = self.spotify_api.get_playlist_tracks(playlist_id)
            track_ids_api = {track_item["track"]["id"] for track_item in tracks_data_api["items"]}
            tracks_local_db = self.db.fetch_playlist_tracks(playlist_id)

            for track in tracks_local_db:
                if track[0] not in track_ids_api:
                    self.db.delete_track(track[0], track[2], track[3])

            print("Playlist cleaned successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to clean playlist: {e}")

    def list_playlists(self):
        """List all playlists in the database."""
        try:
            playlists = self.db.fetch_playlists()
            if not playlists:
                print("No playlists found.")
                return

            id_width = max(len("ID"), *(len(str(playlist[0])) for playlist in playlists))
            name_width = max(len("Name"), *(len(playlist[1]) for playlist in playlists))
            desc_width = max(len("Description"), *(len(playlist[3]) for playlist in playlists))

            print(f"{'ID':<{id_width}} | {'Name':<{name_width}} | {'Description':<{desc_width}}")
            print("-" * (id_width + name_width + desc_width + 9))

            for playlist in playlists:
                print(f"{playlist[0]:<{id_width}} | {playlist[1]:<{name_width}} | {playlist[3]:<{desc_width}}")
        except Exception as e:
            raise RuntimeError(f"Failed to list playlists: {e}")

    def list_tracks(self, playlist_id):
        """List all tracks in a playlist."""
        try:
            playlist = self.db.fetch_playlist_by_id(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found.")

            tracks = self.db.fetch_playlist_tracks(playlist_id)
            if not tracks:
                print("No tracks found.")
                return

            id_width = max(len("ID"), *(len(str(track[0])) for track in tracks))
            name_width = max(len("Name"), *(len(track[2]) for track in tracks))
            artist_width = max(len("Artist"), *(len(track[3]) for track in tracks))
            user_width = max(len("User Added"), *(len(track[5]) for track in tracks))
            time_width = max(len("Time Added"), *(len(track[6]) for track in tracks))

            print(
                f"{'ID':<{id_width}} | {'Name':<{name_width}} | {'Artist':<{artist_width}} | {'User Added':<{user_width}} | {'Time Added':<{time_width}}"
            )
            print("-" * (id_width + name_width + artist_width + user_width + time_width + 13))

            for track in tracks:
                print(
                    f"{track[0]:<{id_width}} | {track[2]:<{name_width}} | {track[3]:<{artist_width}} | {track[5]:<{user_width}} | {track[6]:<{time_width}}"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to list tracks: {e}")


@click.group()
@click.help_option("--help", "-h")
def playlist():
    """Manage Spotify playlists."""
    pass


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("url")
def save(url):
    """Save the playlist and tracks to the database."""
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    playlist_manager = Playlist(db, spotify_api)

    playlist_manager.save_playlist(url)


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id")
def update(playlist_id):
    """Update an existing playlist in the database."""
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    playlist_manager = Playlist(db, spotify_api)

    playlist_manager.update_playlist(playlist_id)


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("url")
def clean(url):
    """Remove tracks not in the current playlist."""
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    playlist_manager = Playlist(db, spotify_api)

    playlist_manager.clean_playlist(url)


@playlist.command()
@click.help_option("--help", "-h")
def list():
    """List all playlists stored in the database."""
    db = Database(CONFIG)
    playlist_manager = Playlist(db, None)
    playlist_manager.list_playlists()


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id")
def list_tracks(playlist_id):
    """List all tracks stored in the database."""
    db = Database(CONFIG)
    playlist_manager = Playlist(db, None)
    playlist_manager.list_tracks(playlist_id)
