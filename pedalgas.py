import pygame

# Inisialisasi pygame
pygame.init()

# Inisialisasi joystick
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()

if joystick_count == 0:
    print("Tidak ada perangkat joystick/pedal yang terdeteksi.")
    exit()

# Pilih joystick pertama
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick terdeteksi: {joystick.get_name()}")


while True:
    pygame.event.pump()  # Proses semua event

    # Cek jumlah axis yang tersedia
    axis_count = joystick.get_numaxes()
    for i in range(axis_count):
        axis_value = joystick.get_axis(i)  # Membaca nilai sumbu
        print(f"Axis {i} Value: {axis_value:.2f}")

    pygame.time.wait(100)
