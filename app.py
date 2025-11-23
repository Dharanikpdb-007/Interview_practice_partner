import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from utils import save_transcript
import speech_recognition as sr
import pyttsx3

st.set_page_config(page_title="Interview Practice Partner", layout="centered")

engine_tts = pyttsx3.init()
voices = engine_tts.getProperty("voices")
engine_tts.setProperty("voice", voices[1].id)
engine_tts.setProperty("rate", 165)

def speak(text):
    engine_tts.say(text)
    engine_tts.runAndWait()

if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()
if "mode" not in st.session_state:
    st.session_state.mode = "Chat"

engine = st.session_state.engine

role = st.sidebar.selectbox("Select Interview Role", ["Software Engineer", "HR", "Sales", "Data Analyst"])
if role != engine.role:
    st.session_state.engine = InterviewEngine(role=role)
    engine = st.session_state.engine

mode = st.sidebar.radio("Interaction Mode", ["Chat", "Voice"])

st.title("Interview Practice Partner")
st.subheader("AI Mock Interview with Voice & Chat Support")

messages = engine.get_transcript()

for m in messages:
    if m["type"] == "agent":
        st.chat_message("assistant").write(m["text"])
    else:
        st.chat_message("user").write(m["text"])

if messages and messages[-1]["type"] == "agent":
    speak(messages[-1]["text"])

if mode == "Chat":
    user_input = st.chat_input("Your answer")
    if user_input:
        speak(user_input)
        engine.add_user_response(user_input)
        st.experimental_rerun()
else:
    if st.button("🎙 Speak Answer"):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, phrase_time_limit=12)
            text = recognizer.recognize_google(audio)
        except:
            text = ""
        if text:
            speak(text)
            engine.add_user_response(text)
            st.experimental_rerun()

if st.button("Next Question ➜"):
    engine.advance_question()
    st.experimental_rerun()

if st.button("Generate Feedback"):
    transcript = engine.get_transcript()
    report = analyze_interview(transcript)
    save_transcript(transcript, "transcript.json")
    st.subheader("📊 Performance Report")
    st.metric("Communication", f"{report['communication']} / 5")
    st.metric("Structure (STAR)", f"{report['structure']} / 5")
    st.metric("Technical Depth", f"{report['technical']} / 5")
    st.metric("Examples & Metrics", f"{report['examples']} / 5")
    st.write("Suggestions:")
    for s in report["suggestions"]:
        st.write("-", s)
    speak("Interview complete. Review your feedback below.")
    st.session_state.engine = InterviewEngine(role=role)
