import streamlit as st
from gtts import gTTS
import base64
import io
import random
from typing import List, Dict
import re
import numpy as np
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

st.set_page_config(page_title="Interview Practice Partner", layout="wide")

QUESTIONS = {
    "Software Engineer": [
        "Tell me about yourself.",
        "Explain OOP concepts.",
        "Tell me about a challenging bug you fixed."
    ],
    "HR": [
        "Introduce yourself.",
        "Describe a time you resolved a conflict."
    ],
    "Sales": [
        "How do you handle objections?",
        "Tell me about a successful pitch."
    ],
    "Data Analyst": [
        "Explain a data project.",
        "How do you clean messy data?"
    ]
}

if "transcript" not in st.session_state:
    st.session_state.transcript = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None


def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.audio(f"data:audio/mp3;base64,{b64}", format="audio/mp3")


def analyze_interview(transcript: List[Dict]):
    answers = [ev["text"] for ev in transcript if ev["type"] == "user"]
    communication_score = 0.0
    technical_score = 0.0
    examples_score = 0.0

    for a in answers:
        wc = len(a.split())
        communication_score += 4.5 if wc > 80 else 4.0 if wc > 40 else 3.0 if wc > 20 else 2.0

        tech_keywords = ["design", "algorithm", "debug", "performance", "optimization", "complexity"]
        technical_score += 4.0 if any(k in a.lower() for k in tech_keywords) else 2.0

        examples_score += 4.0 if re.search(r'\b(\d+%|improved|reduced|resulted)\b', a.lower()) else 2.0

    n = max(1, len(answers))
    return {
        "communication": round(min(5.0, communication_score / n), 2),
        "technical": round(min(5.0, technical_score / n), 2),
        "examples": round(min(5.0, examples_score / n), 2)
    }


class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv_audio(self, frame):
        audio = frame.to_ndarray()
        audio = audio.astype(np.float32).tobytes()
        audio_data = sr.AudioData(audio, 16000, 2)
        try:
            text = self.recognizer.recognize_google(audio_data)
            if text:
                st.session_state.transcript.append({"type": "user", "text": text})
        except:
            pass
        return frame


st.title("Interview Practice Partner")

role = st.selectbox("Select Interview Role", list(QUESTIONS.keys()))
col1, col2 = st.columns([2, 1])

with col2:
    if st.button("Ask Question"):
        q = random.choice(QUESTIONS[role])
        st.session_state.current_question = q
        st.session_state.transcript.append({"type": "agent", "text": q})
        speak(q)

with col1:
    st.subheader("Conversation")
    for e in st.session_state.transcript:
        prefix = "**Interviewer:**" if e["type"] == "agent" else "**You:**"
        st.markdown(f"{prefix} {e['text']}")

st.write("### Voice Answer")
webrtc_streamer(
    key="voice",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False}
)

st.write("### Text Answer")
txt = st.text_area("Type your answer")
if st.button("Submit Text"):
    if txt.strip():
        st.session_state.transcript.append({"type": "user", "text": txt})
        st.success("Answer submitted")

if st.button("Get Feedback"):
    report = analyze_interview(st.session_state.transcript)
    st.write("### Scores")
    st.write(report)
