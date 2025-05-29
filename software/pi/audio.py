from usb_4_mic_array.tuning import Tuning
import usb.core
import subprocess
import time
import logging
import numpy as np
from pathlib import Path
from play_wav import play_wav
from calibrate_and_detect import detect, calibrate

logger = logging.getLogger(__name__)

def get_doa_angle(threshold):
    # Initialize hardware
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    if not dev:
        logger.info("Mic array not found")
        return None

    tuning = Tuning(dev)

    logger.info("Listening for wake word...")
    try:
        while True:
            if detect(threshold):
                angle = (tuning.direction + 90) % 360
                logger.info(f"Wake word detected! Angle: {angle}°")
                play_wav("hear.wav")
                return angle
    except KeyboardInterrupt:
        logger.info("\nStopped by user")
        return -999
