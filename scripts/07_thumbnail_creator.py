#!/usr/bin/env python3
"""HistoryForge — 07_thumbnail_creator.py — Cinematic thumbnails."""

import os, sys, json, logging, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_api_key
from utils.fonts import get_font_path

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Thumb] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np

W, H = 1280, 720


def fetch_bg(query, key):
    try:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": key},
            params={"query": query+" cinematic","per_page":1,"orientation":"landscape"}, timeout=30)
        r.raise_for_status()
        photos = r.json().get("photos",[])
        if photos:
            url = photos[0]["src"].get("original") or photos[0]["src"]["large"]
            return Image.open(requests.get(url, stream=True, timeout=30).raw)
    except: pass
    return None


def create_thumbnail(title, style="dramatic", bg_img=None, output="output/thumbnail.png"):
    if bg_img:
        r = max(W/bg_img.width, H/bg_img.height)
        bg = bg_img.resize((int(bg_img.width*r), int(bg_img.height*r)), Image.LANCZOS)
        l,t = (bg.width-W)//2, (bg.height-H)//2
        bg = bg.crop((l,t,l+W,t+H)).convert("RGB")
        bg = ImageEnhance.Brightness(bg).enhance(0.65)
        bg = ImageEnhance.Contrast(bg).enhance(1.35)
    else:
        bg = Image.new("RGB", (W,H), (15,15,25))

    draw = ImageDraw.Draw(bg)
    fp = get_font_path("thumbnail")
    try: font = ImageFont.truetype(fp, 90) if fp else ImageFont.load_default()
    except: font = ImageFont.load_default()

    words = title.upper().split(); lines, cur = [], []
    for w in words:
        test = " ".join(cur+[w])
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] < W-100: cur.append(w)
        else:
            if cur: lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))

    y = H//3
    for ln in lines[:3]:
        bbox = draw.textbbox((0,0), ln, font=font)
        tw = bbox[2]-bbox[0]; x = (W-tw)//2
        for dx in range(-3,4):
            for dy in range(-3,4):
                draw.text((x+dx,y+dy), ln, font=font, fill=(0,0,0))
        draw.text((x,y), ln, font=font, fill=(255,255,255))
        y += bbox[3]-bbox[1]+10

    draw.rectangle([0,H-8,W,H], fill=(196,164,74))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    bg.save(output, "PNG", quality=95)
    log.info("Thumbnail: %s", output)
    return output


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--topic", default=None)
    p.add_argument("--output", "-o", default="output/thumbnail.png")
    args = p.parse_args()
    bg = None
    if args.topic and os.path.isfile(args.topic):
        with open(args.topic) as f: t = json.load(f)
        k = get_api_key("PEXELS")
        if k: bg = fetch_bg(" ".join(t.get("keywords",[])[:3]) or t["title"], k)
    create_thumbnail(args.title, bg_img=bg, output=args.output)
    print(f"\n🖼️  Thumbnail → {args.output}")

if __name__ == "__main__":
    main()
