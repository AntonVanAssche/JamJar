#!/usr/bin/env python
import json

import requests


class SpotifyError(Exception):
    """Base class for other exceptions"""

    pass


class SpotifyHTTPError(SpotifyError):
    """Raised when the Spotify API returns an HTTP error"""

    def __init__(self, response):
        self.status_code = response.status_code
        self.message = f"Spotify API returned status code {self.status_code}: {response.text}"
        super().__init__(self.message)


class SpotifyJobError(SpotifyError):
    """Raised when there's a job error on Spotify"""

    def __init__(self, device, job):
        self.device = device
        self.job = job
        self.message = f"Job error on device {device}: {job}"
        super().__init__(self.message)


class SpotifyJobTimeoutError(SpotifyError):
    """Raised when a Spotify job times out"""

    def __init__(self, device, job):
        self.device = device
        self.job = job
        self.message = f"Spotify job on device {device} timed out: {job}"
        super().__init__(self.message)

        import requests


class SpotifyAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"

    def get_playlist(self, playlist_id):
        """Fetch playlist details from Spotify."""
        url = f"{self.base_url}/playlists/{playlist_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_playlist_tracks(self, playlist_id):
        """Fetch the tracks of a specific playlist from Spotify."""
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
