#!/usr/bin/env python3
"""HistoryForge — 03_voice_narrator.py — Edge-TTS narration."""

import os, sys, json, asyncio, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import load_voice_profiles

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Voice] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


async def narrate_section(text, voice_id="en-US-GuyNeural",
                          rate="-10%", pitch="-2st", output_path="out.mp3"):
    try:
        import edge_tts
        comm = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
        await comm.save(output_path)
        log.info("TTS: %s (%d chars)", output_path, len(text))
        return True
    except Exception as e:
        log.error("TTS fail: %s", e)
        return False


async def narrate_script(script_path, voice_profile="deep_male",
                         output_dir="output/audio"):
    with open(script_path) as f:
        script = json.load(f)

    profiles = load_voice_profiles()
    prof = profiles.get("profiles", {}).get(voice_profile,
        {"voice_id": "en-US-GuyNeural", "rate": "-10%", "pitch": "-2st"})

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    timing = {"sections": [], "total_duration": 0.0}

    for i, sec in enumerate(script["sections"]):
        text = sec.get("narration", "").strip()
        if not text:
            continue
        if not text.endswith((".", "!", "?")):
            text += "."
        fp = out / f"section_{i:03d}.mp3"
        ok = await narrate_section(text, prof.get("voice_id", "en-US-GuyNeural"),
                                   prof.get("rate", "-10%"), prof.get("pitch", "-2st"),
                                   str(fp))
        if ok:
            timing["sections"].append({
                "type": sec["type"], "audio_file": str(fp),
                "start_time": round(timing["total_duration"], 2),
                "duration_sec": sec.get("duration_sec", 30)})
            timing["total_duration"] += sec.get("duration_sec", 30)

    with open(out / "timing.json", "w") as f:
        json.dump(timing, f, indent=2)

    # Combine audio
    try:
        from moviepy.editor import AudioFileClip, concatenate_audioclips
        clips = [AudioFileClip(s["audio_file"]) for s in timing["sections"]]
        if clips:
            final = concatenate_audioclips(clips)
            final.write_audiofile(str(out / "narration_final.mp3"), fps=44100, logger=None)
            for c in clips: c.close()
            final.close()
    except:
        pass
    return timing


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--script", required=True)
    p.add_argument("--voice", default="deep_male")
    p.add_argument("--output", "-o", default="output/audio")
    args = p.parse_args()
    timing = asyncio.run(narrate_script(args.script, args.voice, args.output))
    print(f"\n🎙️  {timing['total_duration']:.0f}s narrated → {args.output}")

if __name__ == "__main__":
    main()
