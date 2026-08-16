import os
from flask import Blueprint, jsonify, request
from uuid import UUID

from app.extensions import db
from app.models import Music, User
from app.services.downloader import download_audio
from app.services.storage import upload_file, delete_file
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

@admin_bp.get("/music")
@role_required("admin", "superadmin")
def list_music(current_user):
    search = (request.args.get("search") or "").strip()

    query = Music.query

    if search:
        query = query.filter(
            db.or_(
                Music.title.ilike(f"%{search}%"),
                Music.artist.ilike(f"%{search}%"),
            )
        )

    music = query.order_by(Music.created_at.desc()).all()

    return jsonify({"music": [song.to_dict() for song in music]}), 200

@admin_bp.patch("/music/<music_id>/edit")
@role_required("admin", "superadmin")
def update_music(current_user, music_id):
    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    music = Music.query.get(music_uuid)

    if not music:
        return jsonify({"error": "Music not found"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()

        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400

        music.title = title

    if "artist" in data:
        artist = (data.get("artist") or "").strip()

        if not artist:
            return jsonify({"error": "Artist cannot be empty"}), 400

        music.artist = artist

    if "album" in data:
        music.album = (data.get("album") or "").strip() or None

    if "duration" in data:
        duration = data.get("duration")

        if duration is None:
            music.duration = None
        else:
            try:
                duration = int(duration)
            except (TypeError, ValueError):
                return jsonify({"error": "Duration must be an integer"}), 400

            if duration < 0:
                return jsonify({"error": "Duration cannot be negative"}), 400

            music.duration = duration

    if "cover_path" in data:
        music.cover_path = (data.get("cover_path") or "").strip() or None

    db.session.commit()

    return jsonify({
        "message": "Music updated successfully",
        "music": music.to_dict(),
    }), 200

@admin_bp.delete("/music/<music_id>/delete")
@role_required("admin", "superadmin")
def delete_music(current_user, music_id):
    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    music = Music.query.get(music_uuid)

    if not music:
        return jsonify({"error": "Music not found"}), 404

    audio_path = music.audio_path

    try:
        if audio_path:
            delete_file(audio_path)
    except Exception as error:
        return jsonify({
            "error": "Failed to delete audio file",
            "detail": str(error),
        }), 500

    db.session.delete(music)
    db.session.commit()

    return jsonify({"message": "Music deleted successfully"}), 200

@admin_bp.get("/users")
@role_required("superadmin")
def list_users(current_user):
    search = (request.args.get("search") or "").strip().lower()

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.role.ilike(f"%{search}%")
            )
        )

    users = query.order_by(User.created_at.desc()).all()

    return jsonify({"users": [user.to_dict() for user in users]}), 200
