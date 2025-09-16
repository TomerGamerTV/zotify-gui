# Zotify

## A highly customizable music and podcast downloader

<p align="center">
  <img src="https://i.imgur.com/hGXQWSl.png" width="50%" alt="Zotify logo">
</p>

## Features

- Downloads at up to 320kbps \*
- Downloads directly from the source \*\*
- Downloads podcasts, playlists, liked songs, albums, artists, singles.
- Downloads synced lyrics from the source
- Option to download in real time to reduce suspicious API request behavior \*\*\*
- Supports multiple audio formats
- Download directly from URL or use built-in in search
- Bulk downloads from a list of URLs in a text file or parsed directly as arguments

\* Free accounts are limited to 160kbps \*\*
\*\* Audio files are NOT substituted with ones from other sources (such as YouTube or Deezer) \*\*\
\*\*\* 'Real time' downloading limits at the speed of data transfer to typical streaming rates (download time ≈  duration of the track) \*\*\*

## Installation

### Dependencies

- Python 3.10 or greater
- FFmpeg

### For the Command-Line Interface (CLI)

This guide uses *pipx* to manage Zotify.
There are other ways to install and run Zotify but this is the official recommendation.

- **Windows:**
  - Open PowerShell and run:
  - `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - `irm get.scoop.sh | iex`
  - `scoop install python ffmpeg-shared git`
  - `python3 -m pip install --user pipx`
  - `python3 -m pipx ensurepath`
- **macOS:**
  - Open the Terminal app and run:
  - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - `brew install python@3.11 pipx ffmpeg git`
  - `pipx ensurepath`
- **Linux:**
  - Install `python3`, `pip`, `ffmpeg`, and `git` from your distribution's package manager.
  - `python3 -m pip install --user pipx`

After installing the dependencies, install Zotify with:
`pipx install git+https://github.com/Googolplexed0/zotify.git`

### For the Graphical User Interface (GUI)

First, follow the instructions to install the CLI. Then, install the additional dependencies for the GUI:

`python3 -m pip install PyQt5 pyqtdarktheme requests pydub`

## Usage

### Graphical User Interface (GUI)

To launch the GUI, run the following command in your terminal:

`python3 -m zotify.gui.main`

<p align="center">
  <img src="https://user-images.githubusercontent.com/93454665/142783298-9550720a-c5c1-4714-8952-285c852f52d1.png">
</p>

The GUI allows you to:
- Login to your account securely.
- Search for tracks, albums, artists, and playlists.
- View and download your liked songs.
- Download music with a single click.
- Configure settings like download format and directory.

### Command-Line Interface (CLI)

`(python -m) zotify <track/album/playlist/episode/artist url>`

Download track(s), album(s), playlist(s), podcast episode(s), or artist(s) specified by the URL(s) passed as a command line argument(s).
If an artist's URL is given, all albums by the specified artist will be downloaded. Can take multiple URLs as multiple arguments.

### Basic Flags and Modes

`(python -m) zotify <{mode flag}> <{config flag} {config value}> <track/album/playlist/episode/artist url>`

| Command Line Config Flag           | Function                                                                                                                |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `-h`, `--help`                     | See this message                                                                                                        |
| `--version`                        | Show the version of Zotify                                                                                              |
| `-c`, `--config-location`          | Specify a directory containing a Zotify `config.json` file to load settings (Also accepts a filepath to a `.json` file) |
| `-u`, `--username`                 | Account username                                                                                                        |
| `--token`                          | Authentication token                                                                                                    |
| `--debug`                          | Enable debug mode, prints extra information and creates a `config_DEBUG.json` file                                      |
| `--update-config`                  | Updates the `config.json` file while keeping all current settings unchanged                                             |

| Command Line Mode Flag (exclusive) | Mode                                                                                                      |
|------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `-s`, `--search`                   | Search tracks/albums/artists/playlists based on argument (interactive)                                    |
| `-p`, `--playlist`                 | Download playlist(s) saved by your account (interactive)                                                  |
| `-l`, `--liked`                    | Download all Liked Songs on your account                                                                  |
| `-a`, `--artists`                  | Download all songs by all followed artists                                                                |
| `-f`, `--file`                     | Download all tracks/albums/episodes/playlists URLs within the file passed as argument                     |
| `-v`, `--verify-library`           | Check metadata for all tracks in ROOT_PATH or listed in SONG_ARCHIVE, updating the metadata if necessary  |

<details><summary>

### Advanced Usage and Config Flags

</summary>

