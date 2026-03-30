#!/usr/bin/env python3
import os, sys, json, random, logging, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import load_topics_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TopicResearch] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def get_topic_from_ai():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
        body = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You ONLY respond with valid JSON."},
                {"role": "user", "content": 'Generate a compelling topic for a YouTube history documentary. Return ONLY a JSON object: {"title":"under 70 chars","description":"2-3 sentences","keywords":["8 keywords"],"era":"time period","category":"ancient_civilizations","difficulty":"easy"}. Real history only.'}
            ],
            "temperature": 0.9,
            "max_tokens": 500
        }
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        topic = json.loads(text)
        log.info("AI generated topic: %s", topic.get("title", ""))
        return topic
    except Exception as e:
        log.error("AI topic generation failed: %s", e)
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
                "keywords": ["plague", "medieval", "Europe"], "era": "1347-1351",
                "category": "medieval_history", "difficulty": "easy"}
    t = random.choice(topics)
    t.setdefault("description", "A fascinating chapter in history.")
    t.setdefault("keywords", ["history"])
    return t


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--category", type=str, default=None)
    p.add_argument("--ai", action="store_true")
    p.add_argument("--output", "-o", default="output/topic.json")
    args = p.parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    topic = None
    if args.ai:
        topic = get_topic_from_ai()
    if not topic:
        topic = get_random_topic(args.category)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(topic, f, indent=2, ensure_ascii=False)
    print("Topic: " + topic["title"])


if __name__ == "__main__":
    main()
