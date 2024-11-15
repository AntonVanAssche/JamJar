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

    def _process_playlist_and_tracks(self, playlist_id, update=False):
        """Fetch playlist and track data, and either save or update the playlist in the DB."""
        playlist_data = self.spotify_api.get_playlist(playlist_id)
        name = playlist_data.get("name", "Unknown Playlist")
        owner = playlist_data.get("owner", {}).get("id", "Unknown User")
        description = playlist_data.get("description", "")
        url = playlist_data["external_urls"]["spotify"]

        if update:
            self.db.update_playlist(playlist_id, name, owner, description, url)
        else:
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

            print(f"{"Updated" if update else "Added"} track '{track_name}' by '{track_artist}' to the database.")

        action = "saved" if not update else "updated"
        print(f"Playlist '{name}' and tracks {action} to the database.")

    def save_playlist(self, playlist_url):
        """Save the playlist and tracks to the database."""
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        try:
            self._process_playlist_and_tracks(playlist_id, update=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save playlist: {e}")

    def update_playlist(self, playlist_id):
        """Update an existing playlist in the DB."""
        try:
            self._process_playlist_and_tracks(playlist_id, update=True)
        except Exception as e:
            raise RuntimeError(f"Failed to update playlist: {e}")

    def clean_playlist(self, playlist_id):
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

    def export(self, playlist_id, output=None):
        """Export the playlist to a JSON file."""
        try:
            playlist = self.db.fetch_playlist_by_id(playlist_id)
            if not playlist:
                raise ValueError(f"Playlist with ID {playlist_id} not found.")

            tracks = self.db.fetch_playlist_tracks(playlist_id)
            if not tracks:
                print("No tracks found.")
                return

            playlist = playlist[0]
            playlist_data = {
                "id": playlist[0],
                "name": playlist[2],
                "owner": playlist[2],
                "description": playlist[3],
                "url": playlist[4],
                "tracks": [
                    {
                        "id": track[1],
                        "name": track[2],
                        "artist": track[3],
                        "url": track[4],
                        "user_added": track[5],
                        "time_added": track[6],
                    }
                    for track in tracks
                ],
            }

            if not output:
                char_map = {ord(c): "_" for c in "!@#$%^&*()[]{};:,.<>?/'\"\\| "}
                output = f"{playlist[1].translate(char_map)}.json"

            with open(output, "w") as f:
                json.dump(playlist_data, f, indent=2)

            print(f"Playlist data exported to {output}.")
        except Exception as e:
            raise RuntimeError(f"Failed to export playlist: {e}")

    def list_content(self, playlist_id=None):
        """
        List playlists or tracks in a playlist based on the presence of playlist_id.
        If playlist_id is None, lists all playlists. Otherwise, lists tracks in the given playlist.
        """
        try:
            if playlist_id is None:
                # List all playlists
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
            else:
                # List tracks in the given playlist
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
            raise RuntimeError(f"Failed to list content: {e}")


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
@click.argument("playlist_id")
def clean(playlist_id):
    """Remove tracks not in the current playlist."""
    access_token = Auth(CONFIG).get_access_token()
    db = Database(CONFIG)
    spotify_api = SpotifyAPI(access_token)
    playlist_manager = Playlist(db, spotify_api)

    playlist_manager.clean_playlist(playlist_id)


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id", required=False)
def list(playlist_id=None):
    """List all playlists or tracks in a playlist."""
    db = Database(CONFIG)
    playlist_manager = Playlist(db, None)
    playlist_manager.list_content(playlist_id)


@playlist.command()
@click.help_option("--help", "-h")
@click.argument("playlist_id")
@click.option("--output", "-o", help="Output file for the playlist data.")
def export(playlist_id, output=None):
    """Export the playlist to a JSON file."""
    db = Database(CONFIG)
    playlist_manager = Playlist(db, None)
    playlist_manager.export(playlist_id, output)
