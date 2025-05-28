from usb_4_mic_array.tuning import Tuning
import usb.core
import subprocess
import time
import logging
import numpy as np
from pathlib import Path

# Config
AUDIO_DEVICE = "plughw:CARD=ArrayUAC10,DEV=0"  # Find with: arecord -L
SAMPLE_RATE = 16000
FRAME_MS = 30
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples for 30ms

logger = logging.getLogger(__name__)

class AudioIn:
    def __init__(self):
        self.process = subprocess.Popen(
            ["arecord", "-t", "raw", "-D", AUDIO_DEVICE,
             "-c", "1", "-f", "S16_LE", "-r", str(SAMPLE_RATE)],
            stdout=subprocess.PIPE,
            bufsize=CHUNK_SIZE*2
        )

    def read_frame(self):
        return self.process.stdout.read(CHUNK_SIZE * 2)  # 16-bit samples

def play_wav(path):
    subprocess.run(["aplay", "-q", "-D", AUDIO_DEVICE, path])


def get_doa_angle():
    # Initialize hardware
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if not dev:
        logger.info("Mic array not found")
        return None

    tuning = Tuning(dev)
    audio_in = AudioIn()

    logger.info("Listening for wake word...")
    try:
        while True:
            if detect(audio_in):
                angle = (tuning.direction + 90) % 360
                logger.info(f"Wake word detected! Angle: {angle}°")
                play_wav("hear.wav")
                return angle
    except KeyboardInterrupt:
        logger.info("\nStopped by user")
        return -999
    finally:
        audio_in.process.terminate()

if __name__ == "__main__":
    get_doa_angle()
