#!/usr/bin/env python3
"""HistoryForge — 01_topic_research.py — AI topic selection."""

import os, sys, json, random, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import load_settings, get_api_key, load_topics_database

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [TopicResearch] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False


def get_topic_from_gemini():
    if not GEMINI_OK:
        return None
    api_key = get_api_key("GEMINI")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = """Generate a compelling topic for a YouTube history documentary.
Return ONLY a JSON object:
{"title":"...under 70 chars","description":"2-3 sentences",
"keywords":["8-12 keywords"],"era":"time period",
"category":"ancient_civilizations/world_wars/mysteries_conspiracies/famous_figures/lost_cities/space_history/medieval_history/cold_war",
"difficulty":"easy/medium/hard"}
Real history only. Good visual potential."""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except Exception as e:
        log.error("Gemini failed: %s", e)
        return None


def get_random_topic(category=None):
    db = load_topics_database()
    cats = db.get("categories", {})
    topics = []
    if category and category in cats:
        topics = cats[category].get("topics", [])
    else:
        for c in cats.values():
            topics.extend(c.get("topics", []))
    if not topics:
        return {"title": "The Black Death: Plague That Killed Half of Europe",
                "description": "How a bacterium changed European history.",
                "keywords": ["plague","medieval","Europe"], "era": "1347-1351",
                "category": "medieval_history", "difficulty": "easy"}
    t = random.choice(topics)
    t.setdefault("description", "A fascinating chapter in history.")
    t.setdefault("keywords", ["history"])
    return t


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--category", type=str)
    p.add_argument("--ai", action="store_true")
    p.add_argument("--output", "-o", default="output/topic.json")
    args = p.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    topic = None
    if args.ai:
        topic = get_topic_from_gemini()
    if not topic:
        topic = get_random_topic(args.category)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(topic, f, indent=2, ensure_ascii=False)
    print(f"\n📚 Topic: {topic['title']}")
    print(f"   Saved: {args.output}")

if __name__ == "__main__":
    main()
