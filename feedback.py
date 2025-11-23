import re
from typing import List, Dict

def analyze_interview(transcript: List[Dict]) -> Dict:
    answers = [ev["text"] for ev in transcript if ev["type"] == "user"]
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
        report['suggestions'].append('Structure your answers using STAR: Situation, Task, Action, Result. Keep responses clear and focused.')
    if report['technical'] < 3.0:
        report['suggestions'].append('Add more technical depth: mention specific algorithms, tradeoffs, or complexity. Use concrete terms.')
    if report['examples'] < 3.0:
        report['suggestions'].append('Use measurable outcomes and quantify results where possible (e.g., improved throughput by 30%).')

    report['suggestions'].append('Practice mock interviews with varying personas (confused, efficient, chatty) to build adaptability.')

    return report
