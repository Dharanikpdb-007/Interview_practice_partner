import streamlit as st
from st_audiorec import st_audiorec
import tempfile
import speech_recognition as sr
from gtts import gTTS
import os


def get_user_voice_text():
    st.write("🎙️ Click to record your answer:")

    audio_bytes = st_audiorec()

    if audio_bytes is None:
        return None

    # Save temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    # Speech recognition
    r = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        return "Sorry, I couldn't understand what you said."


def play_ai_voice(text):
    tts = gTTS(text=text, lang="en")
    temp_path = "ai_voice.mp3"
    tts.save(temp_path)
    audio_file = open(temp_path, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")
