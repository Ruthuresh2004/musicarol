import requests
from utils.utilities import APP_NAME, TOLERANCE_MS


class MusicBrainzAPI:
    BASE_URL = "https://musicbrainz.org/ws/2"
    HEADERS = {"User-Agent": f"{APP_NAME}/1.0 (laura200291@gmail.com)"}

    def __init__(self, logging):
        self.logging = logging

    def fetch_json(self, endpoint):
        url = f"{MusicBrainzAPI.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=MusicBrainzAPI.HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logging.error(f"Error en la petición a MusicBrainz ({url}): {e}")
            return {}

    def search_recordings(self, song_title):
        query = f'recording:"{song_title}"'
        data = self.fetch_json(f"recording/?query={query}&fmt=json")
        return data.get("recordings", [])

    def get_artist_id(self, artist_name):
        query = f'artist/?query={artist_name}&fmt=json'
        data = self.fetch_json(query)

        if "artists" in data:
            for artist in data["artists"]:
                if artist["name"].lower() == artist_name.lower():
                    return artist["id"]
        return None

    def get_artist_genres(self, artist_id):
        data = self.fetch_json(f"artist/{artist_id}?inc=genres&fmt=json")
        return data.get("genres", [])
