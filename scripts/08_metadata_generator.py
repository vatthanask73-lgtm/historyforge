#!/usr/bin/env python3
"""HistoryForge — 08_metadata_generator.py — YouTube metadata."""

import os, sys, json, hashlib, logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import load_settings

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Meta] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def _ts(s):
    h=int(s//3600); m=int((s%3600)//60); sc=int(s%60)
    return f"{h:02d}:{m:02d}:{sc:02d}" if h else f"{m:02d}:{sc:02d}"


def generate(topic, script, timing):
    ch = load_settings().get("channel_name", "Chronicles Unveiled")
    title = topic.get("title","Documentary")
    if len(title) > 70: title = title[:67]+"..."

    chaps = []; t = 0
    for sec in script.get("sections",[]):
        if sec.get("type") not in ("cold_open","intro","outro"):
            chaps.append(f"{_ts(t)} {sec.get('text_overlay','') or sec.get('type','').title()}")
        t += sec.get("duration_sec", 30)

    desc = "\n".join([
        topic.get("description",""), "", "📖 CHAPTERS:", *chaps, "",
        f"🏛️ {ch}", "👍 LIKE & 🔔 SUBSCRIBE!", "",
        "#history #documentary #education"])

    tags = list(dict.fromkeys(
        ["history","documentary","education",ch.lower()] +
        [k.lower() for k in topic.get("keywords",[])[:12]]))[:30]

    vid = hashlib.md5(f"{title}{datetime.now().timestamp()}".encode()).hexdigest()[:8].upper()
    return {"title":title,"description":desc,"tags":tags,"category_id":"27",
            "privacy_status":"private","made_for_kids":False,"video_id":f"HF{vid}"}


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--script", required=True)
    p.add_argument("--timing", required=True)
    p.add_argument("--output", "-o", default="output/metadata.json")
    args = p.parse_args()
    with open(args.topic) as f: topic = json.load(f)
    with open(args.script) as f: script = json.load(f)
    with open(args.timing) as f: timing = json.load(f)
    meta = generate(topic, script, timing)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output,"w") as f: json.dump(meta, f, indent=2)
    print(f"\n📋 Metadata → {args.output}")

if __name__ == "__main__":
    main()
