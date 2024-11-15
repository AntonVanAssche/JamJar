# JamJar CLI

JamJar is a CLI tool designed to "seal" the history of your Spotify playlists,
just like a jar preserves your favorite jams. Whether it's a collaborative
playlist with friends or your personal collection, JamJar saves every track
and its details into a database. No more losing track of who added what or
what songs were removed—keep your playlist history fresh and intact, like
music in a jar!

## Behind the Creation of JamJar

The inspiration for JamJar came from a simple yet frustrating limitation of
Spotify: the inability to track the history of a collaborative playlist. When
you’re working on a playlist with friends—where everyone can add songs—it’s
fun to keep things dynamic and fresh.

And you have some rule in place like "when you add a new song, you have to
remove one of your earlier choices" to keep things balanced and engaging.
Unfortunately, Spotify doesn’t provide a built-in way to see the history of
the playlist—like who removed song X or who added song Y. Once a song is
removed, it’s gone from the playlis, with no trace of its history.

That’s where JamJar comes in. This CLI tool was created to save the state of a
collaborative playlist to a simple SQLite database. By capturing the playlist
and track details, including who added each song, JamJar allows you to:

- Preserve a historical record of the playlist.
- Review the contributions of each collaborator.
- Export the data for further analysis or backup.

With JamJar, the story of your playlist stays intact, even as tracks come and
go. It’s a way to celebrate the collaborative spirit of music sharing while
maintaining a bit of structure and fun.

## Installation

1. Clone the repository:

   ```console
   git clone https://github.com/your-repo/jamjar.git
   cd jamjar
   ```

2. Set up a virtual environment:

   ```console
   python3 -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```

3. Install dependencies:

   ```console
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

```console
jamjar --help
```

Displays the list of available commands and options.

```console
jamjar --version
```

Shows the current version of JamJar.

### Authentication Commands

```console
jamjar auth --help
```

Manages authentication with Spotify.

| Command | Description                        |
|---------|------------------------------------|
| `login` | Log in to Spotify.                |
| `status`| Display current authentication status. |
| `clean` | Remove the saved access token.    |

### Playlist Commands

```console
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

```console
jamjar auth login
```

### Save a playlist

```console
jamjar playlist save https://open.spotify.com/playlist/playlist_id
```

### List stored playlists

```console
jamjar playlist list
```

### Clean up removed tracks

```console
jamjar playlist clean https://open.spotify.com/playlist/playlist_id
```

### Export a playlist

```console
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
