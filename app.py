import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import record_user_audio, play_ai_voice
import base64
import speech_recognition as sr
import tempfile

st.set_page_config(page_title="AI Interview Partner", layout="wide")

# session init
if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "chat" not in st.session_state:
    st.session_state.chat = []

st.title("🎤 AI Interview Practice Partner (Voice Mode — Option B)")


# ------------------------------------------------------------
# START INTERVIEW
# ------------------------------------------------------------
if st.button("Start Interview"):
    q = st.session_state.engine.ask_question()
    if q:
        st.session_state.chat.append(("AI", q))
        play_ai_voice(q)


# ------------------------------------------------------------
# USER RECORDING (OPTION B)
# ------------------------------------------------------------
st.subheader("🎙 Speak Your Answer")
audio_b64 = record_user_audio()

if audio_b64:
    # convert base64 to wav file
    audio_bytes = base64.b64decode(audio_b64)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    # transcribe
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data)
        except:
            text = ""

    if text:
        st.session_state.chat.append(("You", text))

        # engine generate next step
        result = st.session_state.engine.process_user_answer(text)

        if result["action"] == "followup":
            reply = result["followup"]
        elif result["action"] == "next":
            reply = result["next_question"]
        else:
            reply = "That concludes the interview. Thank you!"

        # log & speak
        st.session_state.chat.append(("AI", reply))
        play_ai_voice(reply)


# ------------------------------------------------------------
# SHOW CHAT
# ------------------------------------------------------------
st.subheader("Conversation")
for spk, msg in st.session_state.chat:
    st.markdown(f"**{spk}:** {msg}")


# ------------------------------------------------------------
# FEEDBACK
# ------------------------------------------------------------
if st.button("Get Feedback"):
    transcript = [{"type": "user" if p == "You" else "agent", "text": m} for p, m in st.session_state.chat]
    report = analyze_interview(transcript)
    st.write(report)
