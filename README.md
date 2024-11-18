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

### From PackageCloud

JamJar can be installed in two ways: via PackageCloud or by building it from
source. Using PackageCloud is the simplest and most user-friendly option,
though it’s not available on all platforms. Currently, only Red Hat-based
systems (like Fedora) and the Python Package Index (PyPI) are supported.

For further instructions, visit the PackageCloud repository:
<https://packagecloud.io/AntonVanAssche/JamJar>

### From Source

1. Clone the repository:

   ```console
   git clone https://github.com/AntonVanAssche/jamjar.git
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

### General Commands

```console
$ jamjar --help
Usage: jamjar [OPTIONS] COMMAND [ARGS]...

  "seal” the history of your Spotify playlists

Options:
  -h, --help     Show this message and exit.
  -v, --version  Display the version of JamJar.

Commands:
  add     Add a playlist to the database.
  auth    Manage Spotify authentication.
  diff    Compares playlist state between database and Spotify.
  export  Export a playlist's data to a JSON file.
  list    List playlists or tracks in a specific playlist.
  remove  Remove a playlist or a specific track from a playlist.
  stats   Get statistics about the playlists and tracks in the database.
  sync    Synchronize a playlist with Spotify.
  update  Update an existing playlist in the database.
```

## Command Details

### Authentication

#### `jamjar auth login`

Logs in to Spotify and stores the access token for future use.

```console
jamjar auth login
```

#### `jamjar auth status`

Displays the current authentication status.

```console
jamjar auth status
```

#### `jamjar auth clean`

Removes the saved Spotify access token.

```console
jamjar auth clean
```

### Playlist Management

#### `jamjar add <url|id>`

Adds a playlist to the database by URL or playlist ID.

```console
jamjar add https://open.spotify.com/playlist/playlist_id
```

```console
jamjar add playlist_id
```

#### `jamjar diff <url|id> [--details]`

Compares the playlist state between the database and Spotify and returns
it in the JSON format.

```console
jamjar diff https://open.spotify.com/playlist/playlist_id
```

```console
jamjar diff playlist_id
```

To also show playlist metadata changes, use the `--details` flag:

```console
jamjar diff playlist_id --details
```

#### `jamjar update <url|id>`

Updates an existing playlist in the database.

```console
jamjar update https://open.spotify.com/playlist/playlist_id
```

```console
jamjar update playlist_id
```

#### `jamjar remove <playlist_id> [--track-id <track_id>]`

Removes a playlist or a specific track from a playlist.

```console
jamjar remove playlist_id
```

```console
jamjar remove playlist_id --track-id track_id
```

#### `jamjar sync <url|id>`

Syncs the playlist with Spotify to update tracks.

```console
jamjar sync playlist_id
```

```console
jamjar sync https://open.spotify.com/playlist/playlist_id
```

#### `jamjar list [--playlist <id>]`

Lists all playlists or tracks in a specific playlist.

```console
jamjar list
```

```console
jamjar list --playlist playlist_id
```

#### `jamjar export <id> [--output <filename>]`

Exports a playlist's data to a JSON file.

```console
jamjar export playlist_id --output my_playlist.json
```

### Statistics

#### `jamjar stats [--top-tracks|--top-artists|--top-users|--recent-tracks]`

Some statistics about the playlists and tracks in the database
returned in the JSON format.

```console
jamjar stats
```

Show the top tracks in the database returned in the JSON format.

```console
jamjar stats --top-tracks
```

Show the top artists in the database returned in the JSON format.

```console
jamjar stats --top-artists
```

Show the top users in the database returned in the JSON format.

```console
jamjar stats --top-users
```

Show the most recent tracks in the database returned in the JSON format.

```console
jamjar stats --recent-tracks
```

## Configuration

The Spotify credentials file (`~/.config/jamjar/config.json`) should contain the following:

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "redirect_uri": "http://localhost:5000/callback"
}
```

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.
