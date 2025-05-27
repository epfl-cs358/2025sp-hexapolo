import sys
import struct
import math
import time
# import numpy as np
# import sounddevice as sd
import RPi.GPIO as GPIO


# Constants
SAMPLE_RATE = 8000     # 8 kHz
CHUNK_SIZE = 205       # ~25ms at 8kHz (tweakable)
TARGET_FREQ = 1000     # Frequency to detect (Hz)
THRESHOLD = 14552392   # Energy threshold (calibrated value)
MEASURE_DURATION = 3   # Seconds to measure each phase

# GPIO setup for the buzzer
BUZZER_PIN = 18  # Replace with the GPIO pin connected to the buzzer
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Pre-compute Goertzel constants
k = int(0.5 + ((CHUNK_SIZE * TARGET_FREQ) / SAMPLE_RATE))
omega = (2.0 * math.pi * k) / CHUNK_SIZE
cosine = math.cos(omega)
coeff = 2.0 * cosine

# Function to generate and play a "bip" sound
def play_bip_with_speaker(frequency=1000, duration=0.2, repeat=2, pause=0.2):
    """Plays a bip sound at the given frequency and duration."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Generate sine wave
    for _ in range(repeat):
        sd.play(wave, samplerate=SAMPLE_RATE)
        sd.wait()  # Wait until the sound finishes
        time.sleep(pause)

def play_bip_with_buzzer(duration=0.2, repeat=2, pause=0.2):
    """Plays a bip sound using the buzzer."""
    for _ in range(repeat):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
        time.sleep(duration)               # Wait for the duration of the bip
        GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off the buzzer
        time.sleep(pause)  

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

# Function to read a chunk of audio data
def read_chunk():
    data = sys.stdin.buffer.read(CHUNK_SIZE * 2)  # 2 bytes per sample
    if len(data) < CHUNK_SIZE * 2:
        return None
    return struct.unpack('<' + 'h' * CHUNK_SIZE, data)

# Function to measure energy in a phase
def measure_phase(prompt):
    print(f"\n🔊 {prompt}")
    play_bip_with_buzzer()  # Play the bip sound twice before measurin
    print("Start measuring in ")
    for i in range(10, 0, -1):
        print(i, end=' ', flush=True)
        time.sleep(1)
    print()
    print("Measuring...", end='', flush=True)

    energies = []
    start_time = time.time()

    while time.time() - start_time < MEASURE_DURATION:
        samples = read_chunk()
        if samples is None:
            break
        energy = goertzel(samples)
        energies.append(energy)
        print('.', end='', flush=True)

    print(" done.")
    return energies

# -------- Calibration flow --------
print("🎛️  Goertzel Frequency Detector with Calibration and Detection")
print(f"Target frequency: {TARGET_FREQ} Hz")
print(f"Sample rate: {SAMPLE_RATE} Hz, Chunk size: {CHUNK_SIZE} samples\n")

# Phase 1: background noise
noise_energies = measure_phase("Ensure no tone is playing (just background noise).")

# Phase 2: tone signal
tone_energies = measure_phase("Now play the tone at target frequency.")

# Analyze and suggest threshold
avg_noise = sum(noise_energies) / len(noise_energies)
max_noise = max(noise_energies)

avg_tone = sum(tone_energies) / len(tone_energies)
min_tone = min(tone_energies)

suggested_threshold = (max_noise + min_tone) / 2

print("\n📈 Calibration Results:")
print(f"  Avg noise energy: {int(avg_noise)}")
print(f"  Max noise energy: {int(max_noise)}")
print(f"  Min tone energy:  {int(min_tone)}")
print(f"  Avg tone energy:  {int(avg_tone)}")
print(f"\n✅ Suggested THRESHOLD: {int(suggested_threshold)}")

print("\nℹ️ Use this value in your detection script like:")
print(f"   THRESHOLD = {int(suggested_threshold)}")

# -------- Detection flow --------
print("\n🔍 Starting frequency detection...")
while True:
    samples = read_chunk()
    if samples is None:
        break

    energy = goertzel(samples)
    if energy > THRESHOLD:
        print(f"Detected {TARGET_FREQ} Hz! Energy = {int(energy)}")