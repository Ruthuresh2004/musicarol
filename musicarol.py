import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMainWindow
from controller.main_controller import Controller
from logic.core_logic import Logic
from ui.main_window import Ui_MainWindow
from utils.utilities import APP_NAME


class MainWindow(QMainWindow):
    def __init__(self, controller, app):
        super().__init__()
        self.controller = controller
        self._app = app

    def closeEvent(self, event):
        self.controller.shutdown()
        self._app.quit()
        self._app.exit(0)
        event.accept()


if __name__ == "__main__":

    settings = QSettings(APP_NAME, APP_NAME)

    logging.basicConfig(
        filename='app.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    app = QApplication(sys.argv)

    logic = Logic(settings, logging)
    ui = Ui_MainWindow(settings)
    controller = Controller(logic, ui)

    MainWindow = MainWindow(controller, app)
    ui.setupUi(MainWindow)

    ui.songsTreeWidget.controller = controller

    MainWindow.show()

    try:
        if hasattr(logic, "show_startup_warning"):
            logic.show_startup_warning()
        if hasattr(logic, "show_startup_help"):
            logic.show_startup_help()
    except Exception as e:
        import traceback
        print(e)

    sys.exit(app.exec_())
