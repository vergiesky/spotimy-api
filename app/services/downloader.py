import os
import re
import shutil
import subprocess
import yt_dlp
import uuid
from urllib.parse import parse_qs, urlparse

YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")

class DownloadAudioError(Exception):
    pass

def get_downloaded_file(tmp_dir, file_id):
    for filename in os.listdir(tmp_dir):
        if filename.startswith(f"{file_id}.") and not filename.endswith(".part"):
            return os.path.join(tmp_dir, filename)

    raise DownloadAudioError("Downloaded file was not found")

def convert_to_m4a(file_path, file_id, tmp_dir):
    if file_path.lower().endswith(".m4a"):
        return file_path

    if not shutil.which("ffmpeg"):
        raise DownloadAudioError("FFmpeg is required to convert downloads to m4a")

    output_path = os.path.join(tmp_dir, f"{file_id}.m4a")

    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            file_path,
            "-vn",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            output_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise DownloadAudioError(result.stderr.strip() or "Failed to convert audio to m4a")

    if os.path.exists(file_path):
        os.remove(file_path)

    return output_path

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

def download_audio(url):
    """
    Downloads audio from YouTube URL using yt-dlp
    Returns metadata and file path
    Files are saved in /tmp for Vercel compatibility
    """
    # Use /tmp for Vercel, or a local tmp dir for development
    tmp_dir = "/tmp" if os.path.exists("/tmp") else "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    file_id = str(uuid.uuid4())
    output_template = os.path.join(tmp_dir, f"{file_id}.%(ext)s")

    # yt-dlp options
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best[ext=mp4]/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "remote_components": ["ejs:github"],
        "extractor_args": {
            "youtube": {
                "player_client": ["android"],
            },
        },
    }

    try:
        node_path = shutil.which("node")
        if node_path:
            ydl_opts["js_runtimes"] = {"node": {"path": node_path}}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = get_downloaded_file(tmp_dir, file_id)
            filename = convert_to_m4a(downloaded_file, file_id, tmp_dir)
            
            return {
                "title": info.get("title"),
                "artist": info.get("uploader"), # YouTube channel as artist fallback
                "duration": info.get("duration"),
                "cover_path": info.get("thumbnail"),
                "file_path": filename,
                "file_id": file_id
            }
    except DownloadAudioError:
        raise
    except Exception as error:
        print(f"Download error: {error}")
        raise DownloadAudioError(str(error)) from error
