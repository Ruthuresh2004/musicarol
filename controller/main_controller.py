import os

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QApplication, QTableWidgetItem, QMessageBox, QProgressDialog
from PyQt5 import QtCore, QtWidgets
from mutagen.mp3 import MP3
from threads.loaders import FolderLoaderThread, FilesLoaderThread
from threads.savers import SaveThread
from utils.utilities import MP3TAG_RECORDING_YEAR, MP3TAG_YEAR


class Controller:

    def __init__(self, logic, ui):
        self.search_success_sound = QSoundEffect()
        self.search_success_sound.setSource(QUrl.fromLocalFile("resources/sounds/search_sound.wav"))
        self.search_success_sound.setVolume(0.5)
        self.files_loader = None
        self.folder_loader = None
        self.save_thread = None
        self.logic = logic
        self.ui = ui
        self.shutdown_process = False
        self.progress_dialog = None

        self.ui.set_callbacks(
            on_add_folder=self.on_add_folder,
            on_add_files=self.on_add_files,
            on_save_changes=self.save_changes,
            on_group_by_grouping=self.group_by_grouping_type,
            on_item_clicked=self.show_metadata,
            on_item_changed=self.logic.update_item_checkboxes,
            on_cell_changed=self.on_metadata_cell_edited,
            on_search_artist=self.on_search_artist,
            on_search_genre=self.on_search_genre,
            on_radio_button_checked=self.ui.exclude_checkboxes,
            on_group_by_artist=self.group_by_artist,
            on_group_by_genre=self.group_by_genre,
            on_group_by_album=self.group_by_album,
            on_group_by_decade=self.group_by_decade,
            on_reset_warnings=self.logic.change_resest_warnings_settings,
            on_show_startup_help=self.logic.change_show_startup_help_preference,
            on_change_save_preference=self.update_save_preference,
            on_change_grouping_preference=self.logic.change_grouping_preference,
            on_change_stylesheet=self.update_and_apply_stylesheet
        )

    # ==============================
    # FILES
    # ==============================

    def on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta con MP3s")
        if not folder:
            return

        files_by_folder = {}
        for root, _, files in os.walk(folder):
            if self.shutdown_process:
                self.logic.logging.error(f"Carga de carpetas detenida antes de la finalización.")
                return
            QApplication.processEvents()
            mp3s = [os.path.join(root, f) for f in files if f.endswith(".mp3")]
            if mp3s:
                files_by_folder[root] = mp3s

        self.ui.songsTreeWidget.clear()

        self.folder_loader = FolderLoaderThread(self.logic, files_by_folder, folder, self.logic.logging)
        self.folder_loader.datos_cargados.connect(self._on_folder_data_loaded)
        self.folder_loader.start()
        self.progress_dialog = QProgressDialog("Cargando archivos...", None, 0, 0, self.ui.MainWindow)
        self.progress_dialog.setWindowTitle("Espere...")
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

    def _on_folder_data_loaded(self, data):
        self.progress_dialog.close()

        for folder, songs in data.items():
            if self.shutdown_process:
                self.logic.logging.error(f"Carga de archivos detenida antes de la finalización.")
                return
            folder_name = (
                f"📂 Archivos desagrupados ({len(songs)})" if folder == "desagrupados"
                else f"📁 {folder} ({len(songs)})"
            )
            root_item = QTreeWidgetItem([folder_name])
            self.ui.songsTreeWidget.addTopLevelItem(root_item)

            for song in songs:
                if self.shutdown_process:
                    self.logic.logging.error(f"Carga de archivos detenida antes de la finalización.")
                    return
                QApplication.processEvents()
                try:
                    item = QTreeWidgetItem([song["titulo"], song["artista"]])
                    item.setData(0, QtCore.Qt.UserRole, song["path"])
                    root_item.addChild(item)

                except Exception as e:
                    self.logic.logging.error(f"Error al procesar {song}: {e}")

        self.ui.songsTreeWidget.expandAll()
        self.folder_loader.quit()
        self.folder_loader.wait()

    def on_add_files(self, loaded_mp3_files):
        if loaded_mp3_files:
            mp3_files = loaded_mp3_files
        else:
            mp3_files, _ = QFileDialog.getOpenFileNames(None, "Seleccionar archivos MP3", "", "Archivos MP3 (*.mp3)")
            if not mp3_files:
                return

        self.ui.songsTreeWidget.clear()

        self.files_loader = FilesLoaderThread(self.logic, mp3_files, self.logic.logging)
        self.files_loader.loaded_songs.connect(self._on_song_files_loaded)
        self.files_loader.start()
        self.progress_dialog = QProgressDialog("Cargando archivos...", None, 0, 0, self.ui.MainWindow)
        self.progress_dialog.setWindowTitle("Espere...")
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

    def _on_song_files_loaded(self, songs):
        self.progress_dialog.close()

        raiz = QTreeWidgetItem([f"📂 Archivos desagrupados ({len(songs)})"])
        self.ui.songsTreeWidget.addTopLevelItem(raiz)

        for song in songs:
            if self.shutdown_process:
                self.logic.logging.error(f"Carga de archivos detenida antes de la finalización.")
                return
            try:
                item = QTreeWidgetItem([song["titulo"], song["artista"]])
                item.setData(0, QtCore.Qt.UserRole, song["path"])
                raiz.addChild(item)

            except Exception as e:
                import traceback
                self.logic.logging.error(f"Error al procesar {song}: {e}")

        self.ui.songsTreeWidget.expandAll()
        self.files_loader.quit()
        self.files_loader.wait()

    # ==============================
    # METADATA HANDLING
    # ==============================

    def _update_metadata_table(self, tags, mp3_path):
        previous_changes = self.logic.metadata_changes.get(mp3_path, {})

        for i, (key, value) in enumerate(tags.items()):
            self.ui.tagsTableWidget.insertRow(i)

            item_tag = QtWidgets.QTableWidgetItem(key)
            item_tag.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tagsTableWidget.setItem(i, 0, item_tag)

            item_valor = QtWidgets.QTableWidgetItem(value)
            item_valor.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tagsTableWidget.setItem(i, 1, item_valor)

            new_tag_value = previous_changes.get(key, value)
            new_value_item = QtWidgets.QTableWidgetItem(new_tag_value)
            new_value_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.ui.tagsTableWidget.setItem(i, 2, new_value_item)

    def show_metadata(self, item):
        title = item.text(0)
        mp3_path = self.logic.song_paths.get(title)

        if not mp3_path:
            return

        tags = self.logic.mp3_metadata_manager.get_all_tags(mp3_path)

        self.ui.tagsTableWidget.setRowCount(0)
        current_artist = tags.get("Artista", "Desconocido")
        has_artist = current_artist.lower() != "desconocido"

        self.ui.btnBuscarGenero.setEnabled(has_artist)
        self.ui.actionBuscarGenero.setEnabled(has_artist)

        self._update_metadata_table(tags, mp3_path)

        image_data = self.logic.mp3_data_extractor.get_mp3_cover_image(mp3_path)
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.coverLabel.setPixmap(scaled)
        else:
            self.ui.coverLabel.clear()

    def on_metadata_cell_edited(self, row, column):
        if column != 2:
            return

        tag_title_item = self.ui.tagsTableWidget.item(row, 0)
        current_value_item = self.ui.tagsTableWidget.item(row, 1)
        new_value_item = self.ui.tagsTableWidget.item(row, 2)

        if not tag_title_item or not new_value_item or not current_value_item:
            return

        tag = tag_title_item.text()
        new = new_value_item.text()
        current = current_value_item.text()

        current_item = self.ui.songsTreeWidget.currentItem() or self.ui.playlistsTreeWidget.currentItem()

        if not current_item:
            return

        mp3_path = self.logic.song_paths.get(current_item.text(0))

        if not mp3_path:
            return

        if mp3_path not in self.logic.metadata_changes:
            self.logic.metadata_changes[mp3_path] = {}

        self.ui.tagsTableWidget.blockSignals(True)

        if new != current:
            self.logic.metadata_changes[mp3_path][tag] = new
        else:
            self.logic.metadata_changes[mp3_path].pop(tag, None)

        if mp3_path in self.logic.metadata_changes and not self.logic.metadata_changes[mp3_path]:
            del self.logic.metadata_changes[mp3_path]

        self.ui.tagsTableWidget.blockSignals(False)

    # ==============================
    # API QUERIES
    # ==============================

    def on_search_artist(self):
        item = self.ui.songsTreeWidget.currentItem() or self.ui.playlistsTreeWidget.currentItem()
        self.ui.btnBuscarArtista.setEnabled(False)

        if not item:
            self.logic.logging.warning("Seleccione un track.")
            self.ui.btnBuscarArtista.setEnabled(True)
            return

        title = item.text(0)
        path = self.logic.song_paths.get(title)

        if not path:
            self.logic.logging.warning("Ruta del archivo no encontrada.")
            self.ui.btnBuscarArtista.setEnabled(True)
            return

        try:
            audio = MP3(path)
            duration_ms = int(audio.info.length * 1000)
            tags = audio.tags
            year = None

            if MP3TAG_RECORDING_YEAR in tags:
                year = str(tags[MP3TAG_RECORDING_YEAR][0])
            elif MP3TAG_YEAR in tags:
                year = str(tags[MP3TAG_YEAR][0])
            if year and len(year) > 4:
                year = year[:4]

        except Exception as e:
            self.logic.logging.error(f"Error al leer duración o año del MP3: {e}")
            self.ui.btnBuscarArtista.setEnabled(True)
            return

        artist = self.logic.get_artist_api(title, year, duration_ms)

        for row in range(self.ui.tagsTableWidget.rowCount()):
            item_tag = self.ui.tagsTableWidget.item(row, 0)
            if item_tag and item_tag.text().strip().lower() == "artista":
                self.ui.tagsTableWidget.setItem(row, 2, QTableWidgetItem(artist))
                self.search_success_sound.play()
                break

        self.ui.btnBuscarArtista.setEnabled(True)

    def on_search_genre(self):
        item = self.ui.songsTreeWidget.currentItem() or self.ui.playlistsTreeWidget.currentItem()

        if not item:
            self.logic.logging.warning("Seleccione un item")
            return

        artist_name = item.text(1)
        genre = self.logic.get_genre_api(artist_name)

        if not genre:
            self.logic.logging.error("Género no encontrado")
            return

        for row in range(self.ui.tagsTableWidget.rowCount()):
            item_tag = self.ui.tagsTableWidget.item(row, 0)
            if item_tag and item_tag.text().strip().lower() == "género":
                self.ui.tagsTableWidget.setItem(row, 2, QTableWidgetItem(genre.replace(",", ";")))
                self.search_success_sound.play()
                break

    # ==============================
    # GROUPING FUNCTIONS
    # ==============================

    def group_by_artist(self):
        self.ui.playlistsTreeWidget.clear()
        artists = {}

        for i in range(self.ui.songsTreeWidget.topLevelItemCount()):
            root = self.ui.songsTreeWidget.topLevelItem(i)

            for j in range(root.childCount()):
                item = root.child(j)
                title = item.text(0)
                artist = item.text(1)

                if artist not in artists:
                    artists[artist] = QTreeWidgetItem([artist])
                    self.logic.add_checkboxes_to_items(artists[artist])
                    self.ui.playlistsTreeWidget.addTopLevelItem(artists[artist])

                item_song = QTreeWidgetItem([title, artist])
                self.logic.add_checkboxes_to_items(item_song)
                artists[artist].addChild(item_song)

        self.ui.playlistsTreeWidget.expandAll()

    def group_by_main_genre(self):
        self.ui.playlistsTreeWidget.clear()
        genres = {}

        for i in range(self.ui.songsTreeWidget.topLevelItemCount()):
            root = self.ui.songsTreeWidget.topLevelItem(i)

            for j in range(root.childCount()):
                item = root.child(j)
                title = item.text(0)
                artist = item.text(1)
                path = self.logic.song_paths.get(title, "")

                main_genres = self.logic.get_main_genres(path)

                for genre in main_genres:
                    if genre not in genres:
                        genres[genre] = QTreeWidgetItem([genre])
                        self.logic.add_checkboxes_to_items(genres[genre])
                        self.ui.playlistsTreeWidget.addTopLevelItem(genres[genre])

                    item_song = QTreeWidgetItem([title, artist])
                    self.logic.add_checkboxes_to_items(item_song)
                    genres[genre].addChild(item_song)

        self.ui.playlistsTreeWidget.expandAll()

    def group_by_specific_genre(self):
        self.ui.playlistsTreeWidget.clear()
        genres = {}

        for i in range(self.ui.songsTreeWidget.topLevelItemCount()):
            root = self.ui.songsTreeWidget.topLevelItem(i)

            for j in range(root.childCount()):
                item = root.child(j)
                title = item.text(0)
                artist = item.text(1)
                path = self.logic.song_paths.get(title, "")

                specific_genres = self.logic.get_specific_genres(path)

                for genre in specific_genres:
                    if genre not in genres:
                        genres[genre] = QTreeWidgetItem([genre.capitalize()])
                        self.logic.add_checkboxes_to_items(genres[genre])
                        self.ui.playlistsTreeWidget.addTopLevelItem(genres[genre])

                    item_song = QTreeWidgetItem([title, artist])
                    self.logic.add_checkboxes_to_items(item_song)
                    genres[genre].addChild(item_song)

        self.ui.playlistsTreeWidget.expandAll()

    def group_by_genre(self):
        if self.logic.grouping_preference == "especifico":
            self.group_by_specific_genre()
        else:
            self.group_by_main_genre()

    def group_by_album(self):
        self.ui.playlistsTreeWidget.clear()
        albumes = {}

        for i in range(self.ui.songsTreeWidget.topLevelItemCount()):
            raiz = self.ui.songsTreeWidget.topLevelItem(i)

            for j in range(raiz.childCount()):
                item = raiz.child(j)
                titulo = item.text(0)
                artista = item.text(1)
                ruta = self.logic.song_paths.get(titulo, "")

                album = self.logic.get_album(ruta)

                if album not in albumes:
                    albumes[album] = QTreeWidgetItem([album])
                    self.logic.add_checkboxes_to_items(albumes[album])
                    self.ui.playlistsTreeWidget.addTopLevelItem(albumes[album])

                hijo = QTreeWidgetItem([titulo, artista])
                self.logic.add_checkboxes_to_items(hijo)
                albumes[album].addChild(hijo)

        self.ui.playlistsTreeWidget.expandAll()

    def group_by_decade(self):
        self.ui.playlistsTreeWidget.clear()
        decades = {}

        for i in range(self.ui.songsTreeWidget.topLevelItemCount()):
            root = self.ui.songsTreeWidget.topLevelItem(i)

            for j in range(root.childCount()):
                item = root.child(j)
                title = item.text(0)
                artist = item.text(1)
                path = self.logic.song_paths.get(title, "")

                decade = self.logic.get_decade(path)

                if decade not in decades:
                    decades[decade] = QTreeWidgetItem([decade])
                    self.logic.add_checkboxes_to_items(decades[decade])
                    self.ui.playlistsTreeWidget.addTopLevelItem(decades[decade])

                item_song = QTreeWidgetItem([title, artist])
                self.logic.add_checkboxes_to_items(item_song)
                decades[decade].addChild(item_song)

        self.ui.playlistsTreeWidget.expandAll()

    def group_by_grouping_type(self):
        grouping_type = self.ui.comboAgrupar.currentText()

        if grouping_type == "Agrupar por artista":
            self.group_by_artist()
        elif grouping_type == "Agrupar por género":
            self.group_by_genre()
        elif grouping_type == "Agrupar por álbum":
            self.group_by_album()
        elif grouping_type == "Agrupar por década":
            self.group_by_decade()

        for i in range(self.ui.playlistsTreeWidget.topLevelItemCount()):
            item = self.ui.playlistsTreeWidget.topLevelItem(i)
            item.setText(0, f"{item.text(0)} ({item.childCount()})")

    # ==============================
    # SAVE
    # ==============================

    def save_changes(self):
        if not self.logic.metadata_changes and self.ui.playlistsTreeWidget.topLevelItemCount() == 0:
            QMessageBox.information(None, "Guardar", "No hay cambios para guardar.")
            return

        user_response = QMessageBox.question(
            None,
            "Confirmar guardado",
            "¿Deseas guardar los cambios en los archivos MP3?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if user_response != QMessageBox.Yes:
            return

        save_folders = self.ui.checkboxFolder.isChecked()
        save_m3u = self.ui.checkboxM3u.isChecked()

        playlist_folder = None
        if save_folders or save_m3u:
            playlist_folder = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta para guardar las playlists.")
            if not playlist_folder:
                self.logic.logging.error("Error: No se seleccionó una carpeta.")
                return

        self.progress_dialog = QProgressDialog("Guardando cambios...", None, 0, 0, self.ui.MainWindow)
        self.progress_dialog.setWindowTitle("Espere...")
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        self.save_thread = SaveThread(
            self.logic,
            self.ui.playlistsTreeWidget,
            playlist_folder,
            save_m3u,
            save_folders,
            self.logic.logging
        )

        self.save_thread.process_finished.connect(self._on_save_completed)
        self.save_thread.start()

    def _on_save_completed(self):
        self.progress_dialog.close()
        QMessageBox.information(None, "Éxito", "Todos los cambios se han guardado correctamente.", QMessageBox.Ok)

    # ==============================
    # SETTINGS
    # ==============================

    def update_and_apply_stylesheet(self, stylesheet):
        self.logic.settings.setValue("layout_style", stylesheet)

        if self.ui.MainWindow is not None:
            self.ui.MainWindow.setStyleSheet(self.ui.layoutLoader())
        else:
            self.logic.logging.error("MainWindow no está inicializado")

    def update_save_preference(self, preference):
        if preference == "symlink" and self.ui.actionSymlink.isChecked():
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Advertencia")
            msg_box.setText(
                "Para que los enlaces simbólicos funcionen correctamente debes ejecutar la aplicación como administrador. "
                "\n\nSi seleccionas esta opción y la aplicación no tiene los permisos necesarios para crear enlaces simbólicos, "
                "se realizará automáticamente una copia de los archivos en su lugar."
            )
            checkbox = QtWidgets.QCheckBox("No volver a mostrar")
            msg_box.setCheckBox(checkbox)

            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

            msg_box.exec_()

            if checkbox.isChecked():
                self.ui.settings.setValue("mostrar_advertencia_symlink", "false")

        self.logic.change_save_preference(preference)

    # ==============================
    # SHUTDOWN
    # ==============================

    def shutdown(self):

        self.shutdown_process = True

        self.logic.shutdown()

        if self.folder_loader and self.folder_loader.isRunning():
            self.folder_loader.quit()
            self.folder_loader.wait()

        if self.files_loader and self.files_loader.isRunning():
            self.files_loader.quit()
            self.files_loader.wait()

        if self.save_thread and self.save_thread.isRunning():
            self.save_thread.interrupt()
            self.save_thread.quit()
            self.save_thread.wait()
