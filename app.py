import streamlit as st
from interview_engine import InterviewEngine
from feedback import FeedbackEngine
from voice import get_user_voice_text, play_ai_voice

# ---------------------------
# Initialize Session State
# ---------------------------
if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "feedback_engine" not in st.session_state:
    st.session_state.feedback_engine = FeedbackEngine()

if "transcript" not in st.session_state:
    st.session_state.transcript = []


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Interview Practice Partner", layout="wide")
st.title("🎯 Interview Practice Partner")
st.write("Practice a real interview with voice support (offline, no API).")


# ---------------------------
# Select Job Role
# ---------------------------
role = st.selectbox(
    "Select a job role:",
    ["Software Engineer", "Data Scientist", "Product Manager"],
    key="role_selector"
)

st.session_state.engine.set_role(role)

st.markdown("---")
st.subheader("🎤 Your Answer (Speak or Type)")


# ---------------------------
# Input Options: Voice or Text
# ---------------------------
voice_col, text_col = st.columns(2)

with voice_col:
    st.write("🎤 **Voice Input**")
    user_voice_text = get_user_voice_text()

with text_col:
    st.write("⌨️ **Text Input**")
    user_typed_text = st.text_area("Type your answer here...", key="typed_input")


# ---------------------------
# Determine the actual input
# ---------------------------
user_input = None

if user_voice_text:
    user_input = user_voice_text
elif user_typed_text.strip():
    user_input = user_typed_text.strip()


# ---------------------------
# Process User Answer
# ---------------------------
if st.button("Submit Answer"):
    if not user_input:
        st.warning("Please speak or type your answer before submitting.")
    else:
        # Save in transcript
        st.session_state.transcript.append(("User", user_input))

        # AI response
        ai_reply = st.session_state.engine.get_reply(user_input)
        st.session_state.transcript.append(("AI", ai_reply))

        # Show response
        st.markdown("### 🤖 Interviewer:")
        st.write(ai_reply)

        # AI voice output
        play_ai_voice(ai_reply)


# ---------------------------
# Display Transcript
# ---------------------------
st.markdown("---")
st.subheader("📝 Conversation Transcript")

for speaker, text in st.session_state.transcript:
    if speaker == "User":
        st.markdown(f"**👤 You:** {text}")
    else:
        st.markdown(f"**🤖 AI:** {text}")


# ---------------------------
# Generate Final Feedback
# ---------------------------
if st.button("Finish Interview & Get Feedback"):
    if not st.session_state.transcript:
        st.warning("You need to answer at least one question first.")
    else:
        feedback = st.session_state.feedback_engine.generate_feedback(
            st.session_state.transcript
        )

        st.markdown("---")
        st.subheader("📊 Final Interview Feedback")
        st.write(feedback)

        play_ai_voice("Here is your final interview feedback. " + feedback)
