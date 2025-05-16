from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util
from time import sleep
from gpiozero import Buzzer, Motor

motor = Motor(forward=23, backward=24)
current_angle = 0  # Tracks motor’s current angle position
SPR = 200 # Steps per full rotation

# Set direction to true to turn right
def turn_motor(direction):
    if direction:
        motor.forward()
    else:
        motor.backward()
    sleep(0.1)
    motor.stop()
    sleep(0.05)

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
    steps = int(abs(delta) / 360 * SPR)

    print(f"Turning {'CW' if direction else 'CCW'} by {abs(delta)}° ({steps} steps)")

    for _ in range(steps):
        turn_motor(direction)

    current_angle = target_angle


if __name__ == "__main__":
    bz = Buzzer(25)
    bz.on()
    bz.beep()
    bz.off()

    try:
        while True:
            doa = get_doa_angle()
            if doa is not None:
                turn_to_angle(doa)
            sleep(0.5)
    except KeyboardInterrupt:
        print("\nProgram terminated cleanly.")
