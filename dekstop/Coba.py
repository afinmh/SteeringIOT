import sys
import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

class ShowImage(QDialog):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi('menu.ui', self)
        self.Image = None
        self.capture_image = None
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.exit.clicked.connect(self.closetab)
        self.startt.clicked.connect(self.controller)
        
    def closetab(self):
        sys.exit(app.exec_())
        
    def controller(self):
        self.menu2_window = QDialog()  # Membuat instance QDialog
        loadUi('setir.ui', self.menu2_window)  # Memuat file menu2.ui
        self.menu2_window.setWindowFlags(Qt.FramelessWindowHint)
        self.menu2_window.showMaximized()  # Membuka dalam mode maximized
        self.menu2_window.setWindowTitle('Menu 2')  # (Opsional) Mengatur judul
        self.menu2_window.exec_()  # Menampilkan jendela dialog secara modal

app = QtWidgets.QApplication(sys.argv)
window = ShowImage()
sys.exit(app.exec_())
