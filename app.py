import streamlit as st
from interview_engine import InterviewEngine
from feedback import analyze_interview
from voice import get_user_voice_text, play_ai_voice

st.set_page_config(page_title="AI Interview Partner", layout="wide")

engine = InterviewEngine()

if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_ai" not in st.session_state:
    st.session_state.last_ai = ""

st.title("🎙 AI Interview Practice Partner (Voice Enabled)")

# -------------------------------
# INTERVIEW START
# -------------------------------

if st.button("Start Interview"):
    question = engine.start_interview()
    st.session_state.last_ai = question
    st.session_state.chat.append(("AI", question))
    play_ai_voice(question)

# -------------------------------
# USER VOICE INPUT
# -------------------------------

user_text = get_user_voice_text()

if user_text:
    st.session_state.chat.append(("You", user_text))
    reply = engine.continue_interview(user_text)

    st.session_state.last_ai = reply
    st.session_state.chat.append(("AI", reply))
    play_ai_voice(reply)

# -------------------------------
# SHOW CHAT
# -------------------------------

st.subheader("Conversation")
for speaker, text in st.session_state.chat:
    if speaker == "AI":
        st.markdown(f"**🤖 AI:** {text}")
    else:
        st.markdown(f"**🧑 You:** {text}")

# -------------------------------
# FEEDBACK BUTTON
# -------------------------------

if st.button("Get Feedback"):
    feedback = analyze_interview(st.session_state.chat)
    st.write("### 📌 Final Feedback")
    st.write(feedback)
