#!/usr/bin/env python3
"""HistoryForge — 04_footage_collector.py — Pexels + Pixabay footage."""

import os, sys, json, time, logging, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_api_key

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Footage] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


class Collector:
    def __init__(self):
        self.pexels = get_api_key("PEXELS")
        self.pixabay = get_api_key("PIXABAY")
        self.s = requests.Session()

    def search_pexels(self, q, n=5):
        if not self.pexels: return []
        try:
            r = self.s.get("https://api.pexels.com/videos/search",
                headers={"Authorization": self.pexels},
                params={"query": q, "per_page": n, "orientation": "landscape"}, timeout=30)
            r.raise_for_status()
            vids = []
            for v in r.json().get("videos", []):
                hd = [f for f in v.get("video_files", [])
                      if f.get("quality") == "hd" and f.get("width", 0) >= 1280]
                if hd:
                    b = max(hd, key=lambda x: x.get("width", 0))
                    vids.append({"url": b["link"], "source": "pexels",
                                 "duration": v.get("duration", 0),
                                 "width": b.get("width", 1920), "height": b.get("height", 1080)})
            return vids
        except Exception as e:
            log.error("Pexels: %s", e); return []

    def search_pixabay(self, q, n=5):
        if not self.pixabay: return []
        try:
            r = self.s.get("https://pixabay.com/api/videos/",
                params={"key": self.pixabay, "q": q, "per_page": n}, timeout=30)
            r.raise_for_status()
            vids = []
            for h in r.json().get("hits", []):
                lg = h.get("videos", {}).get("large", {})
                if lg.get("url"):
                    vids.append({"url": lg["url"], "source": "pixabay",
                                 "duration": h.get("duration", 0),
                                 "width": lg.get("width", 1920), "height": lg.get("height", 1080)})
            return vids
        except Exception as e:
            log.error("Pixabay: %s", e); return []

    def download(self, url, path):
        try:
            r = self.s.get(url, stream=True, timeout=120)
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk: f.write(chunk)
            return True
        except Exception as e:
            log.error("DL fail: %s", e); return False

    def collect(self, script, out_dir="output/footage"):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        dl = []
        for i, sec in enumerate(script.get("sections", [])):
            cue = sec.get("footage_cue", "") or f"{sec.get('type','')} history"
            vids = self.search_pexels(cue, 3) + self.search_pixabay(cue, 2)
            seen = set()
            unique = [v for v in vids if v["url"] not in seen and not seen.add(v["url"])]
            for j, v in enumerate(unique[:2]):
                fp = Path(out_dir) / f"s{i:03d}_{j:02d}_{v['source']}.mp4"
                if fp.exists() or self.download(v["url"], fp):
                    dl.append({"section_index": i, "section_type": sec.get("type",""),
                               "file": str(fp), "source": v["source"],
                               "duration": v["duration"]})
                    time.sleep(0.5)
        with open(Path(out_dir) / "manifest.json", "w") as f:
            json.dump({"total": len(dl), "downloads": dl}, f, indent=2)
        log.info("Downloaded %d clips", len(dl))
        return dl


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--script", required=True)
    p.add_argument("--output", "-o", default="output/footage")
    args = p.parse_args()
    with open(args.script) as f:
        script = json.load(f)
    dl = Collector().collect(script, args.output)
    print(f"\n🎬 {len(dl)} clips → {args.output}")

if __name__ == "__main__":
    main()
