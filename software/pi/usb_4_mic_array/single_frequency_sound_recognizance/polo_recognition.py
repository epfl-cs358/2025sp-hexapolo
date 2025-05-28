import wave
import struct
import math
import numpy as np

SAMPLE_RATE = 8000     # 8 kHz
CHUNK_SIZE = 205       # ~25ms at 8kHz
TARGET_FREQ = 1000     # Frequency to detect (Hz)
THRESHOLD = 14552392   # Adjust as needed

# Goertzel constants
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

def process_audio_file(filename):
    with wave.open(filename, 'rb') as wf:
        assert wf.getnchannels() == 1, "Only mono files are supported"
        assert wf.getsampwidth() == 2, "Only 16-bit samples are supported"
        assert wf.getframerate() == SAMPLE_RATE, f"Expected sample rate {SAMPLE_RATE}"

        frames = wf.readframes(wf.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16)

        for i in range(0, len(samples) - CHUNK_SIZE + 1, CHUNK_SIZE):
            chunk = samples[i:i+CHUNK_SIZE]
            energy = goertzel(chunk)
            if energy > THRESHOLD:
                print(f"Detected {TARGET_FREQ} Hz! Energy = {int(energy)}")

# Example usage:
process_audio_file('POLO.wav')
