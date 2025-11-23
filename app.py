# app.py
import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
import json
import os

st.set_page_config(page_title="Interview Practice Partner (Local)", layout="centered")

# Sidebar controls
st.sidebar.title("Settings")
role = st.sidebar.selectbox("Role", ["Software Engineer", "Sales", "Retail Associate"])
persona = st.sidebar.selectbox("Persona (test scenarios)", ["Default", "Confused", "Efficient", "Chatty", "Edge"])
question_count = st.sidebar.slider("Number of questions", min_value=1, max_value=6, value=3)
st.sidebar.markdown("---")
st.sidebar.markdown("**Project ZIP (uploaded)**")
st.sidebar.caption("Path in container (for your convenience):")
st.sidebar.code("/mnt/data/Interview_practice_partner-main.zip")

st.title("Interview Practice Partner — Local (No external APIs)")

# Create engine in session state to keep across reruns
if "engine" not in st.session_state or st.session_state.get("params") != (role, persona, question_count):
    st.session_state.engine = InterviewEngine(role=role, persona=persona, question_count=question_count)
    st.session_state.engine.start()
    st.session_state.params = (role, persona, question_count)
    st.session_state.transcript = st.session_state.engine.get_transcript()

engine: InterviewEngine = st.session_state.engine

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Conversation")
    transcript = engine.get_transcript()
    # Render transcript nicely
    for ev in transcript:
        ttype = ev["type"]
        text = ev["text"]
        if ttype == "system":
            st.info(text)
        elif ttype == "agent":
            st.markdown(f"**Interviewer:** {text}")
        elif ttype == "user":
            st.markdown(f"**You:** {text}")

with col2:
    st.header("Controls")
    if st.button("Ask first / Restart interview"):
        engine = InterviewEngine(role=role, persona=persona, question_count=question_count)
        engine.start()
        st.session_state.engine = engine
        st.session_state.params = (role, persona, question_count)

    if st.button("Ask next question (force)"):
        q = engine.force_next()
        st.session_state.engine = engine

    st.markdown("---")
    st.markdown("**Quick scenarios**")
    if st.button("Load Confused scenario answers"):
        # Example short answers to provoke followups
        engine.start()
        engine.ask_question()
        engine.process_user_answer("I'm not sure. It was something with the code.")
        engine.process_user_answer("We fixed it.")
        st.session_state.engine = engine

    if st.button("Load Efficient scenario answers"):
        engine.start()
        engine.ask_question()
        engine.process_user_answer("I debugged a race condition and added a mutex. Reduced failures by 40%.")
        engine.process_user_answer("I optimized DB queries, reduced latency by 120 ms.")
        st.session_state.engine = engine

    st.markdown("---")
    if st.button("Show transcript JSON"):
        st.json(engine.get_transcript())

st.markdown("---")
st.header("Answer the current question")
current_q = None
# find last agent question
for ev in reversed(engine.get_transcript()):
    if ev["type"] == "agent":
        current_q = ev["text"]
        break

if not current_q:
    # Ask first question
    q = engine.ask_question()
    current_q = q

st.write(f"**Interviewer:** {current_q}")
answer = st.text_area("Your answer (type and press Submit)", height=150)

cola, colb, colc = st.columns(3)
with cola:
    if st.button("Submit answer"):
        if not answer.strip():
            st.warning("Please enter an answer before submitting.")
        else:
            res = engine.process_user_answer(answer.strip())
            st.session_state.engine = engine
            st.success(f"Agent action: {res.get('action')}")
with colb:
    if st.button("Request feedback now (on current transcript)"):
        report = analyze_interview(engine.get_transcript())
        st.subheader("Feedback report")
        if "error" in report:
            st.error(report["error"])
        else:
            st.metric("Composite (0-5)", report["composite"])
            st.metric("Communication (0-5)", report["communication"])
            st.metric("Technical (0-5)", report["technical"])
            st.metric("Examples (0-5)", report["examples"])
            st.markdown("**Suggestions**")
            for s in report["suggestions"]:
                st.write(f"- {s}")
            st.markdown("**Meta**")
            st.write(report["meta"])

with colc:
    if st.button("Export transcript & feedback"):
        transcript = engine.get_transcript()
        report = analyze_interview(transcript)
        out = {"transcript": transcript, "feedback": report}
        fname = "interview_session.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        with open(fname, "rb") as f:
            st.download_button("Download session JSON", data=f, file_name=fname)

st.markdown("---")
st.caption("Design notes: local rule-based followups (no external APIs). Personas change follow-up aggressiveness and tone to satisfy evaluation scenarios (Confused, Efficient, Chatty, Edge).")
