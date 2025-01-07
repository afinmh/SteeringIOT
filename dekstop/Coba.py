import sys
import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
import pygame
import websocket
import json

WS_URL = "ws://192.168.1.6:8765"

pygame.init()
pygame.joystick.init()
gas_status = False
steer = ""
direction = ""
running = False
music = 3
button_pressed = False
pompa = "OFF"
strobo = "OFF"
key = ""

class ShowImage(QDialog):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi('UI/menu.ui', self)
        self.Image = None
        self.capture_image = None
        self.cap = None
        self.exit.clicked.connect(self.closetab)
        self.startt.clicked.connect(self.controller)
        self.checkstir.stateChanged.connect(self.stir)
        self.checkstik.stateChanged.connect(self.stik)
        
        global joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        joystick_name = joystick.get_name()
        print(f"Joystick terdeteksi: {joystick_name}")

        if joystick_name == "USB Joystick":
            self.checkstir.setEnabled(False) 

    def stir(self, state):
        global key
        if state == Qt.Checked:
            key = "Stir"
            self.checkstik.setEnabled(False)
            self.startt.setEnabled(True)
        else:
            self.startt.setEnabled(False)

    def stik(self, state):
        global key
        if state == Qt.Checked:
            key = "Stik"
            self.checkstir.setEnabled(False)
            self.startt.setEnabled(True)
        else:
            self.startt.setEnabled(False)

    def closetab(self):
        sys.exit()

    def controller(self):
        self.menu2_window = Menu2(self)
        self.close()
        self.menu2_window.showMaximized()


