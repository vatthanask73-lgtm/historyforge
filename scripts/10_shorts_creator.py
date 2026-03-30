#!/usr/bin/env python3
"""HistoryForge — 10_shorts_creator.py — YouTube Shorts."""

import os, sys, json, random, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_output_dir
from utils.fonts import get_font_path

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Shorts] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

SW, SH = 1080, 1920


def find_peak(vpath, dur=50):
    clip = VideoFileClip(vpath)
    total = clip.duration
    if clip.audio is None:
        clip.close(); s = total*0.25; return s, min(s+dur, total)
    sr = 22050
    arr = clip.audio.to_soundarray(fps=sr).mean(axis=1)
    clip.close()
    bk = 5; n = len(arr)//(sr*bk)
    energy = [float(np.sqrt(np.mean(arr[i*sr*bk:(i+1)*sr*bk]**2))) for i in range(n)]
    w = dur//bk; bi, be = 0, -1
    for i in range(len(energy)-w):
        e = sum(energy[i:i+w])
        if e > be: be, bi = e, i
    s = bi*bk; return s, min(s+dur, total)


def reformat(clip):
    def _bg(frame):
        pil = Image.fromarray(frame)
        r = max(SW/pil.width, SH/pil.height)
        pil = pil.resize((int(pil.width*r), int(pil.height*r)), Image.LANCZOS)
        l,t = (pil.width-SW)//2, (pil.height-SH)//2
        pil = pil.crop((l,t,l+SW,t+SH)).filter(ImageFilter.GaussianBlur(25))
        return np.array(Image.blend(pil, Image.new("RGB",(SW,SH),(0,0,0)), 0.45))
    bg = clip.without_audio().fl_image(_bg).set_duration(clip.duration)
    sc = min(SW/clip.w, 1400/clip.h)
    fg = clip.resize(sc).set_position(("center","center"))
    comp = CompositeVideoClip([bg, fg], size=(SW,SH)).set_duration(clip.duration)
    if clip.audio: comp = comp.set_audio(clip.audio)
    return comp


def create_short(vpath, output, dur=50, name="Chronicles Unveiled"):
    log.info("Short from: %s", vpath)
    s, e = find_peak(vpath, dur)
    if e-s > 59: e = s+59
    src = VideoFileClip(vpath)
    seg = src.subclip(s, e)
    vert = reformat(seg)
    fp = get_font_path("caption")
    try: font = ImageFont.truetype(fp, 30) if fp else ImageFont.load_default()
    except: font = ImageFont.load_default()
    wm = Image.new("RGBA",(SW,60),(0,0,0,0))
    d = ImageDraw.Draw(wm)
    bb = d.textbbox((0,0), name, font=font)
    d.text((SW-(bb[2]-bb[0])-20, 15), name, font=font, fill=(255,255,255,90))
    wmc = ImageClip(np.array(wm)).set_duration(vert.duration).set_position((0,40))
    vert = CompositeVideoClip([vert, wmc], size=(SW,SH))
    if seg.audio: vert = vert.set_audio(seg.audio)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    vert.write_videofile(output, fps=30, codec="libx264", audio_codec="aac",
        bitrate="6M", preset="medium", threads=os.cpu_count() or 2, logger=None)
    seg.close(); src.close()
    log.info("✅ Short: %.1f MB", os.path.getsize(output)/1024/1024)
    return output


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("-o","--output", default=None)
    p.add_argument("-d","--duration", type=int, default=50)
    p.add_argument("-n","--channel-name", default="Chronicles Unveiled")
    args = p.parse_args()
    if not args.output:
        args.output = str(get_output_dir()/f"{Path(args.video).stem}_short.mp4")
    create_short(args.video, args.output, args.duration, args.channel_name)

if __name__ == "__main__":
    main()
