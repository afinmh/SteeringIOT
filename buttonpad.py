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
print(f"Jumlah tombol: {joystick.get_numbuttons()}")

try:
    while True:
        # Perbarui event pygame
        pygame.event.pump()

        # Loop untuk membaca status semua tombol
        for i in range(joystick.get_numbuttons()):
            button_status = joystick.get_button(i)  # Membaca status tombol
            if button_status:  # Jika tombol ditekan
                print(f"Tombol {i} ditekan!")

        # Tunggu sebentar untuk mengurangi beban CPU
        pygame.time.wait(100)

except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    pygame.quit()
