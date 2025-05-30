from PyQt5 import QtCore, QtWidgets
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from logic.extractor import MP3DataExtractor
from logic.manager import MP3MetadataManager
from logic.musicbrainz_api import MusicBrainzAPI
from ui.help_window import HelpWindow
from PyQt5.QtMultimedia import QSound

from utils.utilities import MP3TAG_TITLE, TOLERANCE_MS, GENRES_MAP, MAIN_GENRE_KEYWORDS, MP3TAG_ALBUM, \
    MP3TAG_GENRE, MP3TAG_ARTIST


class Logic:

    song_paths = {}
    metadata_changes = {}

    def __init__(self, settings, logging):
        self.settings = settings
        self.mp3_data_extractor = MP3DataExtractor(logging)
        self.musicbrainzapi = MusicBrainzAPI(logging)
        self.mp3_metadata_manager = MP3MetadataManager(self.mp3_data_extractor, logging)
        self.startup_help_window = None
        self.shutdown_process = False
        self.logging = logging

        self.settings.setValue("preferencia_guardado", "copiar")
        self.save_preference = "copiar"
        self.settings.setValue("preferencia_modo_agrupacion", "general")
        self.grouping_preference = "general"
        self.show_symlink_warning_preference = self.settings.value("mostrar_advertencia_symlink", "true")
        self.layout_style = self.settings.value("layout_style", "red")

    def change_save_preference(self, preference):
        self.settings.setValue("preferencia_guardado", preference)
        self.save_preference = self.settings.value("preferencia_guardado", preference)

    def change_grouping_preference(self, preference):
        self.settings.setValue("preferencia_modo_agrupacion", preference)
        self.grouping_preference = preference

    def change_show_startup_help_preference(self, checked):
        self.settings.setValue("mostrar_ventana_ayuda", "true" if checked else "false")

    def change_resest_warnings_settings(self):
        self.settings.setValue("mostrar_advertencia_inicial", "true")
        self.settings.setValue("mostrar_advertencia_symlink", "true")

    @staticmethod
    def add_checkboxes_to_items(item):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

    @staticmethod
    def update_item_checkboxes(item):
        if item.childCount() > 0:
            estado = item.checkState(0)
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, estado)

    def prepare_file_data(self, mp3_files):
        result = []

        for file in mp3_files:
            if self.shutdown_process:
                return result
            title = self.mp3_data_extractor.get_song_tag(file, MP3TAG_TITLE)
            artist = self.mp3_data_extractor.get_song_tag(file, MP3TAG_ARTIST)
            if title == "Desconocido":
                title = os.path.basename(file)

            result.append({
                "titulo": title,
                "artista": artist,
                "path": os.path.normpath(file)
            })

            self.song_paths[title] = os.path.normpath(file)

        return result

    def prepare_file_data_by_folder(self, files_by_folder, root_folder):
        structure = {}

        for folder, files in files_by_folder.items():
            if self.shutdown_process:
                return structure
            key = "desagrupados" if folder == root_folder else os.path.relpath(folder, root_folder)
            structure[key] = self.prepare_file_data(files)
            QApplication.processEvents()

        return structure

    def get_artist_api(self, title, year, duracion_ms):
        query = f'recording:"{title}"'
        if year:
            query += f' AND date:{year}'

        recordings = self.musicbrainzapi.search_recordings(query)
        matches = [r for r in recordings if "length" in r and abs(r["length"] - duracion_ms) <= TOLERANCE_MS]

        best_match = max(matches or recordings, key=lambda r: r.get("score", 0), default=None)
        artist = best_match["artist-credit"][0]["name"] if best_match else "Desconocido"
        return artist

    def get_genre_api(self, artist_name):
        artist_id = self.musicbrainzapi.get_artist_id(artist_name)
        if not artist_id:
            return None

        genres = self.musicbrainzapi.get_artist_genres(artist_id)
        if not genres:
            return None

        top_genres = [tag["name"] for tag in sorted(genres, key=lambda x: x["count"], reverse=True)[:3]]
        return "; ".join(top_genres) if top_genres else None

    @staticmethod
    def _map_to_main_genres(genre_string):
        main_genres = set()

        if not genre_string or genre_string.strip().lower() == "desconocido":
            main_genres.add("Desconocido")
            return main_genres

        genres_list = genre_string.split(";")

        for genre in genres_list:
            genre = genre.strip().lower()

            if genre in GENRES_MAP:
                main_genres.add(GENRES_MAP[genre])
            else:
                for keyword in MAIN_GENRE_KEYWORDS:
                    if keyword in genre:
                        main_genres.add(keyword.capitalize())
                        break
                else:
                    main_genres.add("Otro")

        return main_genres

    def get_album(self, mp3_path):
        return self.mp3_data_extractor.get_song_tag(mp3_path, MP3TAG_ALBUM)

    def get_main_genres(self, mp3_path):
        genre_string = self.mp3_data_extractor.get_song_tag(mp3_path, MP3TAG_GENRE)
        return self._map_to_main_genres(genre_string)

    def get_specific_genres(self, mp3_path):
        genre_string = self.mp3_data_extractor.get_song_tag(mp3_path, MP3TAG_GENRE)
        return [g.strip().lower() for g in genre_string.split("; ") if g.strip()]

    def get_decade(self, mp3_path):
        year_str = self.mp3_data_extractor.get_song_year(mp3_path)
        try:
            year = int(year_str[:4])
            return f"{year // 10 * 10}s"
        except Exception as e:
            self.logging.error(f"No ha sido posible extraer el año de {mp3_path}: {e}")
            return "Desconocido"

    def save_metadata(self):
        for mp3_path, changes in self.metadata_changes.items():
            self.mp3_metadata_manager.update_metadata_in_file(mp3_path, changes)

        self.metadata_changes.clear()

    def show_startup_warning(self):

        if self.settings.value("mostrar_advertencia_inicial") == "true":

            msg_box = QMessageBox()
            msg_box.setWindowTitle("Advertencia de nuevo usuario")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(
                "Los cambios realizados en los metadatos son permanentes.\n\n"
                "Esta herramienta puede renombrar archivos y sobrescribir etiquetas. "
                "Te recomendamos:\n\n"
                "- Leer la documentación en el menú Ayuda.\n"
                "- Probar los resultados con copias de tu música.\n"
                "- Trabajar en pequeños lotes de archivos."
            )
            msg_box.setInformativeText("¿Deseas continuar?")
            msg_box.setStandardButtons(QMessageBox.Ok)

            checkbox = QtWidgets.QCheckBox("No volver a mostrar este mensaje")
            msg_box.setCheckBox(checkbox)

            resultado = msg_box.exec_()

            if resultado == QMessageBox.Ok and checkbox.isChecked():
                self.settings.setValue("mostrar_advertencia_inicial", "false")

    def show_startup_help(self):
        show = self.settings.value("mostrar_ventana_ayuda", "true")
        if show == "true":

            try:
                if self.startup_help_window is None:
                    self.startup_help_window = HelpWindow()
                    self.startup_help_window.setWindowFlag(Qt.WindowStaysOnTopHint)

                self.startup_help_window.show()
                QSound.play("resources/sounds/startup_sound.wav")
                self.startup_help_window.raise_()
                self.startup_help_window.activateWindow()

            except Exception as e:
                self.logging.error(f"Error al mostrar la ventana de ayuda: {e}")

    def shutdown(self):
        self.shutdown_process = True
