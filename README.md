# JamJar CLI

JamJar is a CLI tool designed to "seal" the history of your Spotify playlists,
just like a jar preserves your favorite jams. Whether it's a collaborative
playlist with friends or your personal collection, JamJar saves every track
and its details into a database. No more losing track of who added what or
what songs were removed—keep your playlist history fresh and intact, like
music in a jar!

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/jamjar.git
   cd jamjar
   ```

2. Set up a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Spotify credentials:
   - Create a Spotify app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Add your `client_id` and `client_secret` to `~/.jamjar_config.json`:

     ```json
     {
       "client_id": "your-client-id",
       "client_secret": "your-client-secret"
     }
     ```

## Usage

JamJar's commands are divided into logical groups: `auth` for authentication and `playlist` for managing playlists.

### General Commands

```bash
jamjar --help
```

Displays the list of available commands and options.

```bash
jamjar --version
```

Shows the current version of JamJar.

### Authentication Commands

```bash
jamjar auth --help
```

Manages authentication with Spotify.

| Command | Description                        |
|---------|------------------------------------|
| `login` | Log in to Spotify.                |
| `status`| Display current authentication status. |
| `clean` | Remove the saved access token.    |

### Playlist Commands

```bash
jamjar playlist --help
```

Handles Spotify playlist management.

| Command    | Description                                    |
|------------|------------------------------------------------|
| `save`     | Save the playlist and its tracks to the database. |
| `update`   | Update an existing playlist in the database.   |
| `clean`    | Remove tracks not in the current playlist.     |
| `list`     | List all playlists or tracks in a specific playlist. |
| `export`   | Export the playlist to a JSON file.            |

## Examples

### Authenticate with Spotify

```bash
jamjar auth login
```

### Save a playlist

```bash
jamjar playlist save https://open.spotify.com/playlist/playlist_id
```

### List stored playlists

```bash
jamjar playlist list
```

### Clean up removed tracks

```bash
jamjar playlist clean https://open.spotify.com/playlist/playlist_id
```

### Export a playlist

```bash
jamjar playlist export MY_PLAYLIST_ID --output my_playlist.json
```

## Configuration

The Spotify credentials file (`~/.jamjar_config.json`) should contain the following:

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "redirect_uri": "http://localhost:5000/callback",
  "db_path": "~/.jamjar.db",
  "token_path": "~/.jamjar_token.json"
}
```

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.
