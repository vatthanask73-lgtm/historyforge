#!/usr/bin/env python3
"""HistoryForge — 05_video_editor.py — Video assembly."""

import os, sys, json, random, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import load_settings
from utils.effects import random_ken_burns, vignette, film_grain
from utils.color_grading import grade_clip

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Editor] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

try:
    from moviepy.editor import (VideoFileClip, ImageClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips, AudioFileClip)
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    OK = True
except ImportError as e:
    log.error("Missing: %s", e); OK = False


class Editor:
    def __init__(self):
        s = load_settings()
        v = s.get("video", {})
        r = v.get("resolution", [1920, 1080])
        self.W = r[0] if isinstance(r, list) else 1920
        self.H = r[1] if isinstance(r, list) else 1080
        self.fps = v.get("fps", 30)
        self.name = s.get("channel_name", "Chronicles Unveiled")

    def _card(self, text, dur, bg=(10,10,10), text_color=(196,164,74), font_size=72):
        img = Image.new("RGB", (self.W, self.H), bg)
        draw = ImageDraw.Draw(img)
        if bg == (10,10,10):
            for _ in range(50):
                x, y = random.randint(0,self.W), random.randint(0,self.H)
                draw.ellipse([x-2,y-2,x+2,y+2], fill=(196,164,74))
        try: font = ImageFont.truetype("arial.ttf", font_size)
        except: font = ImageFont.load_default()
        words = text.split(); lines, cur = [], []
        for w in words:
            test = " ".join(cur + [w])
            bbox = draw.textbbox((0,0), test, font=font)
            if bbox[2]-bbox[0] < self.W-120: cur.append(w)
            else:
                if cur: lines.append(" ".join(cur))
                cur = [w]
        if cur: lines.append(" ".join(cur))
        y = (self.H - len(lines)*int(font_size*1.3))//2
        for ln in lines[:10]:
            bbox = draw.textbbox((0,0), ln, font=font)
            draw.text(((self.W-(bbox[2]-bbox[0]))//2, y), ln, font=font, fill=text_color)
            y += int(font_size*1.3)
        return ImageClip(np.array(img)).set_duration(dur).fadein(1).fadeout(1)

    def _load_footage(self, path, dur):
        clip = VideoFileClip(path)
        clip = random_ken_burns(clip)
        if clip.duration < dur:
            clip = concatenate_videoclips([clip] * (int(dur/clip.duration)+1))
        clip = clip.subclip(0, min(dur, clip.duration)).resize((self.W, self.H))
        return grade_clip(clip, "documentary")

    def assemble(self, script, footage, timing, output):
        if not OK: raise ImportError("moviepy/PIL/numpy needed")
        segs = [self._card(self.name, 10)]

        for i, sec in enumerate(script.get("sections", [])):
            dur = sec.get("duration_sec", 30)
            sf = [f for f in footage if f.get("section_index") == i]
            if sf and os.path.isfile(sf[0]["file"]):
                try: segs.append(self._load_footage(sf[0]["file"], dur))
                except: segs.append(self._card(sec.get("narration","")[:200], dur,
                                               (20,20,30), (255,255,255), 40))
            else:
                segs.append(self._card(sec.get("narration","")[:200], dur,
                                       (20,20,30), (255,255,255), 40))

        segs.append(self._card("Thanks for watching!\nSubscribe for more", 15,
                               (26,26,46), (255,255,255), 56))

        log.info("Concatenating %d segments...", len(segs))
        tl = concatenate_videoclips(segs, method="compose")
        tl = vignette(tl, 0.35)
        tl = film_grain(tl, 0.04)

        # Audio
        narr_dir = Path(timing.get("sections",[{}])[0].get("audio_file","")).parent \
            if timing.get("sections") else None
        narr_path = narr_dir / "narration_final.mp3" if narr_dir else None
        if narr_path and narr_path.is_file():
            narr = AudioFileClip(str(narr_path))
            if narr.duration > tl.duration:
                narr = narr.subclip(0, tl.duration)
            tl = tl.set_audio(narr)

        Path(output).parent.mkdir(parents=True, exist_ok=True)
        log.info("Rendering → %s", output)
        tl.write_videofile(output, fps=self.fps, codec="libx264",
            audio_codec="aac", bitrate="10M", preset="medium",
            threads=os.cpu_count() or 2, logger=None)
        tl.close()
        for s in segs:
            try: s.close()
            except: pass
        mb = os.path.getsize(output)/(1024*1024)
        log.info("✅ Done: %s (%.1f MB)", output, mb)
        return output


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--script", required=True)
    p.add_argument("--footage", required=True)
    p.add_argument("--audio-timing", required=True)
    p.add_argument("--output", "-o", default="output/final_video.mp4")
    args = p.parse_args()
    with open(args.script) as f: script = json.load(f)
    with open(args.footage) as f: footage = json.load(f)
    with open(args.audio_timing) as f: timing = json.load(f)
    Editor().assemble(script, footage.get("downloads",[]), timing, args.output)
    print(f"\n🎬 Video → {args.output}")

if __name__ == "__main__":
    main()
