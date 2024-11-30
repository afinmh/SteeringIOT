import sys
sys.path.append('../logidrivepy')
from logidrivepy import LogitechController
import time

def spin_controller(controller, repetitions=3):
    for _ in range(repetitions):
        # Gerakkan setir ke kiri
        for i in range(-90, 90, 10):  # Dari -100 ke 0 dengan langkah 10
            controller.LogiPlaySpringForce(0, i, 100, 40)
            controller.logi_update()
            time.sleep(0.05)
        
        time.sleep(0.2)  # Tunggu sejenak sebelum iterasi berikutnya

def spin_test():
    controller = LogitechController()

    controller.steering_initialize()
    print("\n---Logitech Spin Test---")
    spin_controller(controller, repetitions=10)  # Lakukan 3 kali
    print("Spin test passed.\n")

    controller.steering_shutdown()

if __name__ == "__main__":
    spin_test()
