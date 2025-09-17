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

**NOTE:** The GUI is currently in an experimental state and may contain bugs.

To launch the GUI, run the following command in your terminal:

`python3 -m zotify.gui`

The GUI allows you to:
- Login to your account securely.
- Search for tracks, albums, artists, and playlists.
- View and download your liked songs.
- Download music with a single click.

### Command-Line Interface (CLI)

`(python -m) zotify <track/album/playlist/episode/artist url>`

Download track(s), album(s), playlist(s), podcast episode(s), or artist(s) specified by the URL(s) passed as a command line argument(s).
If an artist's URL is given, all albums by the specified artist will be downloaded. Can take multiple URLs as multiple arguments.

(For more detailed CLI usage, please refer to the output of `zotify --help`)

## Disclaimer

Zotify is intended to be used in compliance with DMCA, Section 1201, for educational, private and fair use. \
Zotify contributors are not responsible for any misuse of the program or source code.

## Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)
