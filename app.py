import streamlit as st
import base64
import tempfile
import speech_recognition as sr

from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import record_user_audio, play_ai_voice

st.set_page_config(page_title="AI Interview Partner", layout="wide")

if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "chat" not in st.session_state:
    st.session_state.chat = []

st.title("🎤 AI Interview Practice Partner (Voice Mode)")

if st.button("Start Interview"):
    first_q = st.session_state.engine.ask_question()
    if first_q:
        st.session_state.chat.append(("AI", first_q))
        play_ai_voice(first_q)

st.subheader("🎙 Speak Your Answer")
audio_b64 = record_user_audio()

if audio_b64:
    audio_bytes = base64.b64decode(audio_b64)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        wav_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as src:
        audio_data = recognizer.record(src)
        try:
            user_text = recognizer.recognize_google(audio_data)
        except:
            user_text = ""

    if user_text:
        st.session_state.chat.append(("You", user_text))
        result = st.session_state.engine.process_user_answer(user_text)

        if result["action"] == "followup":
            ai_reply = result["followup"]
        elif result["action"] == "next":
            ai_reply = result["next_question"]
        else:
            ai_reply = "Thank you for completing the interview."

        st.session_state.chat.append(("AI", ai_reply))
        play_ai_voice(ai_reply)

st.subheader("Conversation")
for role, message in st.session_state.chat:
    st.markdown(f"**{role}:** {message}")

if st.button("Get Feedback"):
    transcript = [
        {"type": "user" if r == "You" else "agent", "text": m}
        for r, m in st.session_state.chat
    ]
    fb = analyze_interview(transcript)
    st.write(fb)
