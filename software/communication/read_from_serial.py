import serial
import threading

# Initialize serial connection
ser = serial.Serial('COM9', baudrate=115200, timeout=1)
<<<<<<< HEAD

def read_from_esp32():
    """Thread function to continuously read ESP32 responses"""
=======
received_global = ""
def read_from_esp32():
    """Thread function to continuously read ESP32 responses"""
    global received_global
>>>>>>> df2c6ec0e467f03febdf29ba2dcfd2c7b3b2f644
    while True:
        if ser.in_waiting > 0:
            received = ser.readline().decode().strip()
            if received:  # Only print non-empty lines
                print(f"[ESP32]: {received}")
<<<<<<< HEAD
=======
                received_global = received
>>>>>>> df2c6ec0e467f03febdf29ba2dcfd2c7b3b2f644

def send_to_esp32():
    """Thread function to handle user input and send messages"""
    while True:
        message = input("")
        if message.lower() == 'exit':
            break
        if message:  # Only send non-empty messages
            ser.write(f"{message}\n".encode())
            print(f"[Pi]: {message}")

# Start threads
read_thread = threading.Thread(target=read_from_esp32, daemon=True)
send_thread = threading.Thread(target=send_to_esp32)

read_thread.start()
send_thread.start()

# Wait for send thread to complete (when user types 'exit')
send_thread.join()
ser.close()
print("Serial connection closed.")