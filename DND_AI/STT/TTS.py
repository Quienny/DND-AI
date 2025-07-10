import whisper
import sounddevice as sd
import numpy as np
import tempfile
import os
import pyautogui
import pyperclip
import time
import keyboard
from scipy.io.wavfile import write as write_wav
from datetime import datetime
import threading
import re

SAMPLE_RATE = 16000
CHANNELS = 1
KEY_HOLD = 'caps lock'
LOG_FILE = os.path.join(os.path.dirname(__file__), 'whisper_typing.log')

model = whisper.load_model("base")

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def fix_punctuation(text):
    text = re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    if not text.endswith(('.', '!', '?')):
        text += '.'
    return text

def record_audio_hold_key():
    log("Started recording...")
    frames = []

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32') as stream:
            while keyboard.is_pressed(KEY_HOLD) and not keyboard.is_pressed('esc'):
                data, _ = stream.read(1024)
                frames.append(data.copy())
                time.sleep(0.01)
    except Exception as e:
        log(f"⚠️ Recording error: {str(e)}")

    log(f"Stopped recording. Collected {len(frames)} audio chunks.")
    if not frames:
        raise ValueError("No audio recorded.")

    audio = np.concatenate(frames, axis=0)
    path = tempfile.mktemp(suffix=".wav")
    write_wav(path, SAMPLE_RATE, (audio * 32767).astype(np.int16))
    return path

def transcribe_with_timeout(audio_path, timeout_sec=30):
    result_container = {}

    def transcribe():
        try:
            log("⏳ Whisper.transcribe() started.")
            result = model.transcribe(audio_path, fp16=False)
            result_container['text'] = result['text'].strip()
            log("✅ Whisper.transcribe() completed.")
        except Exception as e:
            result_container['error'] = str(e)

    thread = threading.Thread(target=transcribe)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        log("❌ Transcription timeout.")
        return None

    if 'error' in result_container:
        log(f"❌ Transcription error: {result_container['error']}")
        return None

    return result_container.get('text', '')

def transcribe_and_paste(audio_path):
    log("Transcribing...")
    text = transcribe_with_timeout(audio_path)
    if not text:
        log("⚠️ No text transcribed.")
        return

    formatted = fix_punctuation(text)
    log(f"Transcribed: {formatted}")
    time.sleep(0.3)

    pyperclip.copy(formatted)
    pyautogui.hotkey("ctrl", "v")
    log(f"Pasted: {formatted}")

    if os.path.exists(audio_path):
        os.remove(audio_path)

def main():
    log("🟢 Whisper typing (Caps Lock hold) started. Hold Caps Lock to speak, release to transcribe and paste. Press ESC to quit.")
    already_held = False

    while True:
        try:
            if keyboard.is_pressed('esc'):
                log("🛑 ESC key pressed — exiting.")
                break

            if keyboard.is_pressed(KEY_HOLD):
                if not already_held:
                    already_held = True
                    path = record_audio_hold_key()
                    transcribe_and_paste(path)
            else:
                already_held = False

            time.sleep(0.01)

        except Exception as e:
            log(f"⚠️ Main loop error: {str(e)}")

if __name__ == "__main__":
    main()
