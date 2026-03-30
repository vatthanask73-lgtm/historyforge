#!/usr/bin/env python3
"""HistoryForge — utils/text_animations.py — Text overlays."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import ImageClip
except ImportError:
    pass

import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fonts import get_font_path

GOLD = "#c4a44a"
WHITE = "#ffffff"


def chapter_title_clip(text, duration=4.0, size=(1920, 1080), fade=0.8):
    hf = get_font_path("heading")
    w, h = size
    img = Image.new("RGBA", (w, h), (10, 10, 10, 230))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(hf, 72)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    tx, ty = (w-tw)//2, (h-th)//2
    lw = min(tw+80, w-200); lx = (w-lw)//2
    draw.line([(lx, ty-30), (lx+lw, ty-30)], fill=GOLD, width=3)
    draw.text((tx, ty), text, font=font, fill=WHITE)
    draw.line([(lx, ty+th+20), (lx+lw, ty+th+20)], fill=GOLD, width=3)
    return ImageClip(np.array(img)).set_duration(duration).fadein(fade).fadeout(fade)


def lower_third_clip(primary, secondary="", duration=5.0, size=(1920,1080), fade=0.5):
    hf, bf = get_font_path("heading"), get_font_path("body")
    w, h = size
    bar_y = h - 160
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([60, bar_y, w-60, bar_y+100], fill=(10,10,30,190))
    draw.rectangle([60, bar_y, 68, bar_y+100], fill=GOLD)
    try: fp = ImageFont.truetype(hf, 36)
    except: fp = ImageFont.load_default()
    try: fs = ImageFont.truetype(bf, 24)
    except: fs = ImageFont.load_default()
    draw.text((90, bar_y+14), primary, font=fp, fill=WHITE)
    if secondary:
        draw.text((90, bar_y+58), secondary, font=fs, fill=GOLD)
    return ImageClip(np.array(img)).set_duration(duration).fadein(fade).fadeout(fade)


def year_stamp_clip(location, year, duration=4.0, size=(1920,1080), fade=0.6):
    hf = get_font_path("heading")
    w, h = size
    try:
        fl = ImageFont.truetype(hf, 52)
        fy = ImageFont.truetype(hf, 34)
    except:
        fl = fy = ImageFont.load_default()
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    x, y = 120, h-240
    draw.text((x, y), location.upper(), font=fl, fill=WHITE)
    bbox = draw.textbbox((x, y), location.upper(), font=fl)
    draw.line([(x, bbox[3]+6), (bbox[2], bbox[3]+6)], fill=GOLD, width=3)
    draw.text((x, bbox[3]+16), year, font=fy, fill=GOLD)
    return ImageClip(np.array(img)).set_duration(duration).fadein(fade).fadeout(fade)
