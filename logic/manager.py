from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TYER
from mutagen.mp3 import MP3
from utils.utilities import MP3TAG_TITLE, MP3TAG_ARTIST, MP3TAG_ALBUM, MP3TAG_GENRE, MP3TAG_RECORDING_YEAR, \
    MP3TAG_YEAR


class MP3MetadataManager:
    def __init__(self, extractor, logging):
        self.extractor = extractor
        self.logging = logging

    def get_all_tags(self, ruta_mp3):

        try:
            return {
                "Título": self.extractor.get_song_tag(ruta_mp3, MP3TAG_TITLE),
                "Artista": self.extractor.get_song_tag(ruta_mp3, MP3TAG_ARTIST),
                "Álbum": self.extractor.get_song_tag(ruta_mp3, MP3TAG_ALBUM),
                "Género": self.extractor.get_song_tag(ruta_mp3, MP3TAG_GENRE),
                "Año": self.extractor.get_song_year(ruta_mp3)
            }
        except Exception as e:
            self.logging.warning(f"Error al leer metadatos en {ruta_mp3}: {e}")
            return {}

    def update_metadata_in_file(self, mp3_path, changes):
        try:
            audio = MP3(mp3_path, ID3=ID3)
            for tag, new_value in changes.items():
                if tag.lower() == "título":
                    audio.tags[MP3TAG_TITLE] = TIT2(encoding=3, text=new_value)
                elif tag.lower() == "artista":
                    audio.tags[MP3TAG_ARTIST] = TPE1(encoding=3, text=new_value)
                elif tag.lower() == "álbum":
                    audio.tags[MP3TAG_ALBUM] = TALB(encoding=3, text=new_value)
                elif tag.lower() == "género":
                    audio.tags[MP3TAG_GENRE] = TCON(encoding=3, text=new_value)
                elif tag.lower() == "año":
                    audio.tags[MP3TAG_RECORDING_YEAR] = TDRC(encoding=3, text=new_value)
                    audio.tags[MP3TAG_YEAR] = TYER(encoding=3, text=new_value)

            audio.save()
            self.logging.info(f"Metadatos guardados para {mp3_path}")

        except Exception as e:
            self.logging.error(f"Error al guardar metadatos en {mp3_path}: {e}")
