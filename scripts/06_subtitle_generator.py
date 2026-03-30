#!/usr/bin/env python3
"""HistoryForge — 06_subtitle_generator.py — SRT from script."""

import os, sys, json, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Subs] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def _ts(s):
    h=int(s//3600); m=int((s%3600)//60); sc=int(s%60); ms=int((s-int(s))*1000)
    return f"{h:02d}:{m:02d}:{sc:02d},{ms:03d}"


def from_script(script, output="output/subtitles.srt"):
    srt, idx, t = "", 1, 0.0
    for sec in script.get("sections", []):
        narr = sec.get("narration","").strip()
        dur = sec.get("duration_sec", 30)
        if not narr: t += dur; continue
        sents, buf = [], ""
        for ch in narr:
            buf += ch
            if ch in ".!?" and len(buf) > 20:
                sents.append(buf.strip()); buf = ""
        if buf.strip(): sents.append(buf.strip())
        if not sents: sents = [narr]
        per = dur / len(sents)
        for s in sents:
            srt += f"{idx}\n{_ts(t)} --> {_ts(t+per)}\n{s}\n\n"
            idx += 1; t += per
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(srt.strip())
    log.info("SRT: %s (%d entries)", output, idx-1)
    return output


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--script", required=True)
    p.add_argument("--output", "-o", default="output/subtitles.srt")
    args = p.parse_args()
    with open(args.script) as f:
        script = json.load(f)
    r = from_script(script, args.output)
    print(f"\n📝 Subtitles → {r}")

if __name__ == "__main__":
    main()
