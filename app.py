import streamlit as st
import openai
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile

openai.api_key = st.secrets["OPENAI_API_KEY"]

INITIAL_QUESTION = "Tell me about yourself."

def speak_text(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio = AudioSegment.from_mp3(fp.name)
        play(audio)

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "Could not understand audio"

def generate_next_question(answer):
    prompt = f"""
    You are an HR interviewer. The candidate answered: "{answer}".
    Give a short response and then ask the next question.
    Format:
    FEEDBACK:
    QUESTION:
    """
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message["content"]

st.set_page_config(page_title="Interview Practice Partner")

st.title("AI Interview Practice Partner")

if "current_question" not in st.session_state:
    st.session_state.current_question = INITIAL_QUESTION

st.subheader("Interview Question")
st.write(st.session_state.current_question)

if st.button("Play Question"):
    speak_text(st.session_state.current_question)

if st.button("Record Answer"):
    user_answer = listen_and_transcribe()
    st.write("Your Answer:")
    st.write(user_answer)

    if user_answer:
        response = generate_next_question(user_answer)
        st.write("AI Response")
        st.write(response)

        if "QUESTION:" in response:
            next_q = response.split("QUESTION:")[-1].strip()
            st.session_state.current_question = next_q
            speak_text(next_q)
