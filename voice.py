import streamlit as st

# --------------------------
# Browser Speech Recognition (JS)
# --------------------------
_JS_START = """
<script>
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
  document.write("<div style='color:darkred'>⚠️ Your browser does not support the Web Speech API. Use Chrome or Edge for live speech.</div>");
}
const recognition = new SpeechRecognition();
recognition.interimResults = false;
recognition.lang = "en-US";

function startRecordingStreamlit() {
  recognition.start();
  const status = document.getElementById("voice_status");
  if (status) status.innerText = "🎤 Listening...";
}

recognition.onresult = function(event) {
  const text = event.results[0][0].transcript;
  const el = document.getElementById("user_voice_input");
  if (el) {
    el.value = text;
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }
  const status = document.getElementById("voice_status");
  if (status) status.innerText = "✔ Captured!";
};

recognition.onerror = function(event) {
  const status = document.getElementById("voice_status");
  if (status) status.innerText = "⚠ Error capturing voice: " + (event.error || "unknown");
};
</script>
"""

def get_user_voice_text():
    """
    Renders a Speak button that uses the browser's Web Speech API and returns
    recognized text via a hidden Streamlit text_input (automatically populated).
    """
    st.markdown(_JS_START, unsafe_allow_html=True)
    # show button (JS function startRecordingStreamlit defined above)
    st.markdown("""
      <button onclick="startRecordingStreamlit()" style="
            background:#4CAF50; color:white; padding:10px; border-radius:8px;
            border:none; cursor:pointer; margin-top:6px;">
        🎤 Speak Now
      </button>
      <span id="voice_status" style="margin-left:12px">Click to speak</span>
    """, unsafe_allow_html=True)

    # a hidden text input that JS will populate
    text = st.text_input("Captured voice (auto-filled)", key="user_voice_input")
    # return text only if non-empty (otherwise None)
    return text if text and text.strip() else None


# --------------------------
# Browser TTS for AI reply
# --------------------------
def play_ai_voice(text: str):
    """
    Uses browser SpeechSynthesis to speak the given text.
    """
    if not text:
        return
    safe = text.replace('"', '\\"').replace("\n", " ")
    script = f"""
    <script>
    const msg = new SpeechSynthesisUtterance("{safe}");
    msg.lang = "en-US";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(script, unsafe_allow_html=True)
