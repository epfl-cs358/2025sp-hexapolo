from time import sleep
import logging
import signal
import sys
from audio import get_doa_angle, play_wav
from basic_movement import forward, turn
from read_from_serial import SerialReader

# Global flag for graceful shutdown
shutdown_flag = False
continue_follow = False

def setup_logging():
    """Setup logging configuration for service operation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/var/log/robot_control.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag, continue_follow
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True
    continue_follow = False

# Setup signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def handle_command(command):
    """Handle incoming commands from ESP32"""
    global continue_follow
    logger = logging.getLogger(__name__)

    try:
        cmd = command.split()
        if len(cmd) >= 1:
            direction = cmd[0].lower()
            if direction == "stop":
                logger.info("Received STOP command, stopping follow mode")
                continue_follow = False 
            else:
                angle = float(cmd[1])  # Convert angle to float
                if direction == 'left':
                    angle *= -1
                logger.info(f"Executing turn command: {direction} {angle}°")
                # try this
                turn(angle)
                forward(3)
        else:
            logger.warning(f"Invalid command format: {command}")
    except Exception as e:
        logger.error(f"Error processing command '{command}': {e}")

def follow():
    global continue_follow, shutdown_flag
    logger = logging.getLogger(__name__)
    
    logger.info("Starting follow mode - initializing serial communication")
    serial_reader = SerialReader(port='/dev/ttyUSB0', callback=handle_command)
    serial_reader.start()
    continue_follow = True

    try:
        logger.info("Follow mode active - robot will move forward and respond to turn commands")
        while continue_follow and not shutdown_flag:
            sleep(0.1)  # Small delay to check flags more frequently
    except KeyboardInterrupt:
        logger.info("Follow mode interrupted by user")
    except Exception as e:
        logger.error(f"Error in follow mode: {e}")
    finally:
        logger.info("Stopping follow mode and closing serial connection")
        serial_reader.stop()

def main_control_loop():
    logger = logging.getLogger(__name__)
    
    logger.info("Starting main robot control loop")
    logger.info("Robot will listen for audio DOA, turn toward sound, then follow movement commands")

    try:
        while not shutdown_flag:
            try:
                play_wav()
                doa = get_doa_angle()
                if not doa:
                    logger.info("DOA loop interrupted, stopping main loop")
                    break
                elif doa is not None:
                    logger.info(f"DOA detected at {doa}°, turning toward sound source")
                    turn(doa)
                    sleep(0.5)
                    logger.info("Entering follow mode")
                    follow()
                    if shutdown_flag:
                        break
                else:
                    # No DOA detected, wait a bit before trying again
                    sleep(2)
            except Exception as e:
                logger.error(f"Error in main control loop iteration: {e}")
                sleep(1)  # Wait before retrying
                
    except KeyboardInterrupt:
        logger.info("Main control loop interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in main control loop: {e}")
    finally:
        logger.info("Main control loop terminated")

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Robot Control Service Starting...")
    logger.info("System: ESP32 Camera -> Laptop CV -> ESP32 -> Pi Robot Control")
    
    try:
        main_control_loop()
    except Exception as e:
        logger.error(f"Fatal error in robot control service: {e}")
        sys.exit(1)
    finally:
        logger.info("Robot Control Service Stopped")
