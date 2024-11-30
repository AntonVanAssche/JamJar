#!/usr/bin/env python

"""
Handles the Spotify API requests for the JamJar CLI.

This module provides a class for interacting with the Spotify API, including
fetching playlist details and tracks.
"""


import requests


class SpotifyError(Exception):
    """Base class for other exceptions"""


class SpotifyHTTPError(SpotifyError):
    """Raised when the Spotify API returns an HTTP error"""

    def __init__(self, response):
        self.status_code = response.status_code
        self.message = f"Spotify API returned status code {self.status_code}: {response.text}"
        super().__init__(self.message)


class SpotifyAPI:
    """
    Handles the Spotify API requests for the JamJar CLI.

    This class provides methods for fetching playlist details and tracks from
    the Spotify API.
    """

    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"

    def get_playlist(self, playlist_id):
        """Fetch playlist details from Spotify."""
        url = f"{self.base_url}/playlists/{playlist_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()

    def get_playlist_tracks(self, playlist_id):
        """Fetch the tracks of a specific playlist from Spotify."""
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        all_tracks = []

        while url:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            all_tracks.extend(data["items"])
            url = data.get("next")

        return {"items": all_tracks}

    def get_user_id(self):
        """Fetch the user ID from Spotify."""
        url = f"{self.base_url}/me"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise SpotifyHTTPError(response)

        return response.json()["id"]

    def post_playlist(self, user_id: str, playlist_data: dict):
        """Post a playlist to Spotify."""
        url = f"{self.base_url}/users/{user_id}/playlists"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=playlist_data, timeout=10)
        if response.status_code != 201:
            raise SpotifyHTTPError(response)

        return response.json()

    def post_tracks(self, playlist_id: str, track_uris: list):
        """Add tracks to a Spotify playlist."""
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {"uris": track_uris}

        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code != 201:
            raise SpotifyHTTPError(response)

        return response.json()

    def post_image(self, playlist_id: str, image_data: str):
        """Add a cover image to a Spotify playlist."""
        url = f"{self.base_url}/playlists/{playlist_id}/images"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "image/jpeg",
        }

        response = requests.put(url, headers=headers, data=image_data, timeout=10)
        if response.status_code != 202:
            raise SpotifyHTTPError(response)

        return response
