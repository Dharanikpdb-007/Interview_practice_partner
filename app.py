# app.py
import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from utils import save_transcript

# Optional import - only used if user uploads audio and wants transcription
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except Exception:
    SPEECH_RECOGNITION_AVAILABLE = False

st.set_page_config(page_title="AI Interview Partner", layout="wide")

# --- Session state initialization ---
if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "chat" not in st.session_state:
    st.session_state.chat = []  # list of tuples: (role, text)

if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --- Sidebar: Persona / Role selection & controls ---
st.sidebar.header("Interview Settings")
role = st.sidebar.selectbox(
    "Choose Role / Persona",
    options=st.session_state.engine.available_roles(),
    index=0
)
mode = st.sidebar.radio("Interaction Mode", ["Text (default)", "Audio Upload (optional)"])
st.sidebar.markdown("---")
if st.sidebar.button("Start New Interview"):
    st.session_state.engine.reset(role=role)
    st.session_state.chat = []
    st.session_state.current_question = st.session_state.engine.next_question()
    if st.session_state.current_question:
        st.session_state.chat.append(("AI", st.session_state.current_question))

# --- Main UI ---
st.title("AI Interview Partner — Demo")
st.write(
    "Use text input to answer the current question. Optionally upload an audio file to be transcribed (wav/mp3). "
    "Press 'Next' to continue, 'Force Next' to skip, or 'Get Feedback' when done."
)

# Show the current question
if st.session_state.current_question:
    st.markdown(f"### **Question:** {st.session_state.current_question}")
else:
    st.info("No active question. Start a new interview from the sidebar.")

# Optionally accept an audio file and transcribe
uploaded_audio = st.file_uploader("Upload audio answer (optional - wav/mp3)", type=["wav", "mp3", "m4a"])

transcribed_text = None
if uploaded_audio is not None:
    st.info("Received audio file. Attempting transcription...")
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.warning("speech_recognition package not available. Please install it to enable transcription.")
    else:
        r = sr.Recognizer()
        # Save to temp file
        import tempfile, io
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name
        try:
            with sr.AudioFile(tmp_path) as source:
                audio_data = r.record(source)
            # This uses Google's free web API (needs internet) - catches exceptions
            transcribed_text = r.recognize_google(audio_data)
            st.success("Transcription successful.")
            st.write("**Transcribed text:**", transcribed_text)
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            transcribed_text = None

# Text answer input (always available)
answer_input = st.text_area("Type your answer here (or paste transcription)", value=(transcribed_text or ""), key="answer_input", height=150)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Submit Answer"):
        if not answer_input.strip():
            st.warning("Please type an answer (or upload audio to transcribe).")
        else:
            st.session_state.chat.append(("You", answer_input.strip()))
            # Provide follow-up question / agent reaction via engine
            reply = st.session_state.engine.process_answer_and_get_reply(answer_input.strip())
            if reply:
                st.session_state.chat.append(("AI", reply))
                st.session_state.current_question = reply
            else:
                # If engine indicates done or returns None, move to next question
                q = st.session_state.engine.next_question()
                if q:
                    st.session_state.chat.append(("AI", q))
                    st.session_state.current_question = q
                else:
                    st.session_state.current_question = None

with col2:
    if st.button("Force Next Question"):
        q = st.session_state.engine.force_next()
        if q:
            st.session_state.chat.append(("AI", q))
            st.session_state.current_question = q
        else:
            st.session_state.current_question = None

with col3:
    if st.button("Get Feedback"):
        # Build transcript expected by feedback.analyze_interview
        transcript = [{"type": "user" if role_ == "You" or role_ == "User" or role_ == "You" else "agent",
                       "text": txt}
                      for role_, txt in st.session_state.chat]
        report = analyze_interview(transcript)
        st.subheader("Feedback Report")
        st.json(report)
        # Save transcript for your records
        path = save_transcript(transcript, path="transcript.json")
        st.info(f"Transcript saved to {path}")

# Conversation display
st.subheader("Conversation")
for role_, message in st.session_state.chat:
    if role_ == "AI":
        st.markdown(f"**{role_}:** {message}")
    else:
        st.markdown(f"**{role_}:** {message}")

# Helpful debugging / dev info (only show when we are in debug)
if st.checkbox("Show engine state (debug)"):
    st.json({
        "engine_state": st.session_state.engine.get_state_for_debug(),
        "current_question": st.session_state.current_question
    })
