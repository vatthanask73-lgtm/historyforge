#!/usr/bin/env python3
"""HistoryForge — utils/effects.py — Ken Burns, transitions, vignette, grain."""

import math
import random
import logging
import numpy as np
from PIL import Image, ImageDraw

log = logging.getLogger("effects")

try:
    from moviepy.editor import (
        VideoFileClip, ImageClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips,
    )
except ImportError:
    pass


def ken_burns(clip, zoom_start=1.0, zoom_end=1.15,
              pan_start=(0.5, 0.5), pan_end=(0.5, 0.5)):
    w, h = clip.size
    def _transform(get_frame, t):
        progress = t / max(clip.duration, 0.001)
        zoom = zoom_start + (zoom_end - zoom_start) * progress
        cx = pan_start[0] + (pan_end[0] - pan_start[0]) * progress
        cy = pan_start[1] + (pan_end[1] - pan_start[1]) * progress
        frame = get_frame(t)
        fh, fw = frame.shape[:2]
        nw, nh = int(fw * zoom), int(fh * zoom)
        pil = Image.fromarray(frame).resize((nw, nh), Image.LANCZOS)
        left = max(0, min(int(cx * (nw - fw)), nw - fw))
        top = max(0, min(int(cy * (nh - fh)), nh - fh))
        cropped = pil.crop((left, top, left + fw, top + fh))
        return np.array(cropped)
    return clip.fl(_transform, apply_to=[])


def random_ken_burns(clip, intensity=0.15):
    return ken_burns(
        clip, 1.0, 1.0 + random.uniform(0.05, intensity),
        (random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)),
        (random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)))


def crossfade(clip_a, clip_b, duration=0.5):
    a = clip_a.crossfadeout(duration)
    b = clip_b.crossfadein(duration).set_start(clip_a.duration - duration)
    return CompositeVideoClip([a, b]).set_duration(
        clip_a.duration + clip_b.duration - duration)


def vignette(clip, strength=0.45):
    w, h = clip.size
    cx, cy = w // 2, h // 2
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = math.sqrt(cx ** 2 + cy ** 2)
    vig = np.clip(1.0 - strength * (dist / max_dist) ** 1.5, 0, 1).astype(np.float32)
    def _apply(frame):
        f = frame.astype(np.float32)
        for c in range(3):
            f[:, :, c] *= vig
        return np.clip(f, 0, 255).astype(np.uint8)
    return clip.fl_image(_apply)


def film_grain(clip, intensity=0.06):
    def _grain(frame):
        noise = np.random.normal(0, intensity * 255, frame.shape).astype(np.float32)
        return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return clip.fl_image(_grain)
