import pygame

# Inisialisasi pygame dan joystick
pygame.init()
pygame.joystick.init()

# Cek apakah joystick terhubung
if pygame.joystick.get_count() == 0:
    print("Tidak ada joystick yang terhubung!")
    exit()

# Ambil joystick pertama
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick terhubung: {joystick.get_name()}")
print(f"Jumlah tombol: {joystick.get_numbuttons()}")
print(f"Jumlah axis: {joystick.get_numaxes()}")
print(f"Jumlah hat: {joystick.get_numhats()}")

# Loop utama
try:
    while True:
        pygame.event.pump()  # Perbarui event
        print("\n--- Input Joystick ---")

        # Cek semua tombol
        for i in range(joystick.get_numbuttons()):
            if joystick.get_button(i):
                print(f"Tombol {i} ditekan")

        # Cek semua axis (analog stick)
        for i in range(joystick.get_numaxes()):
            axis_value = joystick.get_axis(i)
            if abs(axis_value) > 0.1:  # Threshold untuk memfilter noise
                print(f"Axis {i}: {axis_value:.2f}")

        # Cek semua hat (D-pad)
        for i in range(joystick.get_numhats()):
            hat_value = joystick.get_hat(i)
            if hat_value != (0, 0):  # Jika ada input pada D-pad
                print(f"Hat {i}: {hat_value}")

        pygame.time.wait(100)  # Tunggu 100ms sebelum iterasi berikutnya
except KeyboardInterrupt:
    print("\nKeluar...")