class Menu2(QDialog):
    def __init__(self, main_menu):
        super(Menu2, self).__init__()
        loadUi('UI/arah.ui', self)
        self.main_menu = main_menu
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.ws = None
        self.backk.clicked.connect(self.goBack)
        self.joystick_timer = QtCore.QTimer(self)
        self.onmodel.stateChanged.connect(self.toggleModel)
        self.draw_box = False
        self.setupWebSocket()
        self.startCamera()
        self.startJoystickControl()

    def startJoystickControl(self):
        self.joystick_timer.timeout.connect(self.controlJoystick)
        self.joystick_timer.start(50)

    def setupWebSocket(self):
        try:
            self.ws = websocket.create_connection(WS_URL)
            print("Terhubung ke WebSocket!")
            self.ws.send(json.dumps({"type": "sender"}))
        except Exception as e:
            print(f"Gagal terhubung ke WebSocket: {e}")
            self.ws = None

    def startCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)
        
    def controlJoystick(self):
        global key, gas_status, steer, direction, running, music, button_pressed, pompa, strobo, joystick, pygame
        
        pygame.event.pump()  # Memastikan pygame mendapatkan input joystick terbaru

        if key == "Stir":
            self.controlSteer()  # Jika key == Stir, jalankan kontrol stir
        elif key == "Stik":
            self.controlStik()  # Jika key == Stik, jalankan kontrol stik

    def updateFrame(self):
        global key
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qimg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)

            if self.draw_box:
                painter = QPainter(pixmap)
                pen = QPen(QColor("red"))
                pen.setWidth(3)
                painter.setPen(pen)
                box_width, box_height = 100, 100
                x = (pixmap.width() - box_width) // 2
                y = (pixmap.height() - box_height) // 2
                painter.drawRect(x, y, box_width, box_height)
                painter.end()

            self.label.setPixmap(pixmap)

    def controlStik(self):
        global gas_status, steer, direction, running, music, button_pressed, pompa, strobo, joystick, pygame
        
        while True:
            pygame.event.pump()
            if joystick.get_button(9):  # Start
                if not running:
                    running = True
                    print("Kontrol dimulai!")

            if joystick.get_button(8):  # Select
                print("Menghentikan kontrol...")
                gas_status = False
                steer = ""
                direction = ""
                self.ws.send(json.dumps({"topic": "gas", "value": "stop"}))
                self.ws.send(json.dumps({"topic": "direction", "value": ""}))
                self.ws.send(json.dumps({"topic": "steer", "value": ""}))
                print("Nilai reset dan program dihentikan.")
                running = False

            if running:
                if joystick.get_button(5):  # R1
                    if direction != "maju":
                        direction = "maju"
                        self.ws.send(json.dumps({"topic": "direction", "value": "maju"}))
                        print("Motor maju")
                elif joystick.get_button(4):  # L1
                    if direction != "mundur":
                        direction = "mundur"
                        self.ws.send(json.dumps({"topic": "direction", "value": "mundur"}))
                        print("Motor mundur")

                steer_axis = joystick.get_axis(0)
                if steer_axis > 0.5:
                    if steer != "kanan":
                        steer = "kanan"
                        self.ws.send(json.dumps({"topic": "steer", "value": "kanan"}))
                        print("Belok Kanan")
                elif steer_axis < -0.5:
                    if steer != "kiri":
                        steer = "kiri"
                        self.ws.send(json.dumps({"topic": "steer", "value": "kiri"}))
                        print("Belok Kiri")
                else:
                    if steer != "netral":
                        steer = "netral"
                        self.ws.send(json.dumps({"topic": "steer", "value": "netral"}))
                        print("Netral")
                        
                pedal_axis = joystick.get_axis(1)  # Joysstick bagian Kiri (Atas Bawah)
                if pedal_axis < -0.5:  # Joystick ke atas
                    if not gas_status:
                        gas_status = True
                        self.ws.send(json.dumps({"topic": "gas", "value": "start"}))
                        print("Gas dinyalakan!")
                else:
                    if gas_status:
                        gas_status = False
                        self.ws.send(json.dumps({"topic": "gas", "value": "stop"}))
                        print("Gas dimatikan!")
                        
                if joystick.get_button(1):  # Lingkaran (2)
                    if not button_pressed: 
                        self.ws.send(json.dumps({"topic": "sound", "value": str(music)}))
                        print(f"Telolet {music}")   
                    button_pressed = True

                if joystick.get_button(7):  # L2 Next lagu
                    if not button_pressed:
                        if music < 7:
                            music += 1
                            print(f"Music {music}")
                        button_pressed = True

                if joystick.get_button(6):  # R2 Prev lagu
                    if not button_pressed:
                        if music > 3:
                            music -= 1
                            print(f"Music {music}")
                        button_pressed = True
                        
                if joystick.get_button(3): #Kotak
                    if not button_pressed: 
                        self.ws.send(json.dumps({"topic": "sound", "value": "Stop"}))
                        print("Stop")
                    button_pressed = True
                    
                if joystick.get_button(0): #Segitiga
                    if not button_pressed: 
                        if strobo == "OFF":
                            self.ws.send(json.dumps({"topic": "strobo", "value": "ON"}))
                            strobo = "ON"
                            print("Strobo ON")
                        elif strobo == "ON":
                            self.ws.send(json.dumps({"topic": "strobo", "value": "OFF"}))
                            strobo = "OFF"
                            print("Strobo OFF")
                    button_pressed = True
                    
                if joystick.get_button(2): # Silang
                    if not button_pressed: 
                        if pompa == "OFF":
                            self.ws.send(json.dumps({"topic": "pompa", "value": "ON"}))
                            print("Pompa ON")
                            pompa = "ON"
                        elif pompa == "ON":
                            self.ws.send(json.dumps({"topic": "pompa", "value": "OFF"}))
                            print("Pompa OFF")
                            pompa = "OFF"
                    button_pressed = True
                    
                if not joystick.get_button(6) and not joystick.get_button(7) and not joystick.get_button(1)  and not joystick.get_button(3)  and not joystick.get_button(0) and not joystick.get_button(2):
                    button_pressed = False

    def controlStir(self):
        global gas_status, steer, direction, running, music, button_pressed, pompa, strobo, joystick, pygame
        
        while True:
            pygame.event.pump()
            if joystick.get_button(9):  # Start
                if not running:
                    running = True
                    print("Kontrol dimulai!")

            if joystick.get_button(8):  # Select
                print("Menghentikan kontrol...")
                gas_status = False
                steer = ""
                direction = ""
                self.ws.send(json.dumps({"topic": "gas", "value": "stop"}))
                self.ws.send(json.dumps({"topic": "direction", "value": ""}))
                self.ws.send(json.dumps({"topic": "steer", "value": ""}))
                print("Nilai reset dan program dihentikan.")
                running = False

            if running:
                if joystick.get_button(5):  # R1
                    if direction != "maju":
                        direction = "maju"
                        self.ws.send(json.dumps({"topic": "direction", "value": "maju"}))
                        print("Motor maju")
                elif joystick.get_button(4):  # L1
                    if direction != "mundur":
                        direction = "mundur"
                        self.ws.send(json.dumps({"topic": "direction", "value": "mundur"}))
                        print("Motor mundur")

                steer_axis = joystick.get_axis(0)
                if steer_axis > 0.5:
                    if steer != "kanan":
                        steer = "kanan"
                        self.ws.send(json.dumps({"topic": "steer", "value": "kanan"}))
                        print("Belok Kanan")
                elif steer_axis < -0.5:
                    if steer != "kiri":
                        steer = "kiri"
                        self.ws.send(json.dumps({"topic": "steer", "value": "kiri"}))
                        print("Belok Kiri")
                else:
                    if steer != "netral":
                        steer = "netral"
                        self.ws.send(json.dumps({"topic": "steer", "value": "netral"}))
                        print("Netral")
                        
                pedal_axis = joystick.get_axis(1)  # Joysstick bagian Kiri (Atas Bawah)
                if pedal_axis < -0.5:  # Joystick ke atas
                    if not gas_status:
                        gas_status = True
                        self.ws.send(json.dumps({"topic": "gas", "value": "start"}))
                        print("Gas dinyalakan!")
                else:
                    if gas_status:
                        gas_status = False
                        self.ws.send(json.dumps({"topic": "gas", "value": "stop"}))
                        print("Gas dimatikan!")
                        
                if joystick.get_button(1):  # Lingkaran (2)
                    if not button_pressed: 
                        self.ws.send(json.dumps({"topic": "sound", "value": str(music)}))
                        print(f"Telolet {music}")   
                    button_pressed = True

                if joystick.get_button(7):  # L2 Next lagu
                    if not button_pressed:
                        if music < 7:
                            music += 1
                            print(f"Music {music}")
                        button_pressed = True

                if joystick.get_button(6):  # R2 Prev lagu
                    if not button_pressed:
                        if music > 3:
                            music -= 1
                            print(f"Music {music}")
                        button_pressed = True
                        
                if joystick.get_button(3): #Kotak
                    if not button_pressed: 
                        self.ws.send(json.dumps({"topic": "sound", "value": "Stop"}))
                        print("Stop")
                    button_pressed = True
                    
                if joystick.get_button(0): #Segitiga
                    if not button_pressed: 
                        if strobo == "OFF":
                            self.ws.send(json.dumps({"topic": "strobo", "value": "ON"}))
                            strobo = "ON"
                            print("Strobo ON")
                        elif strobo == "ON":
                            self.ws.send(json.dumps({"topic": "strobo", "value": "OFF"}))
                            strobo = "OFF"
                            print("Strobo OFF")
                    button_pressed = True
                    
                if joystick.get_button(2): # Silang
                    if not button_pressed: 
                        if pompa == "OFF":
                            self.ws.send(json.dumps({"topic": "pompa", "value": "ON"}))
                            print("Pompa ON")
                            pompa = "ON"
                        elif pompa == "ON":
                            self.ws.send(json.dumps({"topic": "pompa", "value": "OFF"}))
                            print("Pompa OFF")
                            pompa = "OFF"
                    button_pressed = True
                    
                if not joystick.get_button(6) and not joystick.get_button(7) and not joystick.get_button(1)  and not joystick.get_button(3)  and not joystick.get_button(0) and not joystick.get_button(2):
                    button_pressed = False

    def toggleModel(self, state):
        self.draw_box = state == Qt.Checked

    def goBack(self):
        self.timer.stop()
        self.cap.release()
        if self.ws:
            self.ws.close()
        self.close()
        self.main_menu.show()

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.ws:
            self.ws.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle('PADAMIN')
    window.showMaximized()
    sys.exit(app.exec_())
