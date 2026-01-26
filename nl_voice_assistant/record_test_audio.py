"""
Helper script to record test audio files for Docker submission
Records audio from microphone and saves as 16kHz mono WAV files
"""

import sounddevice as sd
import soundfile as sf
import os
import sys

SAMPLE_RATE = 16000
DURATION = 5  # seconds per recording
OUTPUT_DIR = "audio_samples"

# Test cases to record
TEST_CASES = [
    ("01_greeting.wav", "Say: Hello"),
    ("02_weather_marburg.wav", "Say: What will the weather be like in Marburg today?"),
    ("03_check_rain.wav", "Say: Will it rain there tomorrow?"),
    ("04_create_appointment.wav", "Say: Add an appointment titled Dentist for January 12th"),
    ("05_next_appointment.wav", "Say: What is my next appointment?"),
    ("06_update_location.wav", "Say: Change the location to Berlin"),
    ("07_delete_appointment.wav", "Say: Delete the previously created appointment"),
]

def record_audio(duration=DURATION):
    """Record audio from microphone"""
    print(f"  🎤 Recording for {duration} seconds...")
    print("  (Speak now!)")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()

    print("  ✅ Recording complete!")
    return audio

def save_audio(audio, filename):
    """Save audio to WAV file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    sf.write(filepath, audio, SAMPLE_RATE)
    print(f"  💾 Saved to: {filepath}")

def main():
    print("=" * 60)
    print("Voice Assistant Test Audio Recorder")
    print("=" * 60)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ Output directory: {OUTPUT_DIR}/")
    print()

    print("Instructions:")
    print("  - Speak clearly into your microphone")
    print("  - Each recording is 5 seconds")
    print("  - Press Enter to start each recording")
    print("  - Press Ctrl+C to exit anytime")
    print()

    try:
        for filename, prompt in TEST_CASES:
            print("-" * 60)
            print(f"📝 {filename}")
            print(f"   {prompt}")
            print()

            input("  Press Enter to start recording... ")

            audio = record_audio(DURATION)
            save_audio(audio, filename)

            print()

        print("=" * 60)
        print("✅ All test audio files recorded successfully!")
        print(f"📁 Location: {OUTPUT_DIR}/")
        print()
        print("Files created:")
        for filename, _ in TEST_CASES:
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath) / 1024
                print(f"  ✓ {filename} ({size:.1f} KB)")

        print()
        print("Next steps:")
        print("  1. Test your audio files: python3 asr_tts_batch.py")
        print("  2. Build Docker image: docker build -t voice-assistant .")
        print("  3. Run Docker: docker-compose up")

    except KeyboardInterrupt:
        print("\n\n⚠️  Recording cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check dependencies
    try:
        import sounddevice
        import soundfile
    except ImportError as e:
        print("❌ Missing dependency:", e)
        print("\nInstall required packages:")
        print("  pip install sounddevice soundfile")
        sys.exit(1)

    main()