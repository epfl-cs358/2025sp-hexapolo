import sys
import struct
import logging
import math
import time
from audio import play_wav, AudioIn

# Constants
SAMPLE_RATE = 8000     # 8 kHz
CHUNK_SIZE = 205       # ~25ms at 8kHz (tweakable)
TARGET_FREQ = 1000     # Frequency to detect (Hz)
MEASURE_DURATION = 3   # Seconds to measure each phase

countdown_files = ["5.wav", "4.wav", "3.wav", "2.wav", "1.wav"]

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

def convert_to_samples(raw_bytes):
    """Convert raw audio bytes to integer samples"""
    if not raw_bytes or len(raw_bytes) < CHUNK_SIZE * 2:
        return None
    return struct.unpack('<' + 'h' * CHUNK_SIZE, raw_bytes)

# Function to measure energy in a phase
def measure_phase(prompt, audio_file):
    audio_in = AudioIn()

    logger.info(f"\n🔊 {prompt}")
    play_wav(audio_file)

    for file in countdown_files:
        play_wav(file)
        time.sleep(0.5)

    logger.info("Measuring...")

    energies = []
    start_time = time.time()

    while (time.time() - start_time) < MEASURE_DURATION:
        samples = convert_to_samples(audio_in.read_frame())
        if samples is None:
            break
        energy = goertzel(samples)
        energies.append(energy)
        logger.info('.', end='', flush=True)

    logger.info(" done.")
    audio_in.process.stdout.close()
    audio_in.process.wait()

    return energies

def calibrate():
    global threshold

    # -------- Calibration flow --------
    logger.info("🎛️  Goertzel Frequency Detector with Calibration and Detection")
    logger.info(f"Target frequency: {TARGET_FREQ} Hz")
    logger.info(f"Sample rate: {SAMPLE_RATE} Hz, Chunk size: {CHUNK_SIZE} samples\n")

    # Phase 1: background noise
    noise_energies = measure_phase("Ensure no tone is playing (just background noise).", "cal.wav")

    # Phase 2: tone signal
    tone_energies = measure_phase("Now play the tone at target frequency.", "calwtone.wav")

    # Analyze and suggest threshold
    avg_noise = sum(noise_energies) / len(noise_energies)
    max_noise = max(noise_energies)

    avg_tone = sum(tone_energies) / len(tone_energies)
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

def detect(audio_in):
    # -------- Detection flow --------
    logger.info("\n🔍 Starting frequency detection...")
    start_time = time.time()
    counter = 0

    while True:
        raw_data = audio_in.read_frame()
        time_diff = time.time() - start_time

        if time_diff % 1000 == 0:
            counter = 0

        if pcm is None:
            break

        energy = goertzel(convert_to_samples(raw_data))
        if energy > threshold:
            counter += 1 
            logger.info(f"Detected {TARGET_FREQ} Hz! Energy = {int(energy)}")

        if counter > 12:
            return True

        if time_diff > 15 * 1000:
            return False

if __name__ == "__main__":
    calibrate()
