from time import sleep
from DOA import get_doa_angle
from basic_movement import forward, turn
from read_from_serial import SerialReader

def handle_command(command):
    """Handle incoming commands from ESP32"""
    try:
        cmd = command.split()
        if len(cmd) >= 2:
            direction = cmd[0]
            angle = float(cmd[1])  # Convert angle to float
            if direction == 'right':
                angle *= -1
            turn(angle)
    except Exception as e:
        print(f"Error processing command: {e}")

def follow():
    serial_reader = SerialReader(port='/dev/ttyUSB0', callback=handle_command)
    serial_reader.start()

    try:
        while True:
            sleep(5)
    except KeyboardInterrupt:
        print("\nProgram terminated cleanly.")
    finally:
        serial_reader.stop()

def main_control_loop():

    try:
        while True:
            doa = get_doa_angle()
            if doa == -1:
                break
            elif doa is not None:
                turn(doa)
                sleep(0.5)
                follow()
    except KeyboardInterrupt:
        print("\nProgram terminated cleanly.")

if __name__ == "__main__":
    main_control_loop()
