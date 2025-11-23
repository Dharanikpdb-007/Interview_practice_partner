import av
import queue
import threading
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
from gtts import gTTS

recognizer = sr.Recognizer()
audio_queue = queue.Queue()

# Capture audio frames
def audio_callback(frame):
    audio = frame.to_ndarray().flatten()
    audio_queue.put(audio)
    return frame


def listen_live_audio():
    """
    Takes live audio chunks from queue → converts to WAV → sends to Google STT.
    """
    wav_path = "live_audio.wav"

    # Collect ~2 seconds of audio
    import numpy as np
    data = []

    try:
        for _ in range(30):  # small chunks
            data.append(audio_queue.get(timeout=1))
    except:
        pass

    if not data:
        return None

    audio_data = np.concatenate(data).astype("int16")

    # Write WAV file
    import wave
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data.tobytes())

    # Speech Recognition
    try:
        with sr.AudioFile(wav_path) as src:
            audio = recognizer.record(src)
            text = recognizer.recognize_google(audio)
            return text
    except:
        return "Sorry, I couldn't understand the audio."


def get_user_voice_text():
    """
    Starts the live mic widget and listens for speech.
    """
    webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        client_settings=ClientSettings(
            media_stream_constraints={"audio": True, "video": False}
        ),
        audio_frame_callback=audio_callback,
    )

    st.write("🎤 Speak now, then click the button below:")

    if st.button("Transcribe Speech"):
        return listen_live_audio()

    return None


def play_ai_voice(text):
    """
    Convert AI text → spoken voice via gTTS and play.
    """
    path = "ai_response.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(path)

    with open(path, "rb") as f:
        st.audio(f.read(), format="audio/mp3")
