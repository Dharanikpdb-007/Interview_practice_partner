 Interview Practice Partner - Cloud Friendly

 What this project provides
- Voice-enabled interviewer (agent speaks questions using gTTS via browser audio)
- Text answer input (reliable on Streamlit Cloud)
- Simple scoring and feedback (communication, technical, examples)
- Quick resume scan (PDF) with extracted skills and weakness hints
- Multiple roles and difficulty levels
 How to run locally
1. pip install -r requirements.txt
2. streamlit run app.py

 Notes
- This version avoids heavy NLP packages so it deploys reliably on Streamlit Cloud.
- For voice input in browser you can paste a transcript into 'Voice_hint' mode or integrate streamlit-webrtc later.
