import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import pyttsx3
import tempfile
import streamlit as st


# -----------------------------
# Initialize Text-to-Speech
# -----------------------------
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 180)   # speaking speed
tts_engine.setProperty('volume', 1.0) # max volume


# -----------------------------
# User Voice → Text
# -----------------------------
def get_user_voice_text():
    """
    Records user audio from Streamlit mic widget,
    converts it to text using SpeechRecognition.
    Returns recognized text or None.
    """

    audio_data = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop",
        key="voice_input"
    )

    if audio_data:
        recognizer = sr.Recognizer()

        # Convert bytes to AudioFile
        with sr.AudioFile(audio_data["file"]) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand your audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."

    return None



# -----------------------------
# AI Text → Voice
# -----------------------------
def speak_text(text: str):
    """
    Converts AI text into speech using pyttsx3.
    Creates a temporary audio file and returns its path
    so Streamlit can play it using st.audio().
    """

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_audio_path = f.name

    # Save speech to file
    tts_engine.save_to_file(text, temp_audio_path)
    tts_engine.runAndWait()

    return temp_audio_path



# -----------------------------
# Streamlit Helper
# -----------------------------
def play_ai_voice(text: str):
    """
    High-level wrapper: Convert text → speech,
    and play it in Streamlit.
    """
    audio_path = speak_text(text)
    st.audio(audio_path, format="audio/mp3")
