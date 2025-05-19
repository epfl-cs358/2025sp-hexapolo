from gpiozero import Buzzer
from time import sleep
from DOA import get_doa_angle, turn_to_angle
from basic_movement import forward

bz = Buzzer(11)

if __name__ == "__main__":
    bz.on()
    bz.beep()
    sleep(0.5)
    bz.off()

    try:
        while True:
            doa = get_doa_angle()
            if doa is not None:
                turn_to_angle(doa)
                forward(5)
            sleep(0.5)
    except KeyboardInterrupt:
        print("\nProgram terminated cleanly.")
