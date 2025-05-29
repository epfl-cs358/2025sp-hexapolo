import sys
import struct
import logging
import math
import time
import subprocess
from play_wav import play_wav

# Constants
SAMPLE_RATE = 8000     # 8 kHz
CHUNK_SIZE = 205       # ~25ms at 8kHz (tweakable)
TARGET_FREQ = 1000     # Frequency to detect (Hz)
MEASURE_DURATION = 3   # Seconds to measure each phase
EPS = 1e-6             # prevent divide by 0
TARGET_FREQ = 1000     # Frequency to detect (Hz)
AUDIO_DEVICE = "default:CARD=ArrayUAC10"  # Find with: arecord -L
DIR = "/home/hexapolo/project"

countdown_files = [f"{DIR}/3.wav", f"{DIR}/2.wav", f"{DIR}/1.wav"]

logger = logging.getLogger(__name__)

# Pre-compute Goertzel constants
k = int(0.5 + ((CHUNK_SIZE * TARGET_FREQ) / SAMPLE_RATE))
omega = (2.0 * math.pi * k) / CHUNK_SIZE
cosine = math.cos(omega)
coeff = 2.0 * cosine

# Goertzel algorithm
def goertzel(samples):
    s_prev = 0.0
    s_prev2 = 0.0
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    power = s_prev2**2 + s_prev**2 - coeff * s_prev * s_prev2
    return power

# Start audio recording process
def start_recording():
    return subprocess.Popen(
        ["arecord", "-D", AUDIO_DEVICE, "-f", "S16_LE", "-r", str(SAMPLE_RATE)],
        stdout=subprocess.PIPE
    )

# Function to read a chunk of audio data
def read_chunk(process):
    data = process.stdout.read(CHUNK_SIZE * 2)  # Read directly from subprocess pipe
    if len(data) < CHUNK_SIZE * 2:
        return None
    return struct.unpack('<' + 'h' * CHUNK_SIZE, data)

# Function to measure energy in a phase
def measure_phase(prompt, audio_file, process):
    logger.info(f"\n🔊 {prompt}")
    play_wav(audio_file)

    for file in countdown_files:
        play_wav(file)
        time.sleep(0.5)

    logger.info("Measuring...")

    energies = []
    start_time = time.time()
    raw_chunks = []

    # Only read data during measurement period
    while (time.time() - start_time) < MEASURE_DURATION:
        samples = read_chunk(process)
        if samples is None:
            break
        raw_chunks.append(samples)  # Store without processing
    
    # Process data AFTER acquisition
    energies = [goertzel(chunk) for chunk in raw_chunks]

    logger.info(" done.")
    return energies


def calibrate():
    process = start_recording()

    # -------- Calibration flow --------
    try:
        logger.info("🎛️  Goertzel Frequency Detector with Calibration and Detection")
        logger.info(f"Target frequency: {TARGET_FREQ} Hz")
        logger.info(f"Sample rate: {SAMPLE_RATE} Hz, Chunk size: {CHUNK_SIZE} samples\n")

        # Phase 1: background noise
        noise_energies = measure_phase("Ensure no tone is playing (just background noise).", f"{DIR}/cal.wav", process)

        # Phase 2: tone signal
        tone_energies = measure_phase("Now play the tone at target frequency.", f"{DIR}/calwtone.wav", process)

        # Analyze and suggest threshold
        avg_noise = sum(noise_energies) / (len(noise_energies) + EPS)
        max_noise = max(noise_energies)

        avg_tone = sum(tone_energies) / (len(tone_energies) + EPS)
        min_tone = min(tone_energies)

        threshold = (max_noise + min_tone) / 2


        logger.info("\n📈 Calibration Results:")
        logger.info(f"  Avg noise energy: {int(avg_noise)}")
        logger.info(f"  Max noise energy: {int(max_noise)}")
        logger.info(f"  Min tone energy:  {int(min_tone)}")
        logger.info(f"  Avg tone energy:  {int(avg_tone)}")
        logger.info(f"\n✅ Suggested THRESHOLD: {int(threshold)}")

        logger.info("\nℹ️ Use this value in your detection script like:")
        logger.info(f"   THRESHOLD = {int(threshold)}")
    finally:
        process.terminate()

    return threshold

def detect(threshold):
    process = start_recording()

    # -------- Detection flow --------
    try:
        logger.info("\n🔍 Starting frequency detection...")
        start_time = time.time()
        counter = 0
        time_diff = 0
        detected = False

        while time_diff < 15:
            samples = read_chunk(process)
            time_diff = time.time() - start_time

            if time_diff % 1 == 0:
                counter = 0

            if samples is None:
                break

            energy = goertzel(samples)

            if energy > (threshold/100):
                counter += 1 
                logger.info(f"Detected {TARGET_FREQ} Hz! Energy = {int(energy)}")

            if counter > 12:
                detected = True
                break
    except KeyboardInterrupt:
        logger.info("\nStopped by user")
        return detected
    finally:
        process.terminate()

    return detected
