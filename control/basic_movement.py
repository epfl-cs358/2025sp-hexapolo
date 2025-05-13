from gpiozero import Motor, PWMOutputDevice
from time import sleep


walk_motor = Motor(forward=23, backward=24)
turn_motor = Motor(forward=17, backward=18)

def main():
    while True:
        # Walk forward for 3 seconds
        walk_motor.forward()
        sleep(3)
        walk_motor.stop()

        # Turn 90 degrees (adjust sleep time for precise turning)
        turn_motor.forward()
        sleep(1)  # Adjust this value based on the robot's turning speed
        turn_motor.stop()
