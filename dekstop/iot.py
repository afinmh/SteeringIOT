import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDialog,
    QLabel,
    QProgressBar,
    QLCDNumber,
)
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class MainMenu(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Main Menu")
        self.setGeometry(200, 200, 400, 300)

        # Path gambar latar belakang
        background_image_path = os.path.join(os.getcwd(), "mobil.jpg")

        # Path gambar ikon
        start_icon_path = os.path.join(os.getcwd(), "start.png")
        exit_icon_path = os.path.join(os.getcwd(), "exit.png")

        # Menambahkan latar belakang
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-image: url({background_image_path});
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }}
        """
        )

        # Tombol START
        self.start_button = QPushButton(self)
        self.start_button.setGeometry(100, 100, 100, 50)
        self.start_button.setText("")  # Menghapus teks tombol
        self.start_button.setIcon(QIcon(start_icon_path))
        self.start_button.setIconSize(self.start_button.size())  # Sesuaikan ukuran ikon
        self.start_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan
        self.start_button.clicked.connect(self.open_menu2)

        # Tombol EXIT
        self.exit_button = QPushButton(self)
        self.exit_button.setGeometry(100, 200, 100, 50)
        self.exit_button.setText("")  # Menghapus teks tombol
        self.exit_button.setIcon(
            QIcon(exit_icon_path)
        )  # Masukkan gambar untuk tombol EXIT
        self.exit_button.setIconSize(self.exit_button.size())  # Sesuaikan ukuran ikon
        self.exit_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan
        self.exit_button.clicked.connect(self.close)

    def open_menu2(self):
        self.dialog = Menu2(self.app)
        self.dialog.exec_()


class Menu2(QDialog):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Select Control")
        self.setGeometry(200, 200, 400, 200)

        # Path gambar latar belakang
        background_image_path = os.path.join(os.getcwd(), "mobil.jpg")

        # Path gambar ikon
        joystick_icon_path = os.path.join(os.getcwd(), "panah.png")
        steering_icon_path = os.path.join(os.getcwd(), "setir.png")

        # Menambahkan latar belakang
        self.setStyleSheet(
            f"""
            QDialog {{
                background-image: url({background_image_path});
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }}
        """
        )

        # Tombol untuk joystick
        self.joystick_button = QPushButton(self)
        self.joystick_button.setGeometry(50, 50, 100, 50)
        self.joystick_button.setIcon(
            QIcon(joystick_icon_path)
        )  # Menambahkan ikon joystick
        self.joystick_button.setIconSize(
            self.joystick_button.size()
        )  # Sesuaikan ukuran ikon
        self.joystick_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan
        self.joystick_button.clicked.connect(lambda: self.select_control("Panah"))

        # Tombol untuk setir
        self.steering_button = QPushButton(self)
        self.steering_button.setGeometry(200, 50, 100, 50)
        self.steering_button.setIcon(
            QIcon(steering_icon_path)
        )  # Menambahkan ikon setir
        self.steering_button.setIconSize(
            self.steering_button.size()
        )  # Sesuaikan ukuran ikon
        self.steering_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan
        self.steering_button.clicked.connect(lambda: self.select_control("steering"))

    def select_control(self, control_type):
        self.close()
        self.app.open_control_app(control_type)


class MainApp(QMainWindow):
    def __init__(self, control_type, menu2):
        super().__init__()
        self.menu2 = menu2  # Menyimpan referensi ke Menu2
        self.setWindowTitle(f"{control_type.capitalize()} Control")
        self.setGeometry(200, 200, 935, 521)  # Sesuaikan dimensi jendela

        # Tambahkan label untuk menampilkan kamera
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(50, 50, 640, 360)  # Dimensi area kamera
        self.camera_label.setStyleSheet("border: 1px solid black;")

        self.timer = QTimer(self)  # Timer untuk frame update
        self.timer.timeout.connect(self.update_frame)

        # Inisialisasi kamera
        self.cap = cv2.VideoCapture(0)  # Buka kamera default

        self.btn_kembali = QPushButton(
            "Kembali", self
        )  # Tambahkan teks "Kembali" ke tombol
        self.btn_kembali.setGeometry(
            840, 10, 80, 40
        )  # Posisi di sudut kiri atas dengan ukuran
        self.btn_kembali.setStyleSheet(
            "background-color: lightgray; border: 1px solid black; border-radius: 5px;"
        )  # Gaya sederhana untuk tombol
        self.btn_kembali.clicked.connect(self.kembali_ke_menu)

        # Tombol kiri
        self.btn_kiri = QPushButton(self)
        self.btn_kiri.setGeometry(50, 400, 50, 50)
        self.btn_kiri.setIcon(QIcon("kiri.png"))  # Tambahkan ikon untuk tombol kiri
        self.btn_kiri.setIconSize(self.btn_kiri.size())  # Sesuaikan ukuran ikon
        self.btn_kiri.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan

        # Tombol kanan
        self.btn_kanan = QPushButton(self)
        self.btn_kanan.setGeometry(150, 400, 50, 50)
        self.btn_kanan.setIcon(QIcon("kanan.png"))  # Tambahkan ikon untuk tombol kanan
        self.btn_kanan.setIconSize(self.btn_kanan.size())  # Sesuaikan ukuran ikon
        self.btn_kanan.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan

        # Tombol tambahan (rem)
        self.btn_rem2 = QPushButton(self)
        self.btn_rem2.setGeometry(800, 402, 50, 50)
        self.btn_rem2.setIcon(QIcon("rem.png"))  # Tambahkan ikon untuk tombol rem
        self.btn_rem2.setIconSize(self.btn_rem2.size())  # Sesuaikan ukuran ikon
        self.btn_rem2.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan

        # Tombol gas
        self.btn_gas = QPushButton(self)
        self.btn_gas.setGeometry(850, 400, 50, 50)  # Pindahkan ke sebelah tombol rem
        self.btn_gas.setIcon(QIcon("gas.png"))  # Tambahkan ikon untuk tombol gas
        self.btn_gas.setIconSize(self.btn_gas.size())  # Sesuaikan ukuran ikon
        self.btn_gas.setStyleSheet(
            "background-color: transparent; border: none;"
        )  # Transparan

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(350, 435, 300, 20)
        self.progressBar.setValue(24)  # Set nilai awal sesuai dengan gambar

        # LCD number
        self.lcdNumber = QLCDNumber(self)
        self.lcdNumber.setGeometry(450, 370, 100, 50)
        self.lcdNumber.display(0)  # Nilai awal LCD

        # Label kontrol jenis
        self.label_kontrol = QLabel(f"Kontrol: {control_type}", self)
        self.label_kontrol.setGeometry(50, 10, 200, 30)

        # Mulai timer untuk update kamera
        self.timer.start(30)  # Update setiap 30ms

    def kembali_ke_menu(self):
        """Fungsi untuk kembali ke menu utama (Menu2)."""
        self.timer.stop()  # Berhenti mengupdate kamera
        self.cap.release()  # Lepas kamera
        self.close()  # Menutup jendela saat ini
        self.menu2.show()  # Membuka kembali Menu2

    def update_frame(self):
        """Fungsi untuk mengupdate frame kamera."""
        ret, frame = self.cap.read()
        if ret:
            # Konversi frame ke RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Buat QImage dari frame
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            # Tampilkan di label
            self.camera_label.setPixmap(QPixmap.fromImage(qimg))



class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.main_menu = MainMenu(self)
        self.main_menu.show()

    def open_control_app(self, control_type):
        self.main_menu.hide()
        self.menu2 = Menu2(self)  # Membuat instance dari Menu2
        self.menu2.show()
        self.main_app = MainApp(control_type, self.menu2)  # Passing menu2 ke MainApp
        self.main_app.show()


if __name__ == "__main__":
    app = Application([])
    app.exec_()