All options can be set via the commandline or in a [config.json file](#configuration-files). Commandline arguments take priority over config.json arguments.  
Set arguments in the commandline like this: `-ie False` or `--codec mp3`. Wrap commandline arguments containing spaces or non-alphanumeric characters (weird symbols) with quotes like this: `--output-liked-songs "Liked Songs/{song_name}"`. Make sure to escape any backslashes (`\`) to prevent string-escape errors.

| Main Options                 | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `ROOT_PATH`                  | `-rp`, `--root-path`                | Directory where music is saved (replaces `.` in other path configs)          | `~/Music/Zotify Music`    |
| `SAVE_CREDENTIALS`           | `--save-credentials`                | Whether login credentials should be saved                                    | True                      |
| `CREDENTIALS_LOCATION`       | `--creds`, `--credentials-location` | Directory containing credentials.json                    | See [Path Option Parser](#path-option-parser) |

| File Options                 | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `OUTPUT`                     | `--output`                          | Master output file pattern (overwrites all others)    | See [Output Format Examples](#output-formatting) |
| `OUTPUT_PLAYLIST`            | `-op`, `--output-playlist`          | Output file pattern for playlists                 | See [Output Format Examples](#example-output-values) |
| `OUTPUT_PLAYLIST_EXT`        | `-oe`, `--output-ext-playlist`      | Output file pattern for extended playlists        | See [Output Format Examples](#example-output-values) |
| `OUTPUT_LIKED_SONGS`         | `-ol`, `--output-liked-songs`       | Output file pattern for user's Liked Songs        | See [Output Format Examples](#example-output-values) |
| `OUTPUT_SINGLE`              | `-os`, `--output-single`            | Output file pattern for single tracks             | See [Output Format Examples](#example-output-values) |
| `OUTPUT_ALBUM`               | `-oa`, `--output-album`             | Output file pattern for albums                    | See [Output Format Examples](#example-output-values) |
| `ROOT_PODCAST_PATH`          | `-rpp`, `--root-podcast-path`       | Directory where podcasts are saved                                           | `~/Music/Zotify Podcasts` |
| `SPLIT_ALBUM_DISCS`          | `--split-album-discs`               | Saves each disc of an album into its own subfolder                           | False                     |
| `MAX_FILENAME_LENGTH`        | `--max-filename-length`             | Maximum character length of filenames, truncated to fit, 0 meaning no limit  | 0                         |

| Download Options             | Command Line Config Flag            | Description                                                                              | Default Value |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------------------|---------------|
| `BULK_WAIT_TIME`             | `--bulk-wait-time`                  | The wait time between track downloads, in seconds                                        | 1             |
| `DOWNLOAD_REAL_TIME`         | `-rt`, `--download-real-time`       | Downloads songs as fast as they would be played, should prevent account bans             | False         |
| `TEMP_DOWNLOAD_DIR`          | `-td`, `--temp-download-dir`        | Directory where tracks are temporarily downloaded first, `""` meaning disabled           | `""`          |
| `DOWNLOAD_PARENT_ALBUM`      | `--download-parent-album`           | Download a track's parent album, including itself (uses `OUTPUT_ALBUM` file pattern)     | False         |
| `NO_COMPILATION_ALBUMS`      | `--no-compilation-albums`           | Skip downloading an album if API metadata labels it a compilation (not recommended)      | False         |

| Regex Options                | Command Line Config Flag            | Description                                                                              | Default Value |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------------------|---------------|
| `REGEX_ENABLED`              | `--regex-enabled`                   | Enable Regular Expression filtering on item titles                                       | False         |
| `REGEX_TRACK_SKIP`           | `--regex-track-skip`                | Regex pattern for skipping tracks, `""` meaning disabled                                 | `""`          |
| `REGEX_ALBUM_SKIP`           | `--regex-album-skip`                | Regex pattern for skipping albums, `""` meaning disabled                                 | `""`          |

| Encoding Options             | Command Line Config Flag            | Description                                                                              | Default Value |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------------------|---------------|
| `DOWNLOAD_FORMAT`            | `--codec`, `--download-format`      | Audio codec of downloads, copy avoids remuxing (aac, fdk_aac, mp3, ogg, opus, vorbis)    | copy          |
| `DOWNLOAD_QUALITY`           | `-q`, `--download-quality`          | Audio quality of downloads, auto selects highest available (normal, high, very_high*)    | auto          |
| `TRANSCODE_BITRATE`          | `-b`, `--bitrate`                   | Overwrite the bitrate for FFMPEG encoding (not recommended)                              |               |

| Archive Options              | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `SONG_ARCHIVE_LOCATION`      | `--song-archive-location`           | Directory for storing a global song_archive file         | See [Path Option Parser](#path-option-parser) |
| `DISABLE_SONG_ARCHIVE`       | `--disable-song-archive`            | Disable global song_archive for `SKIP_PREVIOUSLY_DOWNLOADED` checks (NOT RECOMMENDED)   | False          |
| `DISABLE_DIRECTORY_ARCHIVES` | `--disable-directory-archives`      | Disable local song_archive in download directories                                      | False          |
| `SKIP_EXISTING`              | `-ie`, `--skip-existing`            | Skip songs already present in the expected output directory                             | True           |
| `SKIP_PREVIOUSLY_DOWNLOADED` | `-ip`, `--skip-prev-downloaded`     | Use the global song_archive file to skip previously downloaded songs                    | False          |

| Playlist File Config Key     | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `EXPORT_M3U8`                | `-e`, `--export-m3u8`               | Export tracks/albums/episodes/playlists with an accompanying .m3u8 file      | False                     |
| `M3U8_LOCATION`              | `--m3u8-location`                   | Directory where .m3u8 files are saved, `""` being the output directory       | `""`                      |
| `M3U8_REL_PATHS`             | `--m3u8-relative-paths`             | List .m3u8 track paths relative to the .m3u8 file's directory                | True                      |
| `LIKED_SONGS_ARCHIVE_M3U8`   | `--liked-songs-archive-m3u8`        | Use cumulative/archiving method when exporting .m3u8 file for Liked Songs    | True                      |

| Lyric File Options           | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `DOWNLOAD_LYRICS`            | `--download-lyrics`                 | Whether lyrics should be downloaded (synced, with unsynced as fallback)      | True                      |
| `LYRICS_LOCATION`            | `--lyrics-location`                 | Directory where .lrc files are saved, `""` being the output directory        | `""`                      |
| `ALWAYS_CHECK_LYRICS`        | `--always-check-lyrics`             | Always try to download a song's lyrics, even if skipping the song            | False                     |
| `LYRICS_MD_HEADER`           | `--lyrics-md-header`                | Include optional metadata ([see tags here](https://en.wikipedia.org/wiki/LRC_(file_format)#Core_format)) at the start of a .lrc file                     | False                     |

| Metadata Options             | Command Line Config Flag            | Description                                                                              | Default Value |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------------------|---------------|
| `LANGUAGE`                   | `--language`                        | Language in which metadata/tags are requested                                            | en            |
| `STRICT_LIBRARY_VERIFY`      | `--strict-library-verify`           | Whether unreliable tags should be forced to match when verifying local library           | True          |
| `MD_DISC_TRACK_TOTALS`       | `--md-disc-track-totals`            | Whether track totals and disc totals should be saved in metadata                         | True          |
| `MD_SAVE_GENRES`             | `--md-save-genres`                  | Whether genres should be saved in metadata                                               | True          |
| `MD_ALLGENRES`               | `--md-allgenres`                    | Save all relevant genres in metadata                                                     | False         |
| `MD_GENREDELIMITER`          | `--md-genredelimiter`               | Delimiter character to split genres in metadata, use `""` if array-like tags desired     | `", "`        |
| `MD_ARTISTDELIMITER`         | `--md-artistdelimiter`              | Delimiter character to split artists in metadata, use `""` if array-like tags desired    | `", "`        |
| `MD_SAVE_LYRICS`             | `--md-save-lyrics`                  | Whether lyrics should be saved in metadata, requires `--download-lyrics` be True         | True          |
| `ALBUM_ART_JPG_FILE`         | `--album-art-jpg-file`              | Save album art as a separate .jpg file                                                   | False         |

| API Options                  | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `RETRY_ATTEMPTS`             | `--retry-attempts`                  | Number of times to retry failed API requests                                 | 1                         |
| `CHUNK_SIZE`                 | `--chunk-size`                      | Chunk size for downloading                                                   | 20000                     |
| `OAUTH_ADDRESS`              | `--redirect-uri`                    | Local server address listening for OAuth login requests                      | 0.0.0.0                   |
| `REDIRECT_ADDRESS`           | `--redirect-address`                | Local callback point for OAuth login requests                                | 127.0.0.1                 |

| Terminal & Logging Options   | Command Line Config Flag            | Description                                                                  | Default Value             |
|------------------------------|-------------------------------------|------------------------------------------------------------------------------|---------------------------|
| `PRINT_SPLASH`               | `--print-splash`                    | Show the Zotify logo at startup                                              | False                     |
| `PRINT_PROGRESS_INFO`        | `--print-progress-info`             | Show message contianing download progress information                        | True                      |
| `PRINT_SKIPS`                | `--print-skips`                     | Show message when a track is skipped                                         | True                      |
| `PRINT_DOWNLOADS`            | `--print-downloads`                 | Show message when a track is downloaded successfully                         | True                      |
| `PRINT_DOWNLOAD_PROGRESS`    | `--print-download-progress`         | Show track download progress bar                                             | True                      |
| `PRINT_URL_PROGRESS`         | `--print-url-progress`              | Show url progress bar                                                        | True                      |
| `PRINT_ALBUM_PROGRESS`       | `--print-album-progress`            | Show album progress bar                                                      | True                      |
| `PRINT_ARTIST_PROGRESS`      | `--print-artist-progress`           | Show artist progress bar                                                     | True                      |
| `PRINT_PLAYLIST_PROGRESS`    | `--print-playlist-progress`         | Show playlist progress bar                                                   | True                      |
| `PRINT_WARNINGS`             | `--print-warnings`                  | Show warnings                                                                | True                      |
| `PRINT_ERRORS`               | `--print-errors`                    | Show errors                                                                  | True                      |
| `PRINT_API_ERRORS`           | `--print-api-errors`                | Show API errors                                                              | True                      |
| `FFMPEG_LOG_LEVEL`           | `--ffmpeg-log-level`                | FFMPEG's logged level of detail when completing a transcoded download        | error                     |

\* very_high (320k) is limited to Premium accounts only  

</details>

## Disclaimer

Zotify is intended to be used in compliance with DMCA, Section 1201, for educational, private and fair use. \
Zotify contributors are not responsible for any misuse of the program or source code.

## Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)
