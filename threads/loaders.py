from PyQt5.QtCore import QThread, pyqtSignal


class FolderLoaderThread(QThread):
    datos_cargados = pyqtSignal(dict)

    def __init__(self, logic, archivos_por_carpeta, carpeta_raiz, logging):
        super().__init__()
        self.logging = logging
        self.logic = logic
        self.archivos_por_carpeta = archivos_por_carpeta
        self.carpeta_raiz = carpeta_raiz

    def run(self):
        try:
            datos = self.logic.prepare_file_data_by_folder(self.archivos_por_carpeta, self.carpeta_raiz)
            self.datos_cargados.emit(datos)
        except Exception as e:
            self.logging.error(f"Error en FilesLoaderThread: {e}")


class FilesLoaderThread(QThread):
    loaded_songs = pyqtSignal(list)

    def __init__(self, logic, archivos_mp3, logging):
        super().__init__()
        self.logging = logging
        self.logic = logic
        self.archivos_mp3 = archivos_mp3

    def run(self):
        try:
            canciones = self.logic.prepare_file_data(self.archivos_mp3)
            self.loaded_songs.emit(canciones)
        except Exception as e:
            self.logging.error(f"Error en FilesLoaderThread: {e}")
