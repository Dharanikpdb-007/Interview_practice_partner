import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import pyttsx3

# Initialize TTS
tts = pyttsx3.init()

def record_user_voice():
    audio_data = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop",
        key="voice_input"
    )
    if audio_data:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_data["file"]) as source:
            sound = recognizer.record(source)
        try:
            text = recognizer.recognize_google(sound)
            return text
        except:
            return "Sorry, I couldn't understand your voice."
    return None


def speak_ai(text):
    tts.say(text)
    tts.runAndWait()
    st.audio("speech.wav")  # optional if using file output


st.title("Interview Practice Partner (Voice Enabled)")

st.subheader("🎤 Speak your answer")
user_text = record_user_voice()

if user_text:
    st.write("**You said:**", user_text)

    # ---- Your interview engine response ----
    ai_reply = interview_engine.get_reply(user_text)

    st.write("### 🤖 AI Interviewer:", ai_reply)

    # AI voice output
    speak_ai(ai_reply)
