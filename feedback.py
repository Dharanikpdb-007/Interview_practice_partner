# feedback.py
import re
from typing import List, Dict

FILLER_WORDS = {"um", "uh", "like", "you know", "so", "actually", "basically", "right", "okay", "hmm"}
METRIC_REGEX = re.compile(r"\b\d+%|\b\d+\s*(ms|s|seconds|minutes|hours|GB|MB|gb|mb)\b", re.IGNORECASE)

def _count_fillers(text: str) -> int:
    t = text.lower()
    return sum(t.count(f) for f in FILLER_WORDS)

def _detect_star(text: str) -> bool:
    t = text.lower()
    # look for indicators of Situation/Task/Action/Result or explicit result words
    if any(k in t for k in ("situation", "task", "action", "result", "challenge", "outcome")):
        return True
    if any(k in t for k in ("resulted in", "led to", "improved", "reduced", "increased", "success")):
        return True
    return False

def _technical_depth_score(text: str) -> float:
    score = 0.0
    keywords = ["algorithm", "complexity", "latency", "throughput", "scale", "optimization", "database",
                "sql", "nosql", "docker", "kubernetes", "api", "concurrency", "threads", "profiling"]
    t = text.lower()
    for kw in keywords:
        if kw in t:
            score += 0.5
    # reward metrics
    if METRIC_REGEX.search(text):
        score += 1.5
    # reward clear action words
    if any(a in t for a in ("implemented", "designed", "built", "optimized", "fixed", "led")):
        score += 0.5
    return min(score, 5.0)

def analyze_interview(transcript: List[Dict]) -> Dict:
    answers = [ev["text"].strip() for ev in transcript if ev["type"] == "user" and ev.get("text", "").strip()]
    if not answers:
        return {"error": "No user answers in transcript."}

    comm_scores = []
    tech_scores = []
    example_scores = []
    total_fillers = 0
    for a in answers:
        wc = len(a.split())
        fillers = _count_fillers(a)
        total_fillers += fillers

        # Communication score: 0-5
        if wc < 15:
            comm = 2.0
        elif wc < 40:
            comm = 4.0
        elif wc < 80:
            comm = 4.5
        else:
            comm = 3.5  # long and possibly rambling
        # reduce for fillers
        comm -= min(1.5, 0.4 * fillers)
        comm = max(0.0, min(5.0, comm))
        comm_scores.append(comm)

        # Technical depth
        tech = _technical_depth_score(a)
        tech_scores.append(tech)

        # Examples/STAR
        example_scores.append(5.0 if _detect_star(a) else min(3.0, 1.5 + (wc / 80.0) * 5.0))

    n = len(answers)
    communication = round(sum(comm_scores) / n, 2)
    technical = round(sum(tech_scores) / n, 2)
    examples = round(sum(example_scores) / n, 2)

    composite = round((communication * 0.4 + technical * 0.35 + examples * 0.25), 2)

    suggestions = []
    if communication < 3.5:
        suggestions.append("Work on clarity: prefer the STAR structure and aim for ~40-80 words. Reduce filler words and keep sentences crisp.")
    else:
        suggestions.append("Communication is strong. Maintain concise structure and explicit outcomes.")

    if technical < 3.0:
        suggestions.append("Increase technical depth: mention concrete technologies, algorithmic tradeoffs, and measurable results.")
    else:
        suggestions.append("Technical depth is good. Add more metrics when possible.")

    if examples < 3.0:
        suggestions.append("Use STAR more consistently and quantify the results (e.g., 'improved X by 30%').")
    else:
        suggestions.append("Good use of examples — ensure you highlight your personal contribution.")

    if total_fillers / n > 1.5:
        suggestions.append("You use several filler words on average. Practice pausing instead of using 'um'/'like'.")

    report = {
        "communication": min(5.0, communication),
        "technical": min(5.0, technical),
        "examples": min(5.0, examples),
        "composite": min(5.0, composite),
        "meta": {
            "answers_count": n,
            "avg_words": round(sum(len(a.split()) for a in answers) / n, 1),
            "avg_fillers_per_answer": round(total_fillers / n, 2),
        },
        "suggestions": suggestions
    }
    return report
