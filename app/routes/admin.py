import os
from uuid import UUID, uuid4

import httpx
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Music, User, UserRole
from app.routes.auth import role_required
from app.services.storage import delete_file, upload_file
from app.services.youtube import extract_youtube_video_id
from app.utils import get_pagination_params, pagination_meta

admin_bp = Blueprint("admin", __name__)

MAX_AUDIO_UPLOAD_SIZE = 30 * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {
    ".aac",
    ".m4a",
    ".mp3",
}

def get_audio_content_type(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    return {
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".mp3": "audio/mpeg",
        ".aac": "audio/aac",
        ".opus": "audio/ogg",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
    }.get(extension, "application/octet-stream")

def get_youtube_metadata(youtube_url, youtube_video_id):
    metadata = {
        "title": f"YouTube video {youtube_video_id}",
        "artist": "YouTube",
        "cover_path": f"https://img.youtube.com/vi/{youtube_video_id}/hqdefault.jpg",
    }

    try:
        response = httpx.get(
            "https://www.youtube.com/oembed",
            params={"url": youtube_url, "format": "json"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return metadata

    title = (data.get("title") or "").strip()
    author = (data.get("author_name") or "").strip()
    thumbnail_url = (data.get("thumbnail_url") or "").strip()

    if title:
        metadata["title"] = title

    if author:
        metadata["artist"] = author

    if thumbnail_url:
        metadata["cover_path"] = thumbnail_url

    return metadata

def clean_up_uploaded_audio(path):
    try:
        delete_file(path)
    except Exception:
        current_app.logger.exception("Failed to clean up uploaded audio")

@admin_bp.post("/music")
@role_required("admin", "superadmin")
def add_music(current_user):
    if request.mimetype != "multipart/form-data":
        return jsonify({"error": "Use multipart/form-data"}), 415

    data = request.form
    uploaded_path = None

    youtube_url = (data.get("youtube_url") or "").strip()

    if not youtube_url:
        return jsonify({"error": "youtube_url is required"}), 400

    youtube_video_id = extract_youtube_video_id(youtube_url)

    if not youtube_video_id:
        return jsonify({"error": "Invalid YouTube video URL"}), 400

    existing_music = Music.query.filter_by(youtube_video_id=youtube_video_id).first()

    if existing_music:
        return jsonify({
            "error": "Music already exists",
            "music": existing_music.to_dict(),
        }), 409

    audio_file = request.files.get("audio_file")

    if audio_file is None:
        return jsonify({"error": "audio_file is required"}), 400

    original_filename = audio_file.filename or ""
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        return jsonify({"error": "Use MP3, M4A, or AAC audio"}), 400

    file_content = audio_file.read(MAX_AUDIO_UPLOAD_SIZE + 1)

    if not file_content:
        return jsonify({"error": "Audio file cannot be empty"}), 400

    if len(file_content) > MAX_AUDIO_UPLOAD_SIZE:
        return jsonify({"error": "Audio file must not exceed 30 MB"}), 400

    detected_content_type = audio_file.mimetype or ""
    content_type = get_audio_content_type(original_filename)

    if detected_content_type and detected_content_type != "application/octet-stream":
        content_type = detected_content_type

    audio_path = f"library/{uuid4().hex}{extension}"
    metadata = get_youtube_metadata(youtube_url, youtube_video_id)

    try:
        uploaded_path = upload_file(
            file_content,
            audio_path,
            content_type=content_type,
        )

        if not uploaded_path:
            return jsonify({"error": "Failed to upload audio"}), 500

        music = Music(
            title=metadata["title"],
            artist=metadata["artist"],
            duration=None,
            audio_path=uploaded_path,
            cover_path=metadata["cover_path"],
            source_url=youtube_url,
            youtube_video_id=youtube_video_id,
            created_by=current_user.id,
        )

        db.session.add(music)
        db.session.commit()

        return jsonify({
            "message": "Music added successfully",
            "music": music.to_dict(),
        }), 201

    except IntegrityError:
        db.session.rollback()

        if uploaded_path:
            clean_up_uploaded_audio(uploaded_path)

        existing_music = Music.query.filter_by(youtube_video_id=youtube_video_id).first()

        return jsonify({
            "error": "Music already exists",
            "music": existing_music.to_dict() if existing_music else None,
        }), 409

    except Exception as error:
        db.session.rollback()
        current_app.logger.exception("Failed to add music")

        if uploaded_path:
            clean_up_uploaded_audio(uploaded_path)

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

    page, limit = get_pagination_params()

    pagination = query.order_by(Music.created_at.desc()).paginate(
        page=page,
        per_page=limit,
        error_out=False,
    )

    return jsonify({
        "music": [song.to_dict() for song in pagination.items],
        "pagination": pagination_meta(pagination),
    }), 200

@admin_bp.patch("/music/<music_id>")
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

@admin_bp.delete("/music/<music_id>")
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
        current_app.logger.exception("Failed to delete audio file")

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
            )
        )

    page, limit = get_pagination_params()

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=limit,
        error_out=False,
    )

    return jsonify({
        "users": [user.to_dict() for user in pagination.items],
        "pagination": pagination_meta(pagination),
    }), 200

@admin_bp.patch("/users/<user_id>/role")
@role_required("superadmin")
def update_role(current_user, user_id):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user id"}), 400

    user = User.query.get(user_uuid)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.id == current_user.id:
        return jsonify({"error": "You cannot change your own role"}), 400

    data = request.get_json(silent=True) or {}
    role = (data.get("role") or "").strip().lower()

    valid_roles = [user_role.value for user_role in UserRole]

    if role not in valid_roles:
        return jsonify({"error": "Invalid role"}), 400

    user.role = UserRole(role)

    db.session.commit()

    return jsonify({
        "message": "User role updated successfully",
        "user": user.to_dict()
    }), 200

@admin_bp.delete("/users/<user_id>")
@role_required("superadmin")
def delete_user(current_user, user_id):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user id"}), 400

    user = User.query.get(user_uuid)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.id == current_user.id:
        return jsonify({"error": "You cannot delete your own account"}), 400

    if user.role == UserRole.SUPERADMIN:
        superadmin_count = User.query.filter_by(role=UserRole.SUPERADMIN).count()

        if superadmin_count <= 1:
            return jsonify({"error": "Cannot delete the last superadmin account"}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
    
