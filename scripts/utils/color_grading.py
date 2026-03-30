#!/usr/bin/env python3
"""HistoryForge — utils/color_grading.py — Cinematic colour grading."""

import numpy as np
from PIL import Image, ImageEnhance


def teal_orange(frame, strength=0.5):
    r, g, b = frame[:,:,0], frame[:,:,1], frame[:,:,2]
    lum = 0.299*r + 0.587*g + 0.114*b
    sm = np.clip(1.0 - lum/128.0, 0, 1) * strength
    hm = np.clip((lum - 128.0)/128.0, 0, 1) * strength
    rf, gf, bf = r.astype(np.float32), g.astype(np.float32), b.astype(np.float32)
    rf -= sm*18; gf += sm*6; bf += sm*22
    rf += hm*20; gf += hm*6; bf -= hm*14
    return np.stack([np.clip(rf,0,255), np.clip(gf,0,255), np.clip(bf,0,255)], axis=2).astype(np.uint8)


def desaturate(frame, amount=0.25):
    return np.array(ImageEnhance.Color(Image.fromarray(frame)).enhance(1.0 - amount))


def boost_contrast(frame, factor=1.25):
    return np.array(ImageEnhance.Contrast(Image.fromarray(frame)).enhance(factor))


def apply_cinematic_grade(frame, preset="documentary"):
    if preset == "documentary":
        frame = desaturate(frame, 0.20)
        frame = teal_orange(frame, 0.40)
        frame = boost_contrast(frame, 1.15)
    elif preset == "warm":
        frame = teal_orange(frame, 0.25)
        frame = boost_contrast(frame, 1.10)
    elif preset == "cold":
        frame = desaturate(frame, 0.30)
        frame = boost_contrast(frame, 1.15)
    return frame


def grade_clip(clip, preset="documentary"):
    return clip.fl_image(lambda f: apply_cinematic_grade(f, preset))
