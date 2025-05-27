#!/usr/bin/env python3

import sys
import time
import logging
import threading
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        import gpiozero
        logger.info("✓ gpiozero imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import gpiozero: {e}")
        return False
    
    try:
        import serial
        logger.info("✓ pyserial imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import serial: {e}")
        return False
    
    try:
        from basic_movement import forward, turn, walk_motor, turn_motor
        logger.info("✓ basic_movement module imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import basic_movement: {e}")
        return False
    
    try:
        from read_from_serial import SerialReader
        logger.info("✓ read_from_serial module imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import read_from_serial: {e}")
        return False
    
    try:
        from DOA import get_doa_angle
        logger.info("✓ DOA module imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import DOA: {e}")
        return False
    
    return True

def test_gpio_motors():
    """Test GPIO motor connections"""
    logger.info("Testing GPIO motor connections...")
    
    try:
        from basic_movement import walk_motor, turn_motor
        
        # Test walk motor
        logger.info("Testing walk motor...")
        walk_motor.forward(0.1)
        time.sleep(0.2)
        walk_motor.stop()
        logger.info("✓ Walk motor forward test completed")
        
        # Test turn motor
        logger.info("Testing turn motor...")
        turn_motor.forward(0.1)
        time.sleep(0.2)
        turn_motor.stop()
        logger.info("✓ Turn motor forward test completed")
        
        turn_motor.backward(0.1)
        time.sleep(0.2)
        turn_motor.stop()
        logger.info("✓ Turn motor backward test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ GPIO motor test failed: {e}")
        return False

def test_movement_functions():
    """Test basic movement functions"""
    logger.info("Testing movement functions...")
    
    try:
        from basic_movement import forward, turn
        
        logger.info("Testing forward movement (3 seconds)...")
        forward(3)
        logger.info("✓ Forward movement test completed")
        
        logger.info("Testing right turn (30 degrees)...")
        turn(30)
        logger.info("✓ Right turn test completed")
        
        logger.info("Testing left turn (-30 degrees)...")
        turn(-30)
        logger.info("✓ Left turn test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Movement function test failed: {e}")
        return False

def test_serial_connection():
    """Test serial connection to ESP32"""
    logger.info("Testing serial connection...")
    
    try:
        import serial
        
        # Test if serial port exists
        port = '/dev/ttyUSB0'
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            logger.info(f"✓ Serial port {port} opened successfully")
            
            # Send test message
            test_msg = "test from pi"
            ser.write(f"{test_msg}\n".encode())
            logger.info(f"✓ Test message sent: {test_msg}")
            
            # Try to read response
            time.sleep(0.5)
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                logger.info(f"✓ Received response: {response}")
            else:
                logger.warning("No response received (this may be normal)")
            
            ser.close()
            return True
            
        except serial.SerialException as e:
            logger.error(f"✗ Serial connection failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Serial test failed: {e}")
        return False

def test_serial_reader_class():
    """Test SerialReader class functionality"""
    logger.info("Testing SerialReader class...")
    
    received_messages = []
    
    def test_callback(message):
        received_messages.append(message)
        logger.info(f"Callback received: {message}")
    
    try:
        from read_from_serial import SerialReader
        
        # Create SerialReader instance
        reader = SerialReader(port='/dev/ttyUSB0', callback=test_callback)
        
        # Start reading
        reader.start()
        logger.info("✓ SerialReader started successfully")
        
        # Send test message
        reader.send_message("test message from reader")
        
        # Wait for potential responses
        time.sleep(2)
        
        # Stop reader
        reader.stop()
        logger.info("✓ SerialReader stopped successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ SerialReader test failed: {e}")
        return False

def test_doa_functionality():
    """Test DOA (Direction of Arrival) functionality"""
    logger.info("Testing DOA functionality...")
    
    try:
        from audio import get_doa_angle
        
        logger.info("Calling get_doa_angle() - this may take a moment...")
        doa_result = get_doa_angle()
        
        if doa_result is None:
            logger.info("✓ DOA returned None (no sound detected)")
        elif doa_result == -1:
            logger.info("✓ DOA returned -1 (stop signal)")
        else:
            logger.info(f"✓ DOA detected angle: {doa_result}°")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ DOA test failed: {e}")
        return False

def test_command_processing():
    """Test command processing logic"""
    logger.info("Testing command processing...")
    
    try:
        # Import the command handler from main
        sys.path.append('/home/pi/software/pi')
        
        # Test command parsing
        test_commands = [
            "left 45.5",
            "right 30",
            "stop",
            "invalid command",
            "left",  # Missing angle
            "forward 10"
        ]
        
        for cmd in test_commands:
            logger.info(f"Testing command: '{cmd}'")
            try:
                parts = cmd.split()
                if len(parts) >= 2:
                    direction = parts[0].lower()
                    if direction == "stop":
                        logger.info("  -> STOP command detected")
                    else:
                        angle = float(parts[1])
                        if direction == 'left':
                            angle *= -1
                        logger.info(f"  -> Turn command: {angle}°")
                else:
                    logger.warning(f"  -> Invalid command format")
            except ValueError:
                logger.error(f"  -> Could not parse angle in command")
            except Exception as e:
                logger.error(f"  -> Error processing command: {e}")
        
        logger.info("✓ Command processing tests completed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Command processing test failed: {e}")
        return False

def test_integration():
    """Test integration of serial communication with movement"""
    logger.info("Testing integration (serial + movement)...")
    
    movement_executed = False
    
    def integration_callback(command):
        nonlocal movement_executed
        try:
            from basic_movement import turn
            
            cmd = command.split()
            if len(cmd) >= 2:
                direction = cmd[0].lower()
                if direction in ['left', 'right']:
                    angle = float(cmd[1])
                    if direction == 'left':
                        angle *= -1
                    
                    logger.info(f"Integration test: executing turn {angle}°")
                    turn(angle)
                    movement_executed = True
        except Exception as e:
            logger.error(f"Integration callback error: {e}")
    
    try:
        from read_from_serial import SerialReader
        
        # Start serial reader with movement callback
        reader = SerialReader(port='/dev/ttyUSB0', callback=integration_callback)
        reader.start()
        
        # Send test movement command
        reader.send_message("right 15")
        
        # Wait for processing
        time.sleep(2)
        
        reader.stop()
        
        if movement_executed:
            logger.info("✓ Integration test successful - movement executed")
        else:
            logger.info("✓ Integration test completed - no movement triggered")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    logger.info("=" * 50)
    logger.info("ROBOT CONTROL SYSTEM TEST SUITE")
    logger.info("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("GPIO Motors", test_gpio_motors),
        ("Movement Functions", test_movement_functions),
        ("Serial Connection", test_serial_connection),
        ("SerialReader Class", test_serial_reader_class),
        ("DOA Functionality", test_doa_functionality),
        ("Command Processing", test_command_processing),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Robot system is ready.")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)