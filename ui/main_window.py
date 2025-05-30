from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from utils.helpers import load_stylesheet
from utils.utilities import APP_NAME
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt


class DropTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mp3_files = []

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".mp3"):
                mp3_files.append(file_path)

        if mp3_files:
            self.controller.on_add_files(mp3_files)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()


class Ui_MainWindow(object):
    def __init__(self, settings):
        self.MainWindow = None
        self.callbacks = {}
        self.settings = settings
        self.songsTreeWidget = DropTreeWidget()

    def set_callbacks(self, **kwargs):
        if self.callbacks is None:
            self.callbacks = {}
        self.callbacks.update(kwargs)

    def setupUi(self, MainWindow):

        mostrar_ayuda = self.settings.value("mostrar_ventana_ayuda", "true") == "true"

        MainWindow.setObjectName(APP_NAME)
        MainWindow.setWindowTitle(APP_NAME)
        MainWindow.setWindowIcon(QIcon("resources/icons/icon.ico"))
        MainWindow.resize(1010, 700)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ==============================
        # LAYOUT HORIZONTAL PARA BOTONES PRINCIPALES
        # ==============================
        top_buttons_layout = QHBoxLayout()
        self.btnAgregarCarpeta = QtWidgets.QPushButton("Agregar carpeta...")
        self.btnAgregarCarpeta.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnAgregarArchivos = QtWidgets.QPushButton("Agregar archivos...")
        self.btnAgregarArchivos.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.comboAgrupar = QtWidgets.QComboBox()
        self.comboAgrupar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.comboAgrupar.addItems(["Agrupar por artista", "Agrupar por género", "Agrupar por álbum", "Agrupar por década"])
        self.btnAgrupar = QtWidgets.QPushButton("Agrupar")
        self.btnAgrupar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkboxFolder = QtWidgets.QRadioButton("Folder")
        self.checkboxM3u = QtWidgets.QRadioButton(".m3u")
        self.btnGuardar = QtWidgets.QPushButton("Guardar")
        self.btnGuardar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon = QtGui.QIcon("resources/icons/black/save_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.png")
        self.btnGuardar.setIcon(icon)

        top_buttons_layout.addWidget(self.btnAgregarCarpeta)
        top_buttons_layout.addWidget(self.btnAgregarArchivos)

        spacer_between_files_and_grouping = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                                  QtWidgets.QSizePolicy.Minimum)
        top_buttons_layout.addItem(spacer_between_files_and_grouping)

        top_buttons_layout.addWidget(self.comboAgrupar)
        top_buttons_layout.addWidget(self.btnAgrupar)
        top_buttons_layout.addWidget(self.checkboxFolder)
        top_buttons_layout.addWidget(self.checkboxM3u)
        top_buttons_layout.addWidget(self.btnGuardar)

        # ==============================
        # SPLITTER PARA LISTA DE CANCIONES Y PLAYLISTS
        # ==============================
        self.splitter_listas = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # ------------------------------
        # LISTADO DE CANCIONES
        # ------------------------------

        self.songsTreeWidget = DropTreeWidget(parent=self.centralwidget)

        self.songsTreeWidget.setSortingEnabled(True)
        self.songsTreeWidget.sortItems(0, Qt.AscendingOrder)
        self.songsTreeWidget.setColumnCount(2)
        self.songsTreeWidget.setHeaderLabels(["Título", "Artista"])
        self.songsTreeWidget.setColumnWidth(0, 200)
        self.songsTreeWidget.setColumnWidth(1, 150)
        self.songsTreeWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.splitter_listas.addWidget(self.songsTreeWidget)

        # ------------------------------
        # LISTADO DE PLAYLISTS
        # ------------------------------

        self.playlistsTreeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.playlistsTreeWidget.setSortingEnabled(True)
        self.playlistsTreeWidget.sortItems(0, Qt.AscendingOrder)

        self.playlistsTreeWidget.setColumnCount(2)
        self.playlistsTreeWidget.setHeaderLabels(["Título", "Artista"])
        self.playlistsTreeWidget.setColumnWidth(0, 200)
        self.splitter_listas.addWidget(self.playlistsTreeWidget)

        self.splitter_listas.setStretchFactor(0, 1)
        self.splitter_listas.setStretchFactor(1, 1)

        # ==============================
        # TABLA DE METADATOS + IMAGEN
        # ==============================

        self.scrollArea_3 = QtWidgets.QScrollArea()
        self.scrollArea_3.setWidgetResizable(True)

        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()

        metadata_layout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents_3)
        metadata_layout.setContentsMargins(0, 0, 0, 0)

        self.tagsTableWidget = QtWidgets.QTableWidget()
        self.tagsTableWidget.setRowCount(0)
        self.tagsTableWidget.setColumnCount(3)
        self.tagsTableWidget.setHorizontalHeaderLabels(["Etiqueta", "Valor", "Nuevo valor"])

        header = self.tagsTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.coverLabel = QLabel()
        self.coverLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel.setFixedSize(200, 200)

        metadata_layout.addWidget(self.tagsTableWidget, stretch=1)
        metadata_layout.addWidget(self.coverLabel, stretch=0)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.scrollArea_3.setMaximumHeight(250)

        # ==============================
        # LAYOUT HORIZONTAL PARA BOTONES DE BÚSQUEDA
        # ==============================
        bottom_buttons_layout = QHBoxLayout()
        self.btnBuscarArtista = QtWidgets.QPushButton("Buscar artista")
        self.btnBuscarGenero = QtWidgets.QPushButton("Buscar género")
        self.btnBuscarArtista.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnBuscarGenero.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        bottom_buttons_layout.addWidget(self.btnBuscarArtista)
        bottom_buttons_layout.addWidget(self.btnBuscarGenero)
        bottom_buttons_layout.addStretch(1)

        # ==============================
        # LAYOUT VERTICAL PRINCIPAL
        # ==============================
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.addLayout(top_buttons_layout)
        main_layout.addWidget(self.splitter_listas)
        main_layout.addWidget(self.scrollArea_3)
        main_layout.addLayout(bottom_buttons_layout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 21))
        self.menuAgregar_carpeta = QtWidgets.QMenu("&Archivos", self.menubar)
        self.menuHerramientas = QtWidgets.QMenu("Herramien&tas", self.menubar)
        self.menuAyuda = QtWidgets.QMenu("A&yuda", self.menubar)
        self.menuOpciones = QtWidgets.QMenu("&Opciones", self.menubar)
        self.menuVista = QtWidgets.QMenu("&Vista", self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)

        MainWindow.setMenuBar(self.menubar)
        MainWindow.setStatusBar(self.statusbar)

        # ACCIONES DE MENÚ
        self.actionAgregar_carpeta = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/folder_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agregar carpeta...", MainWindow)
        self.actionAgregar_archivos = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/draft_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agregar archivos...", MainWindow)
        self.actionGuardar_2 = QtWidgets.QAction(QtGui.QIcon(
            "resources/icons/white/save_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Guardar", MainWindow)

        self.actionAgruparArtista = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/person_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agrupar por artista",
            MainWindow)
        self.actionAgruparGenero = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/interests_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agrupar por género",
            MainWindow)
        self.actionAgruparAlbum = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/album_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agrupar por álbum",
            MainWindow)
        self.actionAgruparDecada = QtWidgets.QAction(
            QtGui.QIcon("resources/icons/white/calendar_today_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Agrupar por década",
            MainWindow)

        self.actionTipoAgrupacionGenero = QtWidgets.QAction("Agrupación específica", MainWindow)
        self.actionTipoAgrupacionGenero.setCheckable(True)
        self.actionTipoAgrupacionGenero.setChecked(True)

        self.actionBuscarArtista = QtWidgets.QAction(QtGui.QIcon(
            "resources/icons/white/group_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Buscar artista", MainWindow)
        self.actionBuscarGenero = QtWidgets.QAction(QtGui.QIcon(
            "resources/icons/white/category_search_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.png"), "Buscar género", MainWindow)

        self.restablecer_accion = QtWidgets.QAction("Reestablecer advertencias", MainWindow)
        self.actionMostrarAyudaInicio = QtWidgets.QAction("Mostrar ventana de ayuda al iniciar", MainWindow)
        self.actionMostrarAyudaInicio.setCheckable(True)
        self.actionMostrarAyudaInicio.setChecked(mostrar_ayuda)

        self.folderPreferencesActionGroup = QtWidgets.QActionGroup(MainWindow)
        self.submenuGuardadoCarpeta = QtWidgets.QMenu("Guardado en carpeta...", self.menuOpciones)
        self.folderPreferencesActionGroup.setExclusive(True)
        self.actionCopiar = QtWidgets.QAction("Copiar archivos", MainWindow)
        self.actionCopiar.setCheckable(True)
        self.actionSymlink = QtWidgets.QAction("Usar enlaces simbólicos", MainWindow)
        self.actionSymlink.setCheckable(True)
        self.actionCopiar.setChecked(True)

        self.folderPreferencesActionGroup.addAction(self.actionCopiar)
        self.folderPreferencesActionGroup.addAction(self.actionSymlink)

        self.submenuGuardadoCarpeta.addAction(self.actionCopiar)
        self.submenuGuardadoCarpeta.addAction(self.actionSymlink)

        self.genrePreferencesActionGroup = QtWidgets.QActionGroup(MainWindow)
        self.submenuAgrupacionGenero = QtWidgets.QMenu("Tipo de agrupación por género...", self.menuOpciones)
        self.genrePreferencesActionGroup.setExclusive(True)
        self.actionGeneral = QtWidgets.QAction("General", MainWindow)
        self.actionGeneral.setCheckable(True)
        self.actionEspecifico = QtWidgets.QAction("Específico", MainWindow)
        self.actionEspecifico.setCheckable(True)
        self.actionGeneral.setChecked(True)

        self.genrePreferencesActionGroup.addAction(self.actionGeneral)
        self.genrePreferencesActionGroup.addAction(self.actionEspecifico)

        self.submenuAgrupacionGenero.addAction(self.actionGeneral)
        self.submenuAgrupacionGenero.addAction(self.actionEspecifico)

        self.styleActionGroup = QtWidgets.QActionGroup(MainWindow)
        self.styleActionGroup.setExclusive(True)

        self.actionEstiloRojo = QtWidgets.QAction("Rojo DJCarol", MainWindow)
        self.actionEstiloRojo.setCheckable(True)

        self.actionEstiloBlanco = QtWidgets.QAction("Blanco clásico", MainWindow)
        self.actionEstiloBlanco.setCheckable(True)

        self.actionEstiloAzul = QtWidgets.QAction("Azul elegante", MainWindow)
        self.actionEstiloAzul.setCheckable(True)

        self.actionEstiloVerde = QtWidgets.QAction("Verde Cyber", MainWindow)
        self.actionEstiloVerde.setCheckable(True)

        self.submenuCambiarEstilo = QtWidgets.QMenu("Cambiar estilo de ventana", self.menuVista)

        self.styleActionGroup.addAction(self.actionEstiloRojo)
        self.styleActionGroup.addAction(self.actionEstiloBlanco)
        self.styleActionGroup.addAction(self.actionEstiloAzul)
        self.styleActionGroup.addAction(self.actionEstiloVerde)

        self.submenuCambiarEstilo.addAction(self.actionEstiloRojo)
        self.submenuCambiarEstilo.addAction(self.actionEstiloBlanco)
        self.submenuCambiarEstilo.addAction(self.actionEstiloAzul)
        self.submenuCambiarEstilo.addAction(self.actionEstiloVerde)


        # ASIGNACIÓN A MENÚS
        self.menuAgregar_carpeta.addActions(
            [self.actionAgregar_carpeta, self.actionAgregar_archivos])

        self.menuAgregar_carpeta.addSeparator()

        self.menuAgregar_carpeta.addAction(self.actionGuardar_2)

        self.menuHerramientas.addActions([
            self.actionAgruparArtista,
            self.actionAgruparGenero,
            self.actionAgruparAlbum,
            self.actionAgruparDecada
        ])
        self.menuHerramientas.addSeparator()
        self.menuHerramientas.addAction(self.actionBuscarArtista)
        self.menuHerramientas.addAction(self.actionBuscarGenero)

        self.menuAyuda.addActions([self.restablecer_accion, self.actionMostrarAyudaInicio])

        self.menuOpciones.addMenu(self.submenuGuardadoCarpeta)
        self.menuOpciones.addSeparator()
        self.menuOpciones.addMenu(self.submenuAgrupacionGenero)

        self.menuVista.addMenu(self.submenuCambiarEstilo)

        self.menubar.addMenu(self.menuAgregar_carpeta)
        self.menubar.addMenu(self.menuHerramientas)
        self.menubar.addMenu(self.menuAyuda)
        self.menubar.addMenu(self.menuOpciones)
        self.menubar.addMenu(self.menuVista)


        # ==============================
        # CONEXIONES DE SEÑALES
        # ==============================

        self.btnAgregarCarpeta.clicked.connect(self.callbacks.get("on_add_folder"))
        self.actionAgregar_carpeta.triggered.connect(self.callbacks.get("on_add_folder"))
        self.btnAgregarArchivos.clicked.connect(self.callbacks.get("on_add_files"))
        self.actionAgregar_archivos.triggered.connect(self.callbacks.get("on_add_files"))
        self.btnGuardar.clicked.connect(self.callbacks.get("on_save_changes"))
        self.actionGuardar_2.triggered.connect(self.callbacks.get("on_save_changes"))
        self.btnAgrupar.clicked.connect(self.callbacks.get("on_group_by_grouping"))

        self.songsTreeWidget.itemClicked.connect(self.callbacks.get("on_item_clicked"))
        self.playlistsTreeWidget.itemClicked.connect(self.callbacks.get("on_item_clicked"))
        self.playlistsTreeWidget.itemChanged.connect(self.callbacks.get("on_item_changed"))
        self.tagsTableWidget.cellChanged.connect(self.callbacks.get("on_cell_changed"))

        self.btnBuscarArtista.clicked.connect(self.callbacks.get("on_search_artist"))
        self.btnBuscarGenero.clicked.connect(self.callbacks.get("on_search_genre"))

        self.checkboxFolder.toggled.connect(self.callbacks.get("on_radio_button_checked"))
        self.checkboxM3u.toggled.connect(self.callbacks.get("on_radio_button_checked"))

        self.actionAgruparArtista.triggered.connect(self.callbacks.get("on_group_by_artist"))
        self.actionAgruparGenero.triggered.connect(self.callbacks.get("on_group_by_genre"))
        self.actionAgruparAlbum.triggered.connect(self.callbacks.get("on_group_by_album"))
        self.actionAgruparDecada.triggered.connect(self.callbacks.get("on_group_by_decade"))

        self.actionBuscarArtista.triggered.connect(self.callbacks.get("on_search_artist"))
        self.actionBuscarGenero.triggered.connect(self.callbacks.get("on_search_genre"))

        self.restablecer_accion.triggered.connect(self.callbacks.get("on_reset_warnings"))
        self.actionMostrarAyudaInicio.triggered.connect(self.callbacks.get("on_show_startup_help"))

        self.actionCopiar.triggered.connect(lambda: self.callbacks.get("on_change_save_preference")("copiar"))
        self.actionSymlink.triggered.connect(lambda: self.callbacks.get("on_change_save_preference")("symlink"))

        self.actionGeneral.triggered.connect(lambda: self.callbacks.get("on_change_grouping_preference")("general"))
        self.actionEspecifico.triggered.connect(
            lambda: self.callbacks.get("on_change_grouping_preference")("especifico"))

        self.actionEstiloRojo.triggered.connect(lambda: self.callbacks.get("on_change_stylesheet")("red"))
        self.actionEstiloBlanco.triggered.connect(lambda: self.callbacks.get("on_change_stylesheet")("white"))
        self.actionEstiloAzul.triggered.connect(lambda: self.callbacks.get("on_change_stylesheet")("blue"))
        self.actionEstiloVerde.triggered.connect(lambda: self.callbacks.get("on_change_stylesheet")("green"))

        # ==============================
        # APLICAR PALETA DE COLORES
        # ==============================
        MainWindow.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        MainWindow.setStyleSheet(self.layoutLoader())

        self.MainWindow = MainWindow
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(APP_NAME, APP_NAME))
        self.btnAgregarCarpeta.setText(_translate(APP_NAME, "Agregar carpeta..."))
        self.btnAgregarArchivos.setText(_translate(APP_NAME, "Agregar archivos..."))
        self.btnGuardar.setText(_translate(APP_NAME, "Guardar"))
        self.menuAgregar_carpeta.setTitle(_translate(APP_NAME, "&Archivos"))
        self.menuHerramientas.setTitle(_translate(APP_NAME, "Herramien&tas"))
        self.menuAyuda.setTitle(_translate(APP_NAME, "A&yuda"))
        self.menuOpciones.setTitle(_translate(APP_NAME, "&Opciones"))
        self.actionAgregar_carpeta.setText(_translate(APP_NAME, "Agregar carpeta..."))
        self.actionAgregar_archivos.setText(_translate(APP_NAME, "Agregar archivos..."))
        self.actionAgruparArtista.setText(_translate(APP_NAME, "Agrupar por artista"))
        self.actionAgruparGenero.setText(_translate(APP_NAME, "Agrupar por género"))
        self.actionAgruparAlbum.setText(_translate(APP_NAME, "Agrupar por álbum"))
        self.actionGuardar_2.setText(_translate(APP_NAME, "Guardar"))

    def exclude_checkboxes(self):
        if self.checkboxFolder.isChecked():
            self.checkboxM3u.setChecked(False)
        elif self.checkboxM3u.isChecked():
            self.checkboxFolder.setChecked(False)

    def layoutLoader(self):
        layout_style = self.settings.value("layout_style", "red")

        if layout_style == "white":
            self.actionEstiloBlanco.setChecked(True)

        elif layout_style == "red":
            self.actionEstiloRojo.setChecked(True)

        elif layout_style == "blue":
            self.actionEstiloAzul.setChecked(True)

        elif layout_style == "green":
            self.actionEstiloVerde.setChecked(True)

        return load_stylesheet(layout_style)
