import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from utils import save_transcript
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import av
import base64
import numpy as np

st.set_page_config(page_title="Interview Practice Partner", layout="centered")

if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "mode" not in st.session_state:
    st.session_state.mode = "Chat"

engine = st.session_state.engine

st.title("Interview Practice Partner")
st.subheader("AI Mock Interview with Chat & Voice Interaction")

role = st.sidebar.selectbox("Interview Role", ["Software Engineer", "HR", "Sales", "Data Analyst"])
if role != engine.role:
    st.session_state.engine = InterviewEngine(role=role)
    engine = st.session_state.engine

mode = st.sidebar.radio("Interaction Mode", ["Chat", "Voice"])

messages = engine.get_transcript()
for m in messages:
    if m["type"] == "agent":
        st.chat_message("assistant").write(m["text"])
    else:
        st.chat_message("user").write(m["text"])

def speak(text):
    st.session_state.last_audio = text

def play_audio(text):
    import gtts
    from io import BytesIO
    tts = gtts.gTTS(text)
    fp = BytesIO()
    tts.write_to_fp(fp)
    audio = fp.getvalue()
    b64 = base64.b64encode(audio).decode()
    st.markdown(f"<audio autoplay src='data:audio/mp3;base64,{b64}'></audio>", unsafe_allow_html=True)

if messages and messages[-1]["type"] == "agent":
    play_audio(messages[-1]["text"])

if mode == "Chat":
    user_input = st.chat_input("Enter response")
    if user_input:
        play_audio(user_input)
        engine.add_user_response(user_input)
        st.rerun()

else:
    recognizer = sr.Recognizer()

    def callback(frame):
        audio = frame.to_ndarray().flatten().astype(np.float32).tobytes()
        st.session_state.audio_data = audio
        return av.AudioFrame.from_ndarray(frame.to_ndarray(), layout="mono")

    webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_frame_callback=callback,
        media_stream_constraints={"audio": True, "video": False},
    )

    if st.button("Convert Speech to Text"):
        if "audio_data" in st.session_state:
            try:
                audio = sr.AudioData(st.session_state.audio_data, 16000, 2)
                text = recognizer.recognize_google(audio)
            except:
                text = ""
            if text:
                play_audio(text)
                engine.add_user_response(text)
                st.rerun()

if st.button("Next Question ➜"):
    engine.advance_question()
    st.rerun()

if st.button("Generate Feedback"):
    transcript = engine.get_transcript()
    report = analyze_interview(transcript)
    save_transcript(transcript, "transcript.json")
    st.subheader("Interview Performance Summary")
    st.metric("Communication", f"{report['communication']} / 5")
    st.metric("Structure", f"{report['structure']} / 5")
    st.metric("Technical Depth", f"{report['technical']} / 5")
    st.metric("Examples", f"{report['examples']} / 5")
    st.write("Improvement Suggestions:")
    for s in report["suggestions"]:
        st.write("-", s)
    play_audio("Feedback generated. Please review your results below.")
    st.session_state.engine = InterviewEngine(role=role)
