import serial
import threading
import time
import logging
import sys

class SerialReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, callback=None):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.read_thread = None
        self.running = False
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self._connect()

    def _connect(self):
        """Establish serial connection with retry logic"""
        while True:
            try:
                if self.ser:
                    self.ser.close()
                self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
                self.logger.info(f"Serial connection established on {self.port}")
                break
            except Exception as e:
                self.logger.error(f"Failed to connect to {self.port}: {e}")
                self.logger.info("Retrying in 5 seconds...")
                time.sleep(5)

    def read_from_esp32(self):
        """Thread function to continuously read ESP32 responses"""
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    self.logger.warning("Serial connection lost, attempting to reconnect...")
                    self._connect()
                    continue

                if self.ser.in_waiting > 0:
                    received = self.ser.readline().decode().strip()
                    if received:  # Only print non-empty lines
                        self.logger.info(f"[ESP32]: {received}")
                        if self.callback:
                            try:
                                self.callback(received)
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")
                        
            except serial.SerialException as e:
                self.logger.error(f"Serial error: {e}")
                self.logger.info("Attempting to reconnect...")
                self._connect()
            except Exception as e:
                self.logger.error(f"Unexpected error in read loop: {e}")
                time.sleep(1)
            
            time.sleep(0.01)  # Small delay to prevent busy waiting

    def start(self):
        """Start the reading thread"""
        self.running = True
        self.read_thread = threading.Thread(target=self.read_from_esp32, daemon=True)
        self.read_thread.start()
        self.logger.info("SerialReader started")

    def stop(self):
        """Stop the reading thread and close serial connection"""
        self.running = False
        if self.read_thread:
            self.read_thread.join()
        if self.ser:
            self.ser.close()
        self.logger.info("Serial connection closed.")

    def send_message(self, message):
        """Send a message to ESP32"""
        if message:
            try:
                if not self.ser or not self.ser.is_open:
                    self.logger.warning("Serial connection not available, attempting to reconnect...")
                    self._connect()
                
                self.ser.write(f"{message}\n".encode())
                self.logger.info(f"[Pi]: {message}")
            except Exception as e:
                self.logger.error(f"Failed to send message '{message}': {e}")

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/var/log/serial_reader.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the serial reader as a standalone service"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    def message_callback(message):
        """Callback function for received messages"""
        logger.info(f"Received message callback: {message}")
    
    try:
        # Create and start the serial reader
        reader = SerialReader(callback=message_callback)
        reader.start()
        
        logger.info("Serial reader service started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        if 'reader' in locals():
            reader.stop()
        logger.info("Serial reader service stopped.")

if __name__ == "__main__":
    main()
