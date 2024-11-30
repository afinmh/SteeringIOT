import pygame
import requests
import time

# Konfigurasi IP ESP32
ESP32_IP = "http://192.168.1.130"  # Ganti dengan IP ESP32 Anda

# Inisialisasi joystick
pygame.init()
pygame.joystick.init()

# Pastikan joystick terhubung
if pygame.joystick.get_count() == 0:
    print("Joystick tidak ditemukan!")
    exit()

# Ambil joystick pertama
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick terhubung: {joystick.get_name()}")

# Variabel untuk melacak status tombol
gas_pressed = False

def send_request(endpoint):
    try:
        response = requests.get(f"{ESP32_IP}/{endpoint}")
        print(f"Request ke {endpoint}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Gagal mengirim request: {e}")

# Loop utama
try:
    while True:
        pygame.event.pump()  # Perbarui event joystick

        # Tombol X (Gas) sebagai push button
        if joystick.get_button(0) and not gas_pressed:  # Tombol 0 ditekan
            print("Tombol X ditekan - Gas!")
            send_request("gas?value=start")
            gas_pressed = True  # Tandai bahwa tombol sudah ditekan

        elif not joystick.get_button(0) and gas_pressed:  # Tombol 0 dilepas
            print("Tombol X dilepas - Stop Gas!")
            send_request("gas?value=stop")
            gas_pressed = False  # Reset status tombol

        # Mengatur arah motor berdasarkan tombol joystick
        if joystick.get_axis(0) < -0.5:  # Arah kiri (Maju)
            print("Joystick kiri - Maju")
            send_request("direction?value=maju")
        elif joystick.get_axis(0) > 0.5:  # Arah kanan (Mundur)
            print("Joystick kanan - Mundur")
            send_request("direction?value=mundur")

        time.sleep(0.1)  # Debounce delay
except KeyboardInterrupt:
    print("\nKeluar...")
