import os
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Music
from app.services.downloader import download_audio
from app.services.storage import upload_file
from app.routes.auth import role_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.post("/music/add")
@role_required("admin", "superadmin")
def add_music_from_youtube(current_user):
    data = request.get_json(silent=True) or {}

    youtube_url = (data.get("youtube_url") or "").strip()

    if not youtube_url:
        return jsonify({"error": "youtube_url is required"}), 400

    try:
        audio_data = download_audio(youtube_url)

        if not audio_data:
            return jsonify({"error": "Failed to download audio"}), 400

        file_path = audio_data["file_path"]
        filename = os.path.basename(file_path)
        audio_path = f"library/{filename}"

        with open(file_path, "rb") as file:
            file_content = file.read()

        uploaded_path = upload_file(
            file_content,
            audio_path,
            content_type="audio/mp4",
        )

        if not uploaded_path:
            return jsonify({"error": "Failed to upload audio"}), 500

        music = Music(
            title=audio_data["title"],
            artist=audio_data["artist"],
            duration=audio_data["duration"],
            audio_path=uploaded_path,
            cover_path=audio_data["cover_path"],
            created_by=current_user.id,
        )

        db.session.add(music)
        db.session.commit()

        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "message": "Music added successfully",
            "music": music.to_dict(),
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500