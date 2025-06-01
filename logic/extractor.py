import logging

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


class MP3DataExtractor:
    def __init__(self, logging):
        self.logging = logging

    def get_mp3_cover_image(self, mp3_path):
        try:
            audio = ID3(mp3_path)
            for tag in audio.values():
                if isinstance(tag, APIC):
                    return tag.data
        except Exception as e:
            self.logging.warning(f"No se pudo obtener la imagen: {e}")
        return None

    def get_song_tag(self, mp3_file, tag):
        try:
            audio = MP3(mp3_file, ID3=ID3)
            tag_value = audio.tags.get(tag, ["Desconocido"])[0]
            return tag_value
        except Exception as e:
            self.logging.warning(f"Error al leer metadatos en {mp3_file}: {e}")
            return "Desconocido"

    def get_song_year(self, mp3_file):
        try:
            audio = MP3(mp3_file, ID3=ID3)
            tags = audio.tags

            if "TDRC" in tags:
                return str(tags["TDRC"][0])
            elif "TYER" in tags:
                return str(tags["TYER"][0])
            else:
                return "Desconocido"
        except Exception as e:
            self.logging.warning(f"Error al leer año de {mp3_file}: {e}")
            return "Desconocido"
