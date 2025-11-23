import streamlit as st
from gtts import gTTS
import base64
import io
import random
import plotly.graph_objects as go
from typing import List, Dict
import re
import PyPDF2

st.set_page_config(page_title="Interview Practice Partner", layout="wide")

QUESTIONS = {
    "Software Engineer": {
        "intro": ["Tell me about yourself.", "Walk me through your recent project."],
        "technical": ["Explain OOP concepts with an example.", "How do you debug a production issue?"],
        "behavioral": ["Tell me about a challenging bug you fixed.", "Describe a time you missed a deadline and what you learned."]
    },
    "HR": {
        "intro": ["Introduce yourself for an HR role."],
        "technical": ["How would you design a recruitment process for a new role?"],
        "behavioral": ["Describe a time you resolved a conflict at work."]
    },
    "Sales": {
        "intro": ["Introduce yourself for a Sales role."],
        "technical": ["Explain your approach to handling objections."],
        "behavioral": ["Tell me about a successful pitch you delivered."]
    },
    "Data Analyst": {
        "intro": ["Introduce yourself for a Data Analyst role."],
        "technical": ["Explain a data project where you cleaned messy data."],
        "behavioral": ["Describe a time your analysis changed a business decision."]
    }
}

def tts_play(text: str):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    st.audio(f"data:audio/mp3;base64,{b64}", format="audio/mp3")

def simple_resume_analysis(file_bytes: bytes):
    text = ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception:
        try:
            text = file_bytes.decode(errors='ignore')
        except Exception:
            text = ""
    skills = []
    common_skills = ['python','java','sql','javascript','communication','leadership','excel','aws','docker','kubernetes','ml','machine learning','data analysis','react']
    low = text.lower()
    for s in common_skills:
        if s in low and s not in skills:
            skills.append(s)
    strengths = skills[:5]
    weaknesses = []
    if 'python' not in skills:
        weaknesses.append('Add Python projects or skills')
    if 'sql' not in skills:
        weaknesses.append('Show SQL or data querying experience')
    return {'text': text[:2000], 'skills': strengths, 'weaknesses': weaknesses}

def analyze_interview(transcript: List[Dict]) -> Dict:
    answers = [ev.get("text","") for ev in transcript if ev.get("type")=="user"]
    communication_score = 0.0
    technical_score = 0.0
    examples_score = 0.0
    for a in answers:
        word_count = len(a.split())
        if word_count > 80:
            communication_score += 4.5
        elif word_count > 40:
            communication_score += 4.0
        elif word_count > 20:
            communication_score += 3.0
        else:
            communication_score += 2.0
        tech_keywords = ["design", "algorithm", "data structure", "debug", "performance", "latency", "optimization", "complexity"]
        if any(k in a.lower() for k in tech_keywords):
            technical_score += 4.0
        else:
            technical_score += 2.0
        if re.search(r'\b(\d+%|\d+ improvement|improved by|reduced by|increased by|resulted in|achieved)\b', a.lower()):
            examples_score += 4.0
        else:
            examples_score += 2.0
    n = max(1, len(answers))
    report = {
        'communication': round(min(5.0, communication_score / n), 2),
        'technical': round(min(5.0, technical_score / n), 2),
        'examples': round(min(5.0, examples_score / n), 2),
        'suggestions': []
    }
    if report['communication'] < 3.5:
        report['suggestions'].append('Structure your answers using STAR: Situation, Task, Action, Result.')
    if report['technical'] < 3.0:
        report['suggestions'].append('Add more technical depth: mention specific algorithms, tradeoffs, or complexity.')
    if report['examples'] < 3.0:
        report['suggestions'].append('Use measurable outcomes and quantify results where possible.')
    report['suggestions'].append('Practice with different personas: confused, efficient, chatty, edge-case.')
    return report

if "engine" not in st.session_state:
    st.session_state.engine = {"transcript": [], "current_question": None}
st.title("Interview Practice Partner")
col1, col2 = st.columns([2,1])
with col2:
    role = st.selectbox("Role", list(QUESTIONS.keys()))
    mode = st.selectbox("Interaction Mode", ["Chat", "Voice_hint"])
    difficulty = st.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"])
    if st.button("New Question"):
        section = random.choice(list(QUESTIONS[role].keys()))
        q = random.choice(QUESTIONS[role][section])
        st.session_state.engine["current_question"] = {"text": q, "section": section}
        st.session_state.engine["transcript"].append({"type":"agent","text":q})
        tts_play(q)
with col1:
    st.subheader("Conversation")
    for e in st.session_state.engine["transcript"]:
        if e["type"]=="agent":
            st.markdown(f"**Interviewer:** {e['text']}")
        else:
            st.markdown(f"**You:** {e['text']}")
    if mode=="Chat":
        ans = st.text_area("Your answer", key="answer_box", height=120)
        if st.button("Submit Answer"):
            if ans.strip():
                st.session_state.engine["transcript"].append({"type":"user","text":ans})
                st.success("Answer recorded")
    else:
        st.info("Voice hint mode: type short answer or paste a transcript of your spoken answer")
        ans2 = st.text_area("Paste your transcribed answer here", key="answer_box_voice", height=120)
        if st.button("Submit Voice Answer"):
            if ans2.strip():
                st.session_state.engine["transcript"].append({"type":"user","text":ans2})
                st.success("Voice answer recorded")
st.write("---")
if st.button("Get Feedback & Scores"):
    report = analyze_interview(st.session_state.engine["transcript"])
    st.write("### Scores")
    st.write(f"Communication: {report['communication']} / 5")
    st.write(f"Technical: {report['technical']} / 5")
    st.write(f"Examples: {report['examples']} / 5")
    st.write("### Suggestions")
    for s in report["suggestions"]:
        st.write("-", s)
    scores = [report['communication'], report['technical'], report['examples']]
    fig = go.Figure(data=go.Bar(y=scores, x=["Communication","Technical","Examples"]))
    st.plotly_chart(fig)
st.write("---")
st.subheader("Upload Resume (PDF) for quick analysis")
res = st.file_uploader("Upload PDF or TXT", type=["pdf","txt"])
if res:
    data = simple_resume_analysis(res.read())
    st.write("### Extracted Skills")
    st.write(", ".join(data['skills']) if data['skills'] else "No common skills detected")
    st.write("### Quick Weakness Hints")
    for w in data['weaknesses']:
        st.write("-", w)
    st.write("### Resume Preview (first 2000 chars)")
    st.code(data['text'][:1000])
