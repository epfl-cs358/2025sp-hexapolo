from basic_movement import turn
from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep

current_angle = 0  # Tracks motor’s current angle position
SPR = 200 # Steps per full rotation

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
                print(f"Voice detected at {angle}°")
                return angle 
            sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return None


def turn_to_angle(target_angle):
    global current_angle
    delta = (target_angle - current_angle) % 360
    if delta > 180:
        delta -= 360  # Choose shortest path

    direction = delta > 0
    # steps = int(abs(delta) / 360 * SPR)

    print(f"Turning {'CW' if direction else 'CCW'} by {abs(delta)}°")

    turn(angle=delta)
    current_angle = target_angle
