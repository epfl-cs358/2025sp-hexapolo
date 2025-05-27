import sys
import struct
import math
import time

SAMPLE_RATE = 8000
CHUNK_SIZE = 205
TARGET_FREQ = 1000
MEASURE_DURATION = 3  # seconds to measure each phase

k = int(0.5 + ((CHUNK_SIZE * TARGET_FREQ) / SAMPLE_RATE))
omega = (2.0 * math.pi * k) / CHUNK_SIZE
cosine = math.cos(omega)
coeff = 2.0 * cosine

def goertzel(samples):
    s_prev = 0.0
    s_prev2 = 0.0
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    power = s_prev2**2 + s_prev**2 - coeff * s_prev * s_prev2
    return power

def read_chunk():
    data = sys.stdin.buffer.read(CHUNK_SIZE * 2)
    if len(data) < CHUNK_SIZE * 2:
        return None
    return struct.unpack('<' + 'h'*CHUNK_SIZE, data)

def measure_phase(prompt):
    print(f"\n🔊 {prompt}")
    # input("Press Enter to start measuring...")
    # user_input = input("Press Enter to start measuring...")
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
print("🎛️  Goertzel Frequency Detector Calibration")
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
