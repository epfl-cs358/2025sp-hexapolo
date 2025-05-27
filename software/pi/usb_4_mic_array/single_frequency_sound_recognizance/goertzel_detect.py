import sys
import struct
import math

SAMPLE_RATE = 8000     # 8 kHz
CHUNK_SIZE = 205       # ~25ms at 8kHz (tweakable)
TARGET_FREQ = 1000     # Frequency to detect (Hz)
# THRESHOLD = 1000000    # Energy threshold (tweak based on environment)
THRESHOLD = 14552392

# Pre-compute Goertzel constants
k = int(0.5 + ((CHUNK_SIZE * TARGET_FREQ) / SAMPLE_RATE))
omega = (2.0 * math.pi * k) / CHUNK_SIZE
sine = math.sin(omega)
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
    data = sys.stdin.buffer.read(CHUNK_SIZE * 2)  # 2 bytes per sample
    if len(data) < CHUNK_SIZE * 2:
        return None
    return struct.unpack('<' + 'h'*CHUNK_SIZE, data)

while True:
    samples = read_chunk()
    if samples is None:
        break

    energy = goertzel(samples)
    # print(f"Energy: {int(energy)}")

    if energy > THRESHOLD:
        print(f"Detected {TARGET_FREQ} Hz! Energy = {int(energy)}")
