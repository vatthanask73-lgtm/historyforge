#!/usr/bin/env python3
"""
HistoryForge — utils/config.py
Centralised configuration management.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("config")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "config"
OUTPUT_DIR = REPO_ROOT / "output"
TEMP_DIR = REPO_ROOT / "temp"

_settings_cache = None


def _read_yaml(path):
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        data = {}
        current_section = None
        with open(path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.rstrip()
                stripped = line.lstrip()
                if not stripped or stripped.startswith("#"):
                    continue
                indent = len(line) - len(stripped)
                if ":" not in stripped:
                    continue
                key, _, val = stripped.partition(":")
                key = key.strip().strip('"').strip("'")
                val = val.strip().strip('"').strip("'")
                if not val:
                    current_section = key
                    data[key] = {}
                elif indent > 0 and current_section:
                    data[current_section][key] = _auto_cast(val)
                else:
                    current_section = None
                    data[key] = _auto_cast(val)
        return data


def _auto_cast(val):
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1]
        parts = [v.strip().strip('"').strip("'") for v in inner.split(",")]
        return [_auto_cast(p) for p in parts]
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def load_settings(force_reload=False):
    global _settings_cache
    if _settings_cache and not force_reload:
        return _settings_cache

    settings_path = CONFIG_DIR / "settings.yaml"
    if settings_path.is_file():
        data = _read_yaml(settings_path)
    else:
        data = _default_settings()

    for env_key, env_val in os.environ.items():
        if env_key.startswith("HF_"):
            parts = env_key[3:].lower().split("__")
            node = data
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = _auto_cast(env_val)

    _settings_cache = data
    return data


def _default_settings():
    return {
        "channel_name": "Chronicles Unveiled",
        "channel_tagline": "Where History Comes Alive",
        "default_voice": "en-US-GuyNeural",
        "default_duration": 15,
        "default_style": "documentary",
        "color_scheme": {"primary": "#c4a44a", "secondary": "#1a1a2e",
                         "background": "#0a0a0a", "text": "#ffffff"},
        "fonts": {"heading": "Cinzel", "body": "Inter", "caption": "Roboto"},
        "video": {"resolution": [1920, 1080], "fps": 30, "bitrate": "10M",
                  "format": "mp4", "codec": "libx264"},
        "audio": {"music_volume": 0.15, "narration_volume": 1.0, "sfx_volume": 0.5},
        "schedule": {"videos_per_week": 3,
                     "preferred_days": ["Monday", "Wednesday", "Friday"],
                     "preferred_time": "14:00", "timezone": "US/Eastern"},
    }


def get_api_key(name):
    env_map = {
        "GEMINI": "GEMINI_API_KEY",
        "PEXELS": "PEXELS_API_KEY",
        "PIXABAY": "PIXABAY_API_KEY",
        "YOUTUBE_CLIENT_ID": "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CLIENT_SECRET": "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN": "YOUTUBE_REFRESH_TOKEN",
    }
    env_var = env_map.get(name.upper(), name.upper())
    val = os.environ.get(env_var, "")
    if not val:
        log.warning("API key '%s' (env: %s) is not set.", name, env_var)
    return val


def get_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def get_temp_dir():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def load_topics_database():
    db_path = CONFIG_DIR / "topics_database.json"
    if db_path.is_file():
        with open(db_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"categories": {}}


def load_voice_profiles():
    vp_path = CONFIG_DIR / "voice_profiles.yaml"
    if vp_path.is_file():
        return _read_yaml(vp_path)
    return {}


def load_style_presets():
    sp_path = CONFIG_DIR / "style_presets.yaml"
    if sp_path.is_file():
        return _read_yaml(sp_path)
    return {}
