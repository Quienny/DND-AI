import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 3  # seconds

print("🎙️ Recording for 3 seconds...")
recording = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
sd.wait()

# Save temp file
temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
wav.write(temp_file.name, SAMPLE_RATE, (recording * 32767).astype(np.int16))

print("✅ Saved audio to:", temp_file.name)
os.startfile(temp_file.name)  # This will open the file in your default player
