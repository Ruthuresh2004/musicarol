import os
import shutil

from PyQt5.QtCore import QThread, pyqtSignal


class SaveThread(QThread):
    process_finished = pyqtSignal()

    def __init__(self, logic, playlists_tree, playlist_folder, save_m3u, save_folders, logging):
        super().__init__()
        self.logic = logic
        self.playlists_tree = playlists_tree
        self.playlist_folder = playlist_folder
        self.save_m3u = save_m3u
        self.save_folders = save_folders
        self.logging = logging
        self.interrupted = False

    def interrupt(self):
        self.interrupted = True

    def run(self):
        try:
            self.logic.save_metadata()

            if self.save_m3u:
                self._save_playlists_as_m3u()

            if self.save_folders:
                self._save_playlists_as_folders()

        except Exception as e:
            self.logging.error(f"Error al guardar: {e}")
        finally:
            self.process_finished.emit()

    def _save_playlists_as_m3u(self):
        for i in range(self.playlists_tree.topLevelItemCount()):
            playlists_root = self.playlists_tree.topLevelItem(i)
            if playlists_root.checkState(0):
                playlist_name = playlists_root.text(0).split(" ")[0]
                m3u_filename = os.path.join(self.playlist_folder, f"{playlist_name}.m3u")

                if self.interrupted:
                    self.logging.error(f"Guardado de archivos detenida antes de la finalización.")
                    return

                try:
                    with open(m3u_filename, "w", encoding="utf-8") as m3u_file:
                        m3u_file.write("#EXTM3U\n")
                        for j in range(playlists_root.childCount()):
                            sub_item = playlists_root.child(j)
                            if sub_item.checkState(0):
                                title = sub_item.text(0)
                                artist = sub_item.text(1)
                                mp3_path = self.logic.song_paths.get(title).replace("\\", "/")
                                if mp3_path:
                                    m3u_file.write(f"#EXTINF:-1,{title} - {artist}\n")
                                    m3u_file.write(f"{mp3_path}\n")
                    self.logging.info(f"Playlist guardada en {m3u_filename}")
                except Exception as e:
                    self.logging.error(f"Error al guardar .m3u para {playlist_name}: {e}")

    def _save_playlists_as_folders(self):
        for i in range(self.playlists_tree.topLevelItemCount()):
            playlists_root = self.playlists_tree.topLevelItem(i)
            if playlists_root.checkState(0):
                playlist_name = playlists_root.text(0).split(" ")[0]
                destination_folder = os.path.join(self.playlist_folder, playlist_name)
                os.makedirs(destination_folder, exist_ok=True)

                for j in range(playlists_root.childCount()):

                    if self.interrupted:
                        self.logging.error(f"Guardado de archivos detenida antes de la finalización.")
                        return

                    sub_item = playlists_root.child(j)
                    if sub_item.checkState(0):
                        song_title = sub_item.text(0)
                        mp3_path = self.logic.song_paths.get(song_title)

                        if mp3_path:
                            new_file_path = os.path.join(destination_folder, os.path.basename(mp3_path))
                            try:
                                if self.logic.save_preference == "copiar":
                                    shutil.copy(mp3_path, new_file_path)
                                    self.logging.info(f"Copiado: {mp3_path} -> {new_file_path}")
                                else:
                                    try:
                                        os.symlink(mp3_path, new_file_path)
                                        self.logging.info(f"Symlink: {mp3_path} -> {new_file_path}")
                                    except OSError as e:
                                        self.logging.warning(f"Fallo symlink. Copiando. Error: {e}")
                                        shutil.copy(mp3_path, new_file_path)
                            except Exception as e:
                                self.logging.error(f"Error procesando {mp3_path}: {e}")
