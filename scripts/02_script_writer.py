#!/usr/bin/env python3
import os, sys, json, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ScriptWriter] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False


def generate_script(topic, duration=15, style="documentary"):
    if not GEMINI_OK:
        raise ImportError("pip install google-generativeai")
    api_key = get_api_key("GEMINI")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "You are a professional history documentary scriptwriter.\n"
    prompt += "Write a " + str(duration) + "-minute script about: " + topic["title"] + "\n"
    prompt += "Details: " + topic.get("description", "") + "  Era: " + topic.get("era", "") + "\n"
    prompt += "Style: " + style.upper() + "\n\n"
    prompt += "STRUCTURE: cold_open(30s), intro(15s), 3-5 chapters, climax, conclusion, outro(15s)\n\n"
    prompt += "For EACH section provide: narration, footage_cue, text_overlay, music_cue, duration_sec\n\n"
    prompt += 'Return ONLY valid JSON with this structure:\n'
    prompt += '{"title":"' + topic["title"] + '","duration_minutes":' + str(duration) + ',"style":"' + style + '",'
    prompt += '"sections":[{"type":"cold_open","narration":"...","footage_cue":"...","text_overlay":"...","music_cue":"...","duration_sec":30}]}\n\n'
    prompt += "Sound like History Channel. Dramatic. Engaging. Return ONLY the JSON, no other text."
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    script = json.loads(text)
    t = 0.0
    for sec in script["sections"]:
        sec["start_time"] = round(t, 2)
        t += sec.get("duration_sec", 30)
        sec["end_time"] = round(t, 2)
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
