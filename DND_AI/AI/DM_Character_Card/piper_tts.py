import subprocess
import os
import tempfile
import re

def speak(text):
    piper_dir = r"C:\Users\Quint\Desktop\DND_AI\Piper"
    model = os.path.join(piper_dir, "en_GB-northern_english_male-medium.onnx")
    exe = os.path.join(piper_dir, "piper.exe")

    if not os.path.exists(exe) or not os.path.exists(model) or not os.path.exists(model + ".json"):
        print("[TTS] Model or executable not found.")
        return

    try:
        # Preserve commas/pauses, remove junk whitespace
        cleaned_text = re.sub(r'\s+', ' ', text.strip())

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
            tmp_path = tmp_audio.name

        subprocess.run(
            [exe, "-m", model, "--output_file", tmp_path],
            input=cleaned_text.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.run(
            ["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(tmp_path)

    except Exception as e:
        print(f"[TTS ERROR] {e}")
