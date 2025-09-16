from zotify.config import Zotify
from zotify.const import SEARCH_URL

def search(query: str, search_type: str = 'track,album,artist,playlist', limit: int = 20, offset: int = 0):
    """
    Performs a search against the API and returns the raw JSON response.
    """
    if not Zotify.SESSION:
        raise Exception("Not logged in.")

    params = {
        'q': query,
        'type': search_type,
        'limit': str(limit),
        'offset': str(offset)
    }

    return Zotify.invoke_url_with_params(SEARCH_URL, **params)

def get_liked_songs():
    """
    Retrieves the current user's liked songs.
    """
    from zotify.const import USER_SAVED_TRACKS_URL, ITEMS

    if not Zotify.SESSION:
        raise Exception("Not logged in.")

    return Zotify.invoke_url_nextable(USER_SAVED_TRACKS_URL, ITEMS)

def get_local_songs(path):
    """
    Scans a directory for local music files and reads their metadata.
    """
    from zotify.utils import walk_directory_for_tracks
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3

    songs = []
    for file_path in walk_directory_for_tracks(path):
        try:
            audio = MP3(file_path, ID3=EasyID3)
            song_info = {
                'name': audio.get('title', [str(file_path.name)])[0],
                'artists': audio.get('artist', ['Unknown Artist']),
                'album': audio.get('album', ['Unknown Album'])[0],
                'path': str(file_path)
            }
            songs.append(song_info)
        except Exception as e:
            print(f"Error reading metadata for {file_path}: {e}")
    return songs
