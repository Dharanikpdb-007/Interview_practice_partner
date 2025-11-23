import streamlit as st
import tempfile
import speech_recognition as sr
from gtts import gTTS


def get_user_voice_text():
    st.write("🎙️ Upload your recorded answer (MP3/WAV):")

    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])

    if audio_file is None:
        return None

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_file.name) as tmp:
        tmp.write(audio_file.read())
        temp_path = tmp.name

    # Speech to text
    recog = sr.Recognizer()
    with sr.AudioFile(temp_path) as src:
        audio = recog.record(src)

    try:
        text = recog.recognize_google(audio)
        return text
    except:
        return "Sorry, I couldn't understand the audio."


def play_ai_voice(text):
    tts = gTTS(text=text, lang="en")
    path = "ai_voice.mp3"
    tts.save(path)

    with open(path, "rb") as f:
        audio_bytes = f.read()

    st.audio(audio_bytes, format="audio/mp3")
