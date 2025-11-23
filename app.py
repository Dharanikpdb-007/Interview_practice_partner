import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import get_user_voice_text, play_ai_voice

st.set_page_config(page_title="AI Interview Partner", layout="wide")
st.title("🎙 AI Interview Practice Partner (Live Voice, Browser-based)")

# ---------------------------
# Session state init
# ---------------------------
if "engine" not in st.session_state:
    st.session_state.engine = None
if "started" not in st.session_state:
    st.session_state.started = False
if "transcript" not in st.session_state:
    st.session_state.transcript = []  # list of {"type": "agent"|"user"|"system", "text": "..."}
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# ---------------------------
# Controls: role / persona / qcount
# ---------------------------
col1, col2, col3 = st.columns(3)
with col1:
    role = st.selectbox("Role", ["Software Engineer", "Sales", "Retail Associate"], index=0)
with col2:
    persona = st.selectbox("Persona", ["Default", "Confused", "Efficient", "Chatty", "Edge"], index=0)
with col3:
    q_count = st.slider("Number of questions", 1, 6, 3)

start = st.button("Start / Restart Interview")

# ---------------------------
# Start interview
# ---------------------------
if start:
    st.session_state.engine = InterviewEngine(role=role, persona=persona, question_count=q_count)
    st.session_state.engine.start()
    first_q = st.session_state.engine.ask_question()
    st.session_state.transcript = st.session_state.engine.get_transcript()
    st.session_state.started = True
    st.session_state.current_question = first_q
    # Play the question
    play_ai_voice(first_q)

st.markdown("---")

# ---------------------------
# If interview active, show current question and accept answer
# ---------------------------
if st.session_state.started and st.session_state.engine:
    st.subheader("Conversation")
    # render transcript
    for ev in st.session_state.transcript:
        if ev["type"] == "system":
            st.info(ev["text"])
        elif ev["type"] == "agent":
            st.markdown(f"**Interviewer:** {ev['text']}")
        elif ev["type"] == "user":
            st.markdown(f"**You:** {ev['text']}")

    st.markdown("---")
    st.subheader("Answer the current question (speak or type)")

    # show the active agent question (last agent item)
    current_q = None
    for ev in reversed(st.session_state.transcript):
        if ev["type"] == "agent":
            current_q = ev["text"]
            break
    if current_q:
        st.write(f"**Interviewer:** {current_q}")
    else:
        st.write("No question available. Click Start to begin.")

    # Live voice capture (browser-side)
    voice_text = get_user_voice_text()
    if voice_text:
        st.success(f"Captured text: {voice_text}")

    typed = st.text_area("Or type your answer here (overrides voice if non-empty):", key="typed_answer", height=120)

    submit = st.button("Submit Answer")

    if submit:
        answer = None
        if typed and typed.strip():
            answer = typed.strip()
        elif voice_text and voice_text.strip():
            answer = voice_text.strip()

        if not answer:
            st.warning("Please speak or type an answer before submitting.")
        else:
            # feed to engine
            res = st.session_state.engine.process_user_answer(answer)
            # update transcript from engine (engine already appends user & agent events)
            st.session_state.transcript = st.session_state.engine.get_transcript()

            # handle action
            action = res.get("action")
            if action == "followup":
                fup = res.get("followup")
                st.info("Interviewer (follow-up):")
                st.write(fup)
                play_ai_voice(fup)
            elif action == "next":
                next_q = res.get("next_question")
                st.info("Interviewer (next question):")
                st.write(next_q)
                play_ai_voice(next_q)
            elif action == "done":
                done_msg = "That concludes the mock interview. Thank you!"
                st.success(done_msg)
                play_ai_voice(done_msg)

# ---------------------------
# Feedback and export
# ---------------------------
st.markdown("---")
st.header("Feedback & Export")

if st.button("Generate Feedback"):
    if not st.session_state.transcript:
        st.error("No transcript available. Run an interview first.")
    else:
        report = analyze_interview(st.session_state.transcript)
        st.subheader("Feedback Report")
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
            st.json(report["meta"])

if st.button("Export transcript as JSON"):
    import json, io
    if not st.session_state.transcript:
        st.error("No transcript to export.")
    else:
        out = {"transcript": st.session_state.transcript}
        buf = io.StringIO()
        json.dump(out, buf, indent=2)
        st.download_button("Download JSON", data=buf.getvalue(), file_name="interview_transcript.json", mime="application/json")
