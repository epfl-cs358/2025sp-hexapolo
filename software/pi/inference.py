import numpy as np
import sounddevice as sd
import librosa
import tflite_runtime.interpreter as tflite
import time
import os

# === Settings ===
DURATION = 1.0                 # Record for 1 second
SAMPLING_RATE = 16000         # Make sure this matches training
MFCC_N = 10                   # n_mfcc used during training
THRESHOLD = 0.7               # Confidence threshold for detection
MODEL_PATH = "keyword_polo.tflite"

# === Load Model ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']
print("✅ Model loaded. Input shape:", input_shape)

# === Feature Extraction ===
def extract_mfcc(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLING_RATE, n_mfcc=MFCC_N)
    mfcc = mfcc.T
    mfcc = librosa.util.fix_length(mfcc, size=input_shape[1])
    return mfcc.reshape(input_shape).astype(np.float32)

# === Audio Capture and Inference ===
print("🎙️ System ready. Say 'polo' to test keyword detection.\n")

try:
    while True:
        print("🔁 Listening...")
        audio = sd.rec(int(DURATION * SAMPLING_RATE), samplerate=SAMPLING_RATE,
                       channels=1, dtype='float32')
        sd.wait()
        audio = np.squeeze(audio)

        mfcc_input = extract_mfcc(audio)
        interpreter.set_tensor(input_details[0]['index'], mfcc_input)
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        confidence = float(np.squeeze(output_data)[1])  # Assuming index 1 = "polo"

        if confidence > THRESHOLD:
            print(f"✅ POLO DETECTED! Confidence: {confidence:.2f}\n")
        else:
            print(f"❌ No keyword. Confidence: {confidence:.2f}\n")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("🛑 Stopped by user.")
