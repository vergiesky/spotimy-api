import re
from urllib.parse import parse_qs, urlparse

import httpx

YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_youtube_video_id(url):
    parsed_url = urlparse(url if "://" in url else f"https://{url}")
    hostname = parsed_url.netloc.lower().split(":")[0]

    if hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed_url.path.strip("/").split("/")[0]
    elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        parts = [part for part in parsed_url.path.split("/") if part]
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [""])[0]
        elif len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            video_id = parts[1]
        else:
            return None
    else:
        return None

    return video_id if YOUTUBE_VIDEO_ID_PATTERN.fullmatch(video_id) else None


def get_youtube_video_metadata(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    response = httpx.get(
        "https://www.youtube.com/oembed",
        params={"url": video_url, "format": "json"},
        timeout=8,
    )
    response.raise_for_status()
    info = response.json()

    return {
        "title": (info.get("title") or "").strip(),
        "artist": (info.get("author_name") or "").strip(),
        "album": None,
        "cover_path": info.get("thumbnail_url"),
        "duration": None,
        "source_url": video_url,
    }
