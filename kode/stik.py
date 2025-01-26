import pygame
import time
import websocket
import json


WS_URL = "ws://127.0.0.1:8765"


pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Tidak ada joystick yang terdeteksi!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick terdeteksi: {joystick.get_name()}")

try:
    ws = websocket.create_connection(WS_URL)
    print("Terhubung ke WebSocket!")
    ws.send(json.dumps({"type": "sender"}))
except Exception as e:
    print(f"Gagal terhubung ke WebSocket: {e}")
    exit()

def control_motor():
    gas_status = False
    steer = ""
    direction = ""
    running = False 
    music = 3
    button_pressed = False
    pompa = "OFF"
    strobo = "OFF"

    while True:
        pygame.event.pump()

        if joystick.get_button(9): #Start
            if not running:
                running = True
                print("Kontrol dimulai!")

        if joystick.get_button(8): #Select
            print("Menghentikan kontrol...")
            gas_status = False
            steer = ""
            direction = ""
            ws.send(json.dumps({"topic": "gas", "value": "stop"}))
            ws.send(json.dumps({"topic": "direction", "value": ""}))
            ws.send(json.dumps({"topic": "steer", "value": ""}))
            print("Nilai reset dan program dihentikan.")
            running = False

        if running:
            if joystick.get_button(5):  # R1
                if direction != "maju":
                    direction = "maju"
                    ws.send(json.dumps({"topic": "direction", "value": "maju"}))
                    print("Motor maju")
            elif joystick.get_button(4):  # L1
                if direction != "mundur":
                    direction = "mundur"
                    ws.send(json.dumps({"topic": "direction", "value": "mundur"}))
                    print("Motor mundur")

            steer_axis = joystick.get_axis(0)  # Joystick Bagian Kiri (Kiri Kanan)
            if steer_axis > 0.5:  # Joystick ke kanan
                if steer != "kanan":
                    steer = "kanan"
                    ws.send(json.dumps({"topic": "steer", "value": "kanan"}))
                    print("Belok Kanan")
            elif steer_axis < -0.5:  # Joystick ke kiri
                if steer != "kiri":
                    steer = "kiri"
                    ws.send(json.dumps({"topic": "steer", "value": "kiri"}))
                    print("Belok Kiri")
            else:  # Joystick di tengah atau netral
                if steer != "netral":
                    steer = "netral"
                    ws.send(json.dumps({"topic": "steer", "value": "netral"}))
                    print("Netral")

            pedal_axis = joystick.get_axis(1)  # Joysstick bagian Kiri (Atas Bawah)
            if pedal_axis < -0.5:  # Joystick ke atas
                if not gas_status:
                    gas_status = True
                    ws.send(json.dumps({"topic": "gas", "value": "start"}))
                    print("Gas dinyalakan!")
            else:
                if gas_status:
                    gas_status = False
                    ws.send(json.dumps({"topic": "gas", "value": "stop"}))
                    print("Gas dimatikan!")
                    
            if joystick.get_button(1):  # Lingkaran (2)
                if not button_pressed: 
                    ws.send(json.dumps({"topic": "sound", "value": str(music)}))
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
                    ws.send(json.dumps({"topic": "sound", "value": "Stop"}))
                    print("Stop")
                button_pressed = True
                
            if joystick.get_button(0): #Segitiga
                if not button_pressed: 
                    if strobo == "OFF":
                        ws.send(json.dumps({"topic": "strobo", "value": "ON"}))
                        strobo = "ON"
                        print("Strobo ON")
                    elif strobo == "ON":
                        ws.send(json.dumps({"topic": "strobo", "value": "OFF"}))
                        strobo = "OFF"
                        print("Strobo OFF")
                button_pressed = True
                
            if joystick.get_button(2): # Silang
                if not button_pressed: 
                    if pompa == "OFF":
                        ws.send(json.dumps({"topic": "pompa", "value": "ON"}))
                        print("Pompa ON")
                        pompa = "ON"
                    elif pompa == "ON":
                        ws.send(json.dumps({"topic": "pompa", "value": "OFF"}))
                        print("Pompa OFF")
                        pompa = "OFF"
                button_pressed = True
                
            if not joystick.get_button(6) and not joystick.get_button(7) and not joystick.get_button(1)  and not joystick.get_button(3)  and not joystick.get_button(0) and not joystick.get_button(2):
                button_pressed = False

try:
    control_motor()
except KeyboardInterrupt:
    print("\nKontrol dihentikan.")
finally:
    pygame.quit()
    ws.close()
