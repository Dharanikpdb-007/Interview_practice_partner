import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import speech_recognition as sr
from gtts import gTTS
import base64
import os
import random
import plotly.graph_objects as go
from pyresparser import ResumeParser
import tempfile

st.set_page_config(page_title="Interview Practice Partner", page_icon="🎤", layout="wide")

questions = {
    "HR": [
        "Tell me about yourself",
        "Why should we hire you?",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?"
    ],
    "Technical": [
        "Explain OOP concepts",
        "What is REST API?",
        "What is multithreading in Java?",
        "Explain SDLC phases"
    ],
    "Managerial": [
        "Tell me about a conflict you solved",
        "How do you manage deadlines?",
        "Describe a leadership experience",
        "How do you handle team pressure?"
    ]
}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "score" not in st.session_state:
    st.session_state.score = []

mode = st.sidebar.selectbox("Choose Interview Mode", ["HR", "Technical", "Managerial"])
st.title("🎤 AI Interview Practice Partner")
st.write("Chat + Voice answering enabled")

question = random.choice(questions[mode])
st.subheader("Interview Question")
st.write(question)

def tts_speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("reply.mp3")
    audio_file = open("reply.mp3", "rb").read()
    b64 = base64.b64encode(audio_file).decode()
    st.audio(f"data:audio/mp3;base64,{b64}", format="audio/mp3")

def evaluate(answer):
    score = random.randint(6, 10)
    st.session_state.score.append(score)
    return score

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        return frame

st.subheader("Voice Answer Input")
webrtc_streamer(key="voice", audio_processor_factory=AudioProcessor, media_stream_constraints={"audio": True, "video": False})

r = sr.Recognizer()

def convert_speech_to_text():
    with sr.Microphone() as source:
        audio_data = r.listen(source)
        return r.recognize_google(audio_data)

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙 Record Answer"):
        try:
            text = convert_speech_to_text()
            st.session_state.chat_history.append(("User", text))
            score = evaluate(text)
            st.session_state.chat_history.append(("AI", f"Good response. Score: {score}/10"))
            tts_speak(f"Thank you for your answer. Your score is {score} out of 10.")
        except:
            st.error("Voice not captured. Try again.")

with col2:
    typed_answer = st.text_input("Or type your answer here")
    if st.button("Send"):
        st.session_state.chat_history.append(("User", typed_answer))
        score = evaluate(typed_answer)
        st.session_state.chat_history.append(("AI", f"Scored {score}/10"))
        tts_speak(f"Your typed response score is {score} out of 10.")

st.subheader("Chat History")
for role, msg in st.session_state.chat_history:
    st.chat_message("assistant" if role=="AI" else "user").write(msg)

st.subheader("Score Graph")
if st.session_state.score:
    fig = go.Figure(data=go.Scatter(y=st.session_state.score, mode='lines+markers'))
    st.plotly_chart(fig)

st.subheader("Upload Resume for Strength / Weakness Analysis")
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)")
if resume_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name
    data = ResumeParser(tmp_path).get_extracted_data()
    st.write("### Extracted Resume Data")
    st.json(data)
    if "skills" in data and data["skills"]:
        st.write("### Strengths")
        st.write(", ".join(data["skills"]))
        st.write("### Weaknesses")
        st.write("Add more relevant technical certifications and projects.")
