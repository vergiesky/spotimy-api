import os
import yt_dlp
import uuid

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
        "format": "bestaudio[ext=m4a]/bestaudio", # Prefer m4a (AAC)
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get path of downloaded file
            # info["ext"] might change if "bestaudio" isn"t what we requested, 
            # but usually it respects the ext if available.
            # safe method is to look at the filename created
            filename = ydl.prepare_filename(info)
            
            return {
                "title": info.get("title"),
                "artist": info.get("uploader"), # YouTube channel as artist fallback
                "duration": info.get("duration"),
                "cover_path": info.get("thumbnail"),
                "file_path": filename,
                "file_id": file_id
            }
    except Exception as e:
        print(f"Download error: {e}")
        return None