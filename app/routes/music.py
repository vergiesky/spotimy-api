from flask import Blueprint, jsonify, request
from uuid import UUID
from app.models import Music
from app.routes.auth import token_required
from app.services.storage import create_signed_url

music_bp = Blueprint("music", __name__)

@music_bp.get("")
def list_music():
    search = (request.args.get("search") or "").strip()

    query = Music.query

    if search:
        query = query.filter(
            (Music.title.ilike(f"%{search}%")) | 
            (Music.artist.ilike(f"%{search}%"))
        )

    songs = query.order_by(Music.title.asc()).all()

    return jsonify({
        "music": [song.to_public_dict() for song in songs]
    }), 200

@music_bp.get("/<music_id>")
def get_music_detail(music_id):
    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    song = Music.query.get(music_uuid)

    if not song:
        return jsonify({"error": "Music not found"}), 404

    return jsonify({"music": song.to_public_dict()}), 200

@music_bp.get("/<music_id>/stream-url")
@token_required
def get_music_stream_url(current_user, music_id):
    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    song = Music.query.get(music_uuid)

    if not song:
        return jsonify({"error": "Music not found"}), 404

    if not song.audio_path:
        return jsonify({"error": "Audio file is not available"}), 404

    expires_in = 3600
    stream_url = create_signed_url(song.audio_path, expires_in=expires_in)

    if not stream_url:
        return jsonify({"error": "Failed to create stream URL"}), 502


    return jsonify({
        "stream_url": stream_url,
        "expires_in": expires_in
    }), 200

