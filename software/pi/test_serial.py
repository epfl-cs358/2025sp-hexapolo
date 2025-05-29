#!/usr/bin/env python3

import serial
import time
import sys

def test_serial_connection(port='/dev/ttyUSB0', baudrate=115200):
    """Test the serial connection to ESP32"""
    print(f"Testing serial connection on {port} at {baudrate} baud...")
    
    try:
        # Open serial connection
        ser = serial.Serial(port, baudrate=baudrate, timeout=2)
        print(f"✓ Serial port {port} opened successfully")
        
        # Wait a moment for connection to stabilize
        time.sleep(1)
        
        # Send test message
        test_message = "test connection"
        print(f"Sending test message: '{test_message}'")
        ser.write(f"{test_message}\n".encode())
        
        # Try to read any response
        print("Listening for responses (10 seconds)...")
        start_time = time.time()
        response_count = 0
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response:
                    print(f"Received: '{response}'")
                    response_count += 1
            time.sleep(0.1)
        
        print(f"✓ Test completed. Received {response_count} responses.")
        
        # Send a few more test commands
        test_commands = ["left 45", "right 30", "stop"]
        for cmd in test_commands:
            print(f"Sending: '{cmd}'")
            ser.write(f"{cmd}\n".encode())
            time.sleep(0.5)
        
        ser.close()
        print("✓ Serial connection test completed successfully")
        return True
        
    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        print("Check:")
        print("  - ESP32 is connected and powered")
        print("  - FTDI cable is properly connected")
        print("  - Correct port specified")
        print("  - User has permission to access serial port")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def list_serial_ports():
    """List available serial ports"""
    import glob
    ports = glob.glob('/dev/tty[AU]*')
    print("Available serial ports:")
    if ports:
        for port in ports:
            print(f"  {port}")
    else:
        print("  No serial ports found")
    return ports

if __name__ == "__main__":
    print("ESP32-Pi Serial Connection Test")
    print("=" * 40)
    
    # List available ports
    list_serial_ports()
    print()
    
    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    # Test the connection
    success = test_serial_connection(port)
    
    if success:
        print("\n✓ Serial communication appears to be working!")
        print("You can now run the main serial reader service.")
    else:
        print("\n✗ Serial communication test failed.")
        print("Please check your connections and try again.")
    
    sys.exit(0 if success else 1)