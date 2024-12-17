import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QLabel
from PyQt5.QtGui import QIcon


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(200, 200, 400, 300)

        # Path gambar
        start_icon_path = os.path.join(
            os.getcwd(), "start.png"
        )  # Ubah path sesuai lokasi file
        exit_icon_path = os.path.join(
            os.getcwd(), "exit.png"
        )  # Ubah path sesuai lokasi file

        # Tombol START
        self.start_button = QPushButton(self)
        self.start_button.setGeometry(100, 100, 100, 50)
        self.start_button.setText("START")
        self.start_button.setIcon(
            QIcon(start_icon_path)
        )  # Masukkan gambar untuk tombol START
        self.start_button.setIconSize(self.start_button.size())  # Sesuaikan ukuran ikon
        self.start_button.clicked.connect(self.open_menu2)

        # Tombol EXIT
        self.exit_button = QPushButton(self)
        self.exit_button.setGeometry(100, 200, 100, 50)
        self.exit_button.setText("EXIT")
        self.exit_button.setIcon(
            QIcon(exit_icon_path)
        )  # Masukkan gambar untuk tombol EXIT
        self.exit_button.setIconSize(self.exit_button.size())
        self.exit_button.clicked.connect(self.close)

    def open_menu2(self):
        self.dialog = Menu2(self)
        self.dialog.exec_()


class Menu2(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Select Control")
        self.setGeometry(200, 200, 400, 200)

        # Tombol untuk joystick
        self.joystick_button = QPushButton("Joystick", self)
        self.joystick_button.setGeometry(50, 50, 100, 50)
        self.joystick_button.clicked.connect(self.select_joystick)

        # Tombol untuk setir
        self.steering_button = QPushButton("Setir", self)
        self.steering_button.setGeometry(200, 50, 100, 50)
        self.steering_button.clicked.connect(self.select_steering)

    def select_joystick(self):
        self.open_app("joystick")

    def select_steering(self):
        self.open_app("steering")

    def open_app(self, control_type):
        self.close()
        self.parent().open_control_app(control_type)


class MainApp(QMainWindow):
    def __init__(self, control_type):
        super().__init__()
        self.setWindowTitle("Control App")
        self.setGeometry(200, 200, 400, 200)

        # Tampilkan jenis kontrol yang dipilih
        self.label = QLabel(f"Kontrol: {control_type}", self)
        self.label.setGeometry(50, 50, 200, 50)


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.main_menu = MainMenu()
        self.main_menu.show()

    def open_control_app(self, control_type):
        self.main_menu.hide()
        self.main_app = MainApp(control_type)
        self.main_app.show()


if __name__ == "__main__":
    app = Application([])
    app.exec_()
