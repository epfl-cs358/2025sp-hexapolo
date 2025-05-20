from basic_movement import turn
from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep

def get_doa_angle():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        print("Mic Array not found.")
        return None

    Mic_tuning = Tuning(dev)
    print("Waiting for voice...")

    try:
        while True:
            if Mic_tuning.is_voice():
                angle = Mic_tuning.direction
                angle = (angle + 90) % 360
                print(f"Voice detected at {angle}°")
                return angle 
            sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return -1
