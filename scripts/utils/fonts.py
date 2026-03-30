#!/usr/bin/env python3
"""HistoryForge — utils/fonts.py — Font management."""

import os
import logging
import urllib.request
from pathlib import Path

log = logging.getLogger("fonts")

FONT_DIR = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "fonts"

FONT_URLS = {
    "Cinzel": "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf",
    "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "Roboto": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
    "BebasNeue": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
}

ROLE_MAP = {"heading": "Cinzel", "body": "Inter", "caption": "Roboto", "thumbnail": "BebasNeue"}


def _download_font(name):
    url = FONT_URLS.get(name)
    if not url:
        return None
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    dest = FONT_DIR / f"{name}.ttf"
    if dest.is_file():
        return dest
    try:
        log.info("Downloading font '%s'...", name)
        urllib.request.urlretrieve(url, str(dest))
        return dest
    except Exception as exc:
        log.warning("Could not download font '%s': %s", name, exc)
        return None


def get_font_path(role_or_name):
    name = ROLE_MAP.get(role_or_name, role_or_name)
    cached = FONT_DIR / f"{name}.ttf"
    if cached.is_file():
        return str(cached)
    dl = _download_font(name)
    if dl:
        return str(dl)
    for sp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "C:\\Windows\\Fonts\\arial.ttf",
               "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.isfile(sp):
            return sp
    return ""


def ensure_all_fonts():
    for name in FONT_URLS:
        _download_font(name)
