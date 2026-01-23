Natural Language Voice Assistant 

Overview

This project is a local voice assistant that can:
	•	Recognize spoken English commands (ASR via Vosk)
	•	Speak responses (TTS via pyttsx3)
	•	Track conversation context
	•	Retrieve weather info from the weather API
	•	Manage calendar appointments via the calendar API
	•	Run entirely locally, without cloud services

⸻

Setup Instructions

1. Clone the repository
# git clone https://github.com/GABhorkar/NaturalLangSystem.git
cd NaturalLangSystem/nl_voice_assistant
2. Install dependencies
# pip install vosk sounddevice pyttsx3 requests python-dateutil soundfile
3. Verify your Python version
# python3 --version
	•	Recommended: Python 3.9+

  Running the Assistant

1. Test ASR + TTS
 python3 asr_tts.py
	•	Assistant should greet you via speech.
	•	Speak something simple like “Hello” — it should repeat it.
2. Run the full assistant
python3 assistant.py

	•	Speak natural language commands for weather and calendar.
	•	Example commands:
	•	“What will the weather be like today in Marburg?”
	•	“Will it rain there on Saturday?”
	•	“Add an appointment titled Dentist for the 12th of January.”
	•	“Where is my next appointment?”
	•	“Delete the previously created appointment.”
	•	“Change the place for my appointment tomorrow.”

⸻

Supported Features
	•	Weather: Forecast for any known place and day, plus rain check.
	•	Calendar: Create, read, update, delete appointments.
	•	Conversation Memory: Can refer to previous turns (e.g., last appointment).
	•	Cross-Platform TTS: Works on Mac, Linux, Windows.

⸻

Verification Checklist (MS3)
	1.	Run asr_tts.py – you hear greeting + repeats your speech.
	2.	Run assistant.py – test commands listed above.
	3.	Confirm conversation context works across multiple turns.
	4.	.idea/, .venv/, and Python cache files are ignored (git status).
	5.	Verify no cloud API dependencies; only local + provided APIs.

⸻

Notes
	•	Vosk model path: vosk-model-small-en-us-0.15
	•	Python packages: vosk, sounddevice, pyttsx3, requests, python-dateutil
	•	To stop the assistant: say “exit”, “quit”, or press Ctrl+C.
