import streamlit as st
import base64
import json

# -------------------------------------------------------------------
# USER VOICE CAPTURE USING BROWSER MediaRecorder (Option B)
# -------------------------------------------------------------------

def record_user_audio():
    st.markdown("""
        <script>
        let mediaRecorder;
        let audioChunks = [];

        async function startRecording() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                audioChunks = [];

                const reader = new FileReader();
                reader.onload = () => {
                    const base64Data = reader.result.split(',')[1];
                    const input = document.getElementById("audio_input_streamlit");
                    input.value = base64Data;
                    input.dispatchEvent(new Event("input", { bubbles: true }));
                };
                reader.readAsDataURL(audioBlob);
            };

            mediaRecorder.start();
            document.getElementById("rec_status").innerText = "🎤 Recording...";
        }

        function stopRecording() {
            mediaRecorder.stop();
            document.getElementById("rec_status").innerText = "⏹ Stopped";
        }
        </script>

        <button onclick="startRecording()" style="
            background:#0099ff; color:white; padding:10px; border:none;
            border-radius:8px; cursor:pointer;">
            🎙 Hold to Speak
        </button>

        <button onclick="stopRecording()" style="
            background:#ff5555; color:white; padding:10px; border:none;
            border-radius:8px; cursor:pointer; margin-left:10px;">
            ⏹ Stop
        </button>

        <p id="rec_status"></p>

    """, unsafe_allow_html=True)

    audio_base64 = st.text_input("", key="audio_input_streamlit")
    return audio_base64


# -------------------------------------------------------------------
# AI VOICE USING Browser SpeechSynthesis
# -------------------------------------------------------------------

def play_ai_voice(text: str):
    safe = text.replace('"', '\\"')
    st.markdown(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{safe}");
            msg.lang = "en-US";
            msg.pitch = 1;
            msg.rate = 1;
            window.speechSynthesis.speak(msg);
        </script>
    """, unsafe_allow_html=True)
