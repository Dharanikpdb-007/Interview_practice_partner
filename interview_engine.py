import random
import re
from typing import List, Dict, Optional

QUESTION_BANK = {
    "Software Engineer": [
        {"id": "se1", "q": "Tell me about a challenging bug you fixed.", "type": "behavioral"},
        {"id": "se2", "q": "Explain a project where you used data structures to improve performance.", "type": "technical"},
        {"id": "se3", "q": "How do you approach debugging a production issue?", "type": "technical"},
        {"id": "se4", "q": "Describe a time you made a tradeoff between speed and correctness.", "type": "behavioral"},
    ],
    "Sales": [
        {"id": "sa1", "q": "Tell me about a sale you are proud of.", "type": "behavioral"},
        {"id": "sa2", "q": "How do you handle objections from a difficult prospect?", "type": "behavioral"},
        {"id": "sa3", "q": "How do you prioritize leads?", "type": "technical"},
    ],
    "Retail Associate": [
        {"id": "rt1", "q": "Describe a time you handled an unhappy customer.", "type": "behavioral"},
        {"id": "rt2", "q": "How do you balance speed vs. accuracy when working the register?", "type": "behavioral"},
    ],
}

PERSONAS = {
    "Confused": {"followup_style": "clarify", "max_followups": 3},
    "Efficient": {"followup_style": "concise", "max_followups": 1},
    "Chatty": {"followup_style": "explore", "max_followups": 4},
    "Edge": {"followup_style": "boundary", "max_followups": 2},
    "Default": {"followup_style": "balanced", "max_followups": 2},
}

METRIC_PATTERN = re.compile(r"\b\d+%|\b\d+\s*(ms|s|seconds|minutes|hours|GB|MB|gb|mb)\b")
TEAM_WORDS = {"we", "team", "our", "us"}
FIRST_PERSON = {"i", "me", "my", "mine"}

def _contains_metrics(text: str) -> bool:
    return bool(METRIC_PATTERN.search(text))

def _uses_first_person(text: str) -> bool:
    t = text.lower()
    return any(f in t.split() for f in FIRST_PERSON)

def _uses_team_words(text: str) -> bool:
    t = text.lower()
    return any(w in t.split() for w in TEAM_WORDS)

def _word_count(text: str) -> int:
    return len(text.strip().split())

def _has_action_words(text: str) -> bool:
    actions = ["built", "designed", "implemented", "reduced", "improved", "fixed", "led", "created", "optimized"]
    t = text.lower()
    return any(a in t for a in actions)

class InterviewEngine:
    def __init__(self, role: str = "Software Engineer", persona: str = "Default", question_count: int = 3):
        self.role = role if role in QUESTION_BANK else "Software Engineer"
        self.persona = persona if persona in PERSONAS else "Default"
        bank = QUESTION_BANK.get(self.role, [])
        seed = hash((self.role, self.persona)) & 0xffffffff
        rng = random.Random(seed)
        rng.shuffle(bank)
        self.questions = [q["q"] for q in bank][:question_count]
        self.q_types = [q.get("type", "behavioral") for q in bank][:question_count]
        self.current_index = 0
        self.events: List[Dict] = [{"type": "system", "text": f"Interview started for role={self.role}, persona={self.persona}"}]
        self.followup_counts = {}

    def start(self):
        self.current_index = 0
        self.events = [{"type": "system", "text": f"Interview started for role={self.role}, persona={self.persona}"}]
        self.followup_counts = {}

    def ask_question(self) -> Optional[str]:
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.events.append({"type": "agent", "text": q})
            return q
        return None

    def _heuristic_followup(self, q_text: str, answer: str, style: str) -> Optional[str]:
        wc = _word_count(answer)
        has_metrics = _contains_metrics(answer)
        has_action = _has_action_words(answer)
        uses_team = _uses_team_words(answer)
        uses_first = _uses_first_person(answer)

        if wc < 20:
            if style in ("clarify", "balanced", "explore"):
                return "Could you expand a bit — what exactly did you do and why?"
            if style == "concise":
                return "One-sentence highlight: what was your single contribution?"
        if not has_metrics and ("technical" in q_text.lower() or "data" in q_text.lower() or "performance" in q_text.lower()):
            return "Can you quantify the impact or mention performance tradeoffs (latency, throughput, complexity)?"
        if uses_team and not uses_first:
            return "You mentioned the team — what was your specific contribution?"
        if has_action and not has_metrics:
            return "What was the outcome or result of that work?"
        if style == "explore":
            return "Interesting — why did you choose that approach over alternatives?"
        if style == "boundary":
            return "That sounds related to other contexts — how does it map to this role's responsibilities?"
        return "Can you outline the steps you took and the measurable outcome?"

    def process_user_answer(self, answer_text: str) -> Dict:
        self.events.append({"type": "user", "text": answer_text})
        style = PERSONAS[self.persona]["followup_style"]
        max_fups = PERSONAS[self.persona]["max_followups"]
        idx = self.current_index
        fcount = self.followup_counts.get(idx, 0)

        ask_followup = False
        wc = _word_count(answer_text)
        if fcount < max_fups:
            if wc < 30:
                ask_followup = True
            elif not _has_action_words(answer_text):
                ask_followup = True
            elif not _contains_metrics(answer_text) and (idx < len(self.q_types) and "technical" in self.q_types[idx]):
                ask_followup = True
            elif style == "explore" and fcount < max_fups:
                ask_followup = True
            if re.search(r"(why are you asking|this is irrelevant|how does that help)", answer_text.lower()):
                ask_followup = False

        if ask_followup:
            fup = self._heuristic_followup(self.questions[idx], answer_text, style)
            self.followup_counts[idx] = fcount + 1
            if fup:
                self.events.append({"type": "agent", "text": fup})
                return {"action": "followup", "followup": fup}

        self.current_index += 1
        if self.current_index < len(self.questions):
            next_q = self.questions[self.current_index]
            self.events.append({"type": "agent", "text": next_q})
            return {"action": "next", "next_question": next_q}
        else:
            self.events.append({"type": "agent", "text": "That concludes the mock interview. Thank you!"})
            return {"action": "done"}

    def force_next(self) -> Optional[str]:
        self.current_index += 1
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.events.append({"type": "agent", "text": q})
            return q
        self.events.append({"type": "agent", "text": "That concludes the mock interview. Thank you!"})
        return None

    def get_transcript(self) -> List[Dict]:
        return self.events
