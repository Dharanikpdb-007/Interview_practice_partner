import json
from typing import List, Dict

def save_transcript(transcript: List[Dict], path: str = "transcript.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)
    return path
