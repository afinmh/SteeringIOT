import pygame

# Inisialisasi pygame
pygame.init()

# Inisialisasi joystick
pygame.joystick.init()

# Cek apakah ada joystick yang terhubung
if pygame.joystick.get_count() == 0:
    print("Tidak ada perangkat joystick yang terdeteksi!")
    pygame.quit()
    exit()

# Pilih joystick pertama
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick terdeteksi: {joystick.get_name()}")
print(f"Jumlah axis: {joystick.get_numaxes()}")

try:
    while True:
        # Perbarui event pygame
        pygame.event.pump()

        # Membaca nilai dari axis 1
        axis_value = joystick.get_axis(1)  # Axis 1 biasanya vertikal (Y)
        
        # Menampilkan nilai axis
        print(f"Axis 1 value: {axis_value:.2f}")
        
        # Tunggu sebentar untuk mengurangi beban CPU
        pygame.time.wait(100)

except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    pygame.quit()
