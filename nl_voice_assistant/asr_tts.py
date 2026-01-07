import json
import queue
import sys
import os
import asyncio
import tempfile

import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer
import edge_tts

from assistant import handle_intent
from nlu import parse_intent

# CONFIGURATION
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

print("ASR_TTS program started")

if not os.path.exists(MODEL_PATH):
    print("ERROR: Vosk model not found")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))
#---------------- TTS (WAV + sounddevice, CROSS-PLATFORM) ----------------
async def speak_async(text):
    print("Assistant:", text)

    voice = "en-US-AriaNeural"

    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_file = f.name

    communicate = edge_tts.Communicate(text, voice)

    # Save as WAV (no arguments in constructor, just filename)
    await communicate.save(wav_file)

    # Read WAV and play using sounddevice (cross-platform)
    data, samplerate = sf.read(wav_file, dtype="float32")
    sd.play(data, samplerate)
    sd.wait()

    os.remove(wav_file)


def speak(text):
    asyncio.run(speak_async(text))

# LISTEN ONCE
def listen_once():
    print("Listening... Speak now.")
    with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback
    ):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

# MAIN LOOP
if __name__ == "__main__":
    conversation_state = {
        "last_place": None,
        "last_day": None,
        "last_created_event_id": None,
        "last_referenced_event_id": None
    }

    speak("Hello. I am your voice assistant.")

    try:
        while True:
            user_text = listen_once()
            print("User:", user_text)

            if user_text.lower() in ["exit", "quit", "stop"]:
                speak("Goodbye!")
                break

            intent_data = parse_intent(user_text, conversation_state)
            print("Intent:", intent_data)

            response_text = handle_intent(intent_data, conversation_state)
            speak(response_text)

    except KeyboardInterrupt:
        speak("Goodbye!")
        sys.exit(0)