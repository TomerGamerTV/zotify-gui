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
    from mutagen import File

    songs = []
    for file_path in walk_directory_for_tracks(path):
        try:
            audio = File(file_path, easy=True)
            if audio is None:
                continue

            # Also get the full tag info to look for album art
            full_audio = File(file_path)
            artwork = None
            if full_audio:
                if 'APIC:' in full_audio:
                    artwork = full_audio['APIC:'].data
                elif 'covr' in full_audio:  # for mp4/m4a
                    artwork = full_audio['covr'][0]

            song_info = {
                'type': 'local_track',  # Add type
                'name': audio.get('title', [str(file_path.name)])[0],
                'artists': audio.get('artist', ['Unknown Artist']),  # Keep as list of strings
                'album': audio.get('album', ['Unknown Album'])[0],  # Keep as string
                'path': str(file_path),
                'image_data': artwork  # Add image data
            }
            songs.append(song_info)
        except Exception as e:
            print(f"Error reading metadata for {file_path}: {e}")
    return songs
