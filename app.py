import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import get_user_voice_text, play_ai_voice

st.set_page_config(page_title="AI Interview Partner", page_icon="🎤", layout="centered")

# ---------------------------
# Session State Initialization
# ---------------------------
if "engine" not in st.session_state:
    st.session_state.engine = None
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "last_question" not in st.session_state:
    st.session_state.last_question = None
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "waiting_for_answer" not in st.session_state:
    st.session_state.waiting_for_answer = False

st.title("🎤 AI Mock Interview Partner")
st.subheader("Practice interviews with voice or text.")

st.markdown("---")

# ---------------------------
# Settings
# ---------------------------
role = st.selectbox("Select Interview Role:", ["Software Engineer", "Sales", "Retail Associate"])
persona = st.selectbox("Choose Interviewer Persona:", ["Default", "Efficient", "Confused", "Chatty", "Edge"])
q_count = st.slider("Number of Questions:", 1, 5, 3)

start_btn = st.button("Start Interview")

# ---------------------------
# Start Interview
# ---------------------------
if start_btn:
    st.session_state.engine = InterviewEngine(role, persona, q_count)
    st.session_state.engine.start()
    q = st.session_state.engine.ask_question()
    st.session_state.last_question = q
    st.session_state.waiting_for_answer = True
    st.session_state.interview_started = True

    st.write("### Interviewer:")
    st.info(q)

# ---------------------------
# Main Interview Loop
# ---------------------------
if st.session_state.interview_started and st.session_state.waiting_for_answer:

    st.markdown("### Your Answer")

    # ==== OPTION 1: Voice answer ====
    st.write("🎙️ Record & upload your answer:")
    voice_text = get_user_voice_text()

    # Display converted text if voice was uploaded
    if voice_text:
        st.success(f"Transcribed Text: {voice_text}")

    # ==== OPTION 2: Text answer ====
    manual_text = st.text_area("Or type your answer here:")

    # ---------------------------
    # Submit Answer
    # ---------------------------
    if st.button("Submit Answer"):
        user_answer = None
        if voice_text and voice_text.strip():
            user_answer = voice_text
        elif manual_text and manual_text.strip():
            user_answer = manual_text

        if not user_answer:
            st.error("Please provide either a voice or text answer.")
        else:
            result = st.session_state.engine.process_user_answer(user_answer)
            st.session_state.transcript = st.session_state.engine.get_transcript()

            st.write("### Interviewer Response:")

            if result["action"] == "followup":
                st.warning(result["followup"])
                play_ai_voice(result["followup"])
                st.session_state.waiting_for_answer = True

            elif result["action"] == "next":
                st.info(result["next_question"])
                play_ai_voice(result["next_question"])
                st.session_state.last_question = result["next_question"]
                st.session_state.waiting_for_answer = True

            else:
                st.success("Interview finished!")
                play_ai_voice("The interview has concluded. Thank you for participating!")
                st.session_state.waiting_for_answer = False

# ---------------------------
# FEEDBACK SECTION
# ---------------------------
st.markdown("---")
st.header("📊 Interview Feedback")

if st.button("Generate Feedback Report"):
    if not st.session_state.transcript:
        st.error("No transcript available yet.")
    else:
        report = analyze_interview(st.session_state.transcript)

        st.subheader("Scores")
        st.write(f"**Communication:** {report['communication']} / 5")
        st.write(f"**Technical Depth:** {report['technical']} / 5")
        st.write(f"**Examples/STAR Usage:** {report['examples']} / 5")
        st.write(f"### 🏆 Composite Score: **{report['composite']} / 5**")

        st.markdown("### Suggestions")
        for s in report["suggestions"]:
            st.write(f"- {s}")

        st.markdown("### Meta")
        st.json(report["meta"])
