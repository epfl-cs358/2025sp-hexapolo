from gpiozero import Motor
from time import sleep
import logging

# Setup logger
logger = logging.getLogger(__name__)

walk_motor = Motor(forward=4, backward=11)
turn_motor = Motor(forward=23, backward=24)

def forward(duration=1, speed=1):
    """Move forward for specified duration in seconds"""
    logger.info(f"Walking forward for {duration} second(s) at speed {speed}")
    try:
        walk_motor.forward(speed)
        sleep(duration)
        walk_motor.stop()
        logger.debug(f"Forward movement completed successfully")
    except Exception as e:
        logger.error(f"Error during forward movement: {e}")
        walk_motor.stop()  # Ensure motor stops on error
        raise

def turn(angle, speed=1):
    """Turn by specified angle in degrees (positive=right, negative=left)"""
    # Convert angle to time-based turn (simplified approach)
    # Shortest turn
    if angle > 180:
        angle -= 360
    elif angle < -180:
        angle += 360
    
    direction = 'CCW' if angle > 0 else 'CW'
    logger.info(f"Turning {direction} by {abs(angle)}° at speed {speed}")

    turn_time = abs(angle) / 50 * 0.5  # 0.5s per 90 degrees
    logger.debug(f"Calculated turn time: {turn_time:.2f} seconds")

    try:
        if angle > 0:
            turn_motor.backward(speed)
        else:
            turn_motor.forward(speed)

        sleep(turn_time)
        turn_motor.stop()
        logger.debug(f"Turn movement completed successfully")
    except Exception as e:
        logger.error(f"Error during turn movement: {e}")
        turn_motor.stop()  # Ensure motor stops on error
        raise
