from PyQt5.QtCore import QThread, pyqtSignal


class FolderLoaderThread(QThread):
    loaded_data = pyqtSignal(dict)

    def __init__(self, logic, files_by_folder, root_folder, logging):
        super().__init__()
        self.logging = logging
        self.logic = logic
        self.files_by_folder = files_by_folder
        self.root_folder = root_folder

    def run(self):
        try:
            data = self.logic.prepare_file_data_by_folder(self.files_by_folder, self.root_folder)
            self.loaded_data.emit(data)
        except Exception as e:
            self.logging.error(f"Error en FilesLoaderThread: {e}")


class FilesLoaderThread(QThread):
    loaded_songs = pyqtSignal(list)

    def __init__(self, logic, mp3_files, logging):
        super().__init__()
        self.logging = logging
        self.logic = logic
        self.mp3_files = mp3_files

    def run(self):
        try:
            songs = self.logic.prepare_file_data(self.mp3_files)
            self.loaded_songs.emit(songs)
        except Exception as e:
            self.logging.error(f"Error en FilesLoaderThread: {e}")
