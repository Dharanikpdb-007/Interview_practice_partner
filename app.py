import streamlit as st
from interview_engine import InterviewEngine
from utils import save_transcript
from feedback import analyze_interview

st.set_page_config(page_title="Interview Practice Partner", layout="centered")
st.title("Interview Practice Partner")

# Sidebar controls
role = st.sidebar.selectbox("Role", ["Software Engineer", "Sales", "Retail Associate"])
persona = st.sidebar.selectbox("User Persona", ["Confused", "Efficient", "Chatty", "Edge Case"])
mode = st.sidebar.selectbox("Mode", ["Fallback (rule-based)", "LLM (OpenAI) - optional"])

# Initialize engine once per session
if "engine" not in st.session_state or st.session_state.get("config") != (role, persona, mode):
    st.session_state.engine = InterviewEngine(role=role, persona=persona, mode=mode)
    st.session_state["config"] = (role, persona, mode)

engine: InterviewEngine = st.session_state.engine

# Layout
col1, col2 = st.columns([3,1])

with col1:
    st.subheader("Interview Chat")
    for ev in engine.get_events():
        if ev["type"] == "agent":
            st.markdown(f"**Interviewer**: {ev['text']}")
        else:
            st.markdown(f"**You**: {ev['text']}")

with col2:
    st.subheader("Controls")
    if st.button("Start Interview"):
        engine.start()
        st.experimental_rerun()
    if st.button("Next Question"):
        engine.force_next()
        st.experimental_rerun()
    if st.button("End Interview & Get Feedback"):
        transcript = engine.get_transcript()
        save_transcript(transcript, path="transcript.json")
        feedback = analyze_interview(transcript)
        st.session_state["last_feedback"] = feedback
        st.experimental_rerun()

# Input box for user's answer
user_input = st.text_input("Your answer (press Enter to send)")
if user_input:
    engine.add_user_response(user_input)
    st.experimental_rerun()

# Show feedback if available
if st.session_state.get("last_feedback"):
    st.subheader("Feedback Report")
    fb = st.session_state["last_feedback"]
    st.write(f"Communication score: {fb['communication']} / 5")
    st.write(f"Technical score: {fb['technical']} / 5")
    st.write(f"Examples score: {fb['examples']} / 5")
    st.write("Suggestions:")
    for s in fb["suggestions"]:
        st.write(f"- {s}")
