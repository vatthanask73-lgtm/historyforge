#!/usr/bin/env python3
import os, sys, json, logging, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ScriptWriter] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def generate_script(topic, duration=15, style="documentary"):
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            return generate_script_gemini(topic, duration, style, api_key)
        raise ValueError("No AI API key set. Set GROQ_API_KEY or GEMINI_API_KEY")
    return generate_script_groq(topic, duration, style, api_key)


def generate_script_groq(topic, duration, style, api_key):
    log.info("Using Groq API (Llama 3.3 70B)")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    prompt = build_prompt(topic, duration, style)
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional history documentary scriptwriter. You ONLY respond with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    resp = requests.post(url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"].strip()
    return parse_script(text, topic, duration, style)


def generate_script_gemini(topic, duration, style, api_key):
    log.info("Using Gemini API")
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    prompt = build_prompt(topic, duration, style)
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    return parse_script(text, topic, duration, style)


def build_prompt(topic, duration, style):
    p = "Write a " + str(duration) + "-minute documentary script about: " + topic["title"] + "\n"
    p += "Details: " + topic.get("description", "") + "\n"
    p += "Era: " + topic.get("era", "") + "\n"
    p += "Style: " + style.upper() + "\n\n"
    p += "STRUCTURE:\n"
    p += "- cold_open (30 seconds): Shocking dramatic hook\n"
    p += "- intro (15 seconds): Welcome and topic introduction\n"
    p += "- 3 to 5 chapters: Main content with dramatic narration\n"
    p += "- climax: Most dramatic revelation\n"
    p += "- conclusion (30 seconds): Summary and thought-provoking ending\n"
    p += "- outro (15 seconds): Subscribe call to action\n\n"
    p += "For EACH section provide these fields:\n"
    p += "- type: section type name\n"
    p += "- narration: the spoken text (dramatic documentary tone like History Channel)\n"
    p += "- footage_cue: description of what video footage to show\n"
    p += "- text_overlay: on-screen text to display\n"
    p += "- music_cue: music mood (epic, mysterious, dramatic, somber)\n"
    p += "- duration_sec: duration in seconds\n\n"
    p += "Total duration must be approximately " + str(duration) + " minutes (" + str(duration * 60) + " seconds).\n\n"
    p += "Return ONLY a valid JSON object with this exact structure:\n"
    p += '{"title": "' + topic["title"] + '", "duration_minutes": ' + str(duration) + ', "style": "' + style + '", '
    p += '"sections": [{"type": "cold_open", "narration": "In the year...", "footage_cue": "dark dramatic shots", '
    p += '"text_overlay": "THE TITLE", "music_cue": "ominous", "duration_sec": 30}]}\n\n'
    p += "IMPORTANT: Return ONLY the JSON. No markdown. No explanation. Just the JSON object."
    return p


def parse_script(text, topic, duration, style):
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    text = text.strip()
    script = json.loads(text)
    if "title" not in script:
        script["title"] = topic["title"]
    if "duration_minutes" not in script:
        script["duration_minutes"] = duration
    if "style" not in script:
        script["style"] = style
    t = 0.0
    for sec in script.get("sections", []):
        sec["start_time"] = round(t, 2)
        t += sec.get("duration_sec", 30)
        sec["end_time"] = round(t, 2)
    log.info("Script generated: %d sections", len(script.get("sections", [])))
    return script


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--duration", type=int, default=15)
    p.add_argument("--style", default="documentary")
    p.add_argument("--output", "-o", default="output/script.json")
    args = p.parse_args()
    with open(args.topic) as f:
        topic = json.load(f)
    script = generate_script(topic, args.duration, args.style)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
    print("Script: " + str(len(script["sections"])) + " sections saved to " + args.output)


if __name__ == "__main__":
    main()
