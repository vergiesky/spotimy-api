import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_youtube_video_id(url):
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        parsed_url = urlparse(f"https://{url}")

    hostname = parsed_url.netloc.lower()

    if hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed_url.path.strip("/").split("/")[0]
    elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        video_id = parse_qs(parsed_url.query).get("v", [""])[0]
    else:
        return None

    if not YOUTUBE_VIDEO_ID_PATTERN.fullmatch(video_id):
        return None

    return video_id
