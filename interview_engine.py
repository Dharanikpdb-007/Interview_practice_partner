import random
from typing import List, Dict
import os
from dotenv import load_dotenv
import openai


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  

QUESTION_BANK = {
    "Software Engineer": [
        {"id": "se1", "q": "Tell me about a challenging bug you fixed.", "type": "behavioral"},
        {"id": "se2", "q": "Explain a project where you used data structures to improve performance.", "type": "technical"},
        {"id": "se3", "q": "How do you approach debugging a production issue?", "type": "technical"},
    ],
    "Sales": [
        {"id": "sales1", "q": "How would you handle an objection about price?", "type": "roleplay"},
        {"id": "sales2", "q": "Sell me this pen.", "type": "roleplay"},
    ],
    "Retail Associate": [
        {"id": "ret1", "q": "Describe a time you handled an upset customer.", "type": "behavioral"},
        {"id": "ret2", "q": "How do you prioritize tasks during a busy shift?", "type": "behavioral"},
    ],
}

FALLBACK_FOLLOWUPS = [
    "Can you give one concrete example?",
    "What were the steps you took and what was the outcome?",
    "Can you explain your thinking more technically?",
    "What metrics or results did you achieve?",
]

class InterviewEngine:
    def __init__(self, role="Software Engineer", persona="Efficient", mode="Fallback (rule-based)"):
        self.role = role
        self.persona = persona
        self.mode = mode
        self.events = []
        self.current_question = 0
        self.questions = self.load_questions()

    def load_questions(self):
      
        return [q["q"] for q in QUESTION_BANK.get(self.role, [])] or [
            "Tell me about yourself.",
            "Why do you want this job?",
            "What is your biggest strength?",
            "What is your biggest weakness?"
        ]

    def start(self):
        self.events = []
        self.current_question = 0
        self.ask_question()

    def get_events(self):
        return self.events

    def add_user_response(self, text):
        self.events.append({"type": "user", "text": text})
        if self.mode.startswith("LLM") and openai.api_key:
            self.add_agent_response_llm()
        else:
            self.add_agent_response_fallback()

    def add_agent_response_fallback(self):
       
        if self.current_question < len(self.questions):
            response = "Thank you for your answer."
            self.events.append({"type": "agent", "text": response})
            self.current_question += 1

    def add_agent_response_llm(self):
        
        if self.current_question < len(self.questions):
            prompt = (
                f"You are an interviewer. Role: {self.role}, Persona: {self.persona}.\n"
                f"User answered: {self.events[-1]['text']}\n"
                f"Generate a follow-up question or a comment for the user."
            )
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful interviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                text = response.choices[0].message.content
            except Exception as e:
                text = f"LLM Error: {str(e)}"

            self.events.append({"type": "agent", "text": text})
            self.current_question += 1

    def ask_question(self):
        if self.current_question < len(self.questions):
            self.events.append({"type": "agent", "text": self.questions[self.current_question]})

    def force_next(self):
        self.current_question += 1
        self.ask_question()

    def get_transcript(self):
        return self.events
