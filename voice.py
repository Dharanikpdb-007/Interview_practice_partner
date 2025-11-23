import streamlit as st
import base64
import uuid

# -------------------------------------
# BROWSER SPEECH RECOGNITION (JS BASED)
# -------------------------------------

def get_user_voice_text():
    st.markdown("""
        <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        function startRecording() {
            recognition.start();
            document.getElementById("voice_status").innerText = "🎤 Listening...";
        }

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            const streamlitInput = document.getElementById("user_voice_input");
            streamlitInput.value = text;
            streamlitInput.dispatchEvent(new Event("input", { bubbles: true }));
            document.getElementById("voice_status").innerText = "✔ Captured!";
        }
        recognition.onerror = function() {
            document.getElementById("voice_status").innerText = "⚠ Error capturing voice.";
        }
        </script>

        <button onclick="startRecording()" style="
            background:#4CAF50; color:white; padding:10px; border-radius:8px;
            border:none; cursor:pointer; margin-top:10px;">
            🎤 Speak Now
        </button>
        <p id="voice_status"></p>
    """, unsafe_allow_html=True)

    text = st.text_input("Captured Voice Input:", key="user_voice_input")
    return text


# -------------------------------------
# AI SPEAKS (TTS USING BROWSER SPEECH)
# -------------------------------------

def play_ai_voice(text):
    escaped = text.replace('"', '\\"')

    st.markdown(f"""
        <script>
        const msg = new SpeechSynthesisUtterance("{escaped}");
        msg.lang = "en-US";
        window.speechSynthesis.speak(msg);
        </script>
    """, unsafe_allow_html=True)
