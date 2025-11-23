# app.py

import streamlit as st
from interview_engine import InterviewEngine

st.set_page_config(page_title="Interview Practice Partner", layout="centered")

# Initialize engine
if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

st.title("🎤 AI Interview Practice Partner")

# Select Role
st.subheader("1. Choose interview role")

options = st.session_state.engine.available_roles()

role = st.selectbox("Select a role:", options)

# Ask Question Section
if st.button("Start Interview Question"):
    question = st.session_state.engine.ask_question(role)
    st.session_state.current_question = question
    st.write(f"**Interview Question:** {question}")

# User Answer Input
if "current_question" in st.session_state:
    answer = st.text_area("Your Answer:")

    if st.button("Submit Answer"):
        feedback = st.session_state.engine.evaluate_answer(answer)
        st.write("### Feedback")
        st.success(feedback)
