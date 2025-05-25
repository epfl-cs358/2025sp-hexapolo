import serial
import threading

class SerialReader:
    def __init__(self, port='COM9', baudrate=115200, callback=None):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        self.read_thread = None
        self.path = "./.cmd.txt"
        self.running = False
        self.callback=callback

    def read_from_esp32(self):
        """Thread function to continuously read ESP32 responses"""
        while self.running:
            if self.ser.in_waiting > 0:
                received = self.ser.readline().decode().strip()
                if received:  # Only print non-empty lines
                    print(f"[ESP32]: {received}")
                    if self.callback:
                        self.callback(received)

    def start(self):
        """Start the reading thread"""
        self.running = True
        self.read_thread = threading.Thread(target=self.read_from_esp32, daemon=True)
        self.read_thread.start()

    def stop(self):
        """Stop the reading thread and close serial connection"""
        self.running = False
        if self.read_thread:
            self.read_thread.join()
        self.ser.close()
        print("Serial connection closed.")

    def send_message(self, message):
        """Send a message to ESP32"""
        if message:
            self.ser.write(f"{message}\n".encode())
            print(f"[Pi]: {message}")
