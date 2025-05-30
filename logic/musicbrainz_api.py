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

    def buscar_artista_api(self, title, year, duracion_ms):
        query = f'{title} AND date:{year}' if year else title
        recordings = self.search_recordings(query)

        coincidencias = [
            r for r in recordings
            if "length" in r and abs(r["length"] - duracion_ms) <= TOLERANCE_MS
        ]

        mejor_registro = max(coincidencias or recordings, key=lambda r: r.get("score", 0), default=None)
        artista = mejor_registro["artist-credit"][0]["name"] if mejor_registro else "Desconocido"
        return artista

    def buscar_genero_api(self, artist_name):
        artist_id = self.get_artist_id(artist_name)
        if not artist_id:
            return None

        genres = self.get_artist_genres(artist_id)
        if not genres:
            return None

        top_genres = [tag["name"] for tag in sorted(genres, key=lambda x: x.get("count", 0), reverse=True)[:3]]
        return "; ".join(top_genres) if top_genres else None
