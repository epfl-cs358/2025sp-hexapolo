from gpiozero import Buzzer
from time import sleep
from DOA import get_doa_angle
from basic_movement import forward, turn

bz = Buzzer(11)

def main_control_loop():
    bz.on()
    bz.beep()
    sleep(0.5)
    bz.off()

    try:
        while True:
            doa = get_doa_angle()
            if doa == -1:
                break
            elif doa is not None:
                turn(doa)
                forward(5)
    except KeyboardInterrupt:
        print("\nProgram terminated cleanly.")

if __name__ == "__main__":
    main_control_loop()
