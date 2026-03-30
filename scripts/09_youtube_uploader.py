#!/usr/bin/env python3
"""HistoryForge — 09_youtube_uploader.py — YouTube upload."""

import os, sys, json, time, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.config import get_api_key

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [Upload] %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_yt():
    creds = Credentials(
        token=None,
        refresh_token=get_api_key("YOUTUBE_REFRESH_TOKEN"),
        client_id=get_api_key("YOUTUBE_CLIENT_ID"),
        client_secret=get_api_key("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token")
    return build("youtube", "v3", credentials=creds)


def upload(video_path, title="Documentary", description="", tags=None,
           category="27", privacy="private", thumbnail=None, is_short=False):
    if not os.path.isfile(video_path):
        raise FileNotFoundError(video_path)
    yt = get_yt()
    if is_short and "#shorts" not in title.lower():
        title += " #Shorts"
    body = {"snippet": {"title": title[:100], "description": description,
                        "tags": tags or ["history"], "categoryId": category},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    media = MediaFileUpload(video_path, mimetype="video/mp4",
                            resumable=True, chunksize=10*1024*1024)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None; retries = 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status: log.info("Upload: %d%%", int(status.progress()*100))
        except Exception as e:
            retries += 1
            if retries > 5: raise
            log.warning("Retry %d: %s", retries, e)
            time.sleep(5*retries)
    vid = resp["id"]
    log.info("✅ Uploaded: https://youtube.com/watch?v=%s", vid)
    if thumbnail and os.path.isfile(thumbnail):
        try:
            yt.thumbnails().set(videoId=vid,
                media_body=MediaFileUpload(thumbnail, mimetype="image/png")).execute()
        except: pass
    return vid


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--metadata", default=None)
    p.add_argument("--thumbnail", default=None)
    p.add_argument("--title", default="History Documentary")
    p.add_argument("--description", default="")
    p.add_argument("--tags", default="history,documentary")
    p.add_argument("--category", default="27")
    p.add_argument("--privacy", default="private")
    p.add_argument("--is-short", action="store_true")
    args = p.parse_args()

    if args.metadata and os.path.isfile(args.metadata):
        with open(args.metadata) as f: m = json.load(f)
        title = m.get("title", args.title)
        desc = m.get("description", args.description)
        tags = m.get("tags", args.tags.split(","))
        priv = m.get("privacy_status", args.privacy)
    else:
        title, desc, tags, priv = args.title, args.description, args.tags.split(","), args.privacy

    vid = upload(args.video, title, desc, tags, args.category, priv,
                 args.thumbnail, args.is_short)
    print(f"\n✅ https://youtube.com/watch?v={vid}")

if __name__ == "__main__":
    main()
