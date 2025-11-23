import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import get_user_voice_text, play_ai_voice


# ---------------------------
# Initialize Session State
# ---------------------------
def init_state():
    if "engine" not in st.session_state:
        st.session_state.engine = InterviewEngine()

    if "transcript" not in st.session_state:
        st.session_state.transcript = []

    if "started" not in st.session_state:
        st.session_state.started = False


init_state()


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Interview Practice Partner", layout="wide")
st.title("🎯 Interview Practice Partner (Voice Enabled)")
st.write("Mock interview with voice input/output. 100% local, no API.")


# ---------------------------
# Select Role + Persona Before Start
# ---------------------------
if not st.session_state.started:
    col1, col2 = st.columns(2)

    with col1:
        role = st.selectbox(
            "Select a job role:",
            ["Software Engineer", "Sales", "Retail Associate"],
            key="role_selector",
        )

    with col2:
        persona = st.selectbox(
            "Select interviewer persona:",
            ["Default", "Confused", "Efficient", "Chatty", "Edge"],
            key="persona_selector",
        )

    if st.button("Start Interview"):
        st.session_state.engine = InterviewEngine(
            role=role,
            persona=persona,
            question_count=3,
        )
        st.session_state.started = True

        first_q = st.session_state.engine.ask_question()
        st.session_state.transcript.append({"type": "agent", "text": first_q})
        play_ai_voice(first_q)
        st.experimental_rerun()


# ---------------------------
# Only show interview UI after start
# ---------------------------
if st.session_state.started:
    st.markdown("---")
    st.subheader("🎤 Speak or Type Your Answer")

    # Voice Input
    voice_col, text_col = st.columns(2)

    with voice_col:
        st.write("🎤 **Voice Input**")
        user_voice_text = get_user_voice_text()

    # Typed Input
    with text_col:
        st.write("⌨️ **Text Input**")
        user_typed_text = st.text_area(
            "Type your answer here...", key="typed_answer"
        )

    # Determine active input
    user_input = user_voice_text if user_voice_text else user_typed_text.strip()

    if st.button("Submit Answer"):
        if not user_input:
            st.warning("Please speak or type your answer.")
        else:
            # Record user answer
            st.session_state.transcript.append(
                {"type": "user", "text": user_input}
            )

            # Process with engine
            response = st.session_state.engine.process_user_answer(user_input)

            if response["action"] == "followup":
                fup = response["followup"]
                st.session_state.transcript.append(
                    {"type": "agent", "text": fup}
                )
                st.write("### 🤖 Follow-up:")
                st.write(fup)
                play_ai_voice(fup)
