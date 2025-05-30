from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint
import webbrowser


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.background = QPixmap("resources/screens/musicarol_welcome_screen.png")
        self.resize(self.background.size())

        btn_close = QPushButton("X",self)
        btn_close.setObjectName("btn_close")
        btn_close.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_close.setFixedSize(20, 20)
        btn_close.move(550, 12)

        btn_question = QPushButton("?",self)
        btn_question.setObjectName("btn_question")
        btn_question.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_question.setFixedSize(50, 50)
        btn_question.move(80, 510)

        btn_close.clicked.connect(self.close)
        btn_question.clicked.connect(self.open_github)

        self.setStyleSheet("""
        
        QPushButton#btn_close{
            color: #5f0000;
            font-weight: bold;
            background-color: red;
            border-radius: 10px;
            border: 2px solid #5f0000;
        }
        
        QPushButton#btn_question{
            color: #5f0000;
            font-weight: bold;
            font-size: 23px;
            background-color: red;
            border-radius: 25px;
            border: 5px solid #5f0000;
        }
        
        QPushButton:hover {
            background-color: white;
            color: red;
            border: 1px solid red;
            border-radius: 3px;
        }
        
        QPushButton#btn_close:hover {
            background-color: #cc0000;
            color: lightgrey;
            border: 2px solid #5f0000;
            padding-top: 1px;
            padding-right: 1px;
        }
        
        QPushButton#btn_question:hover {
            background-color: #cc0000;
            color: lightgrey;
            border: 5px solid #5f0000;
            padding-top: 4px;
            padding-right: 2px;
        }
        
        
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.background)
    
    def open_github(self):
        webbrowser.open("https://github.com/lauragomezp/musicarol")


