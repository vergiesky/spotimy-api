from flask import Blueprint, jsonify, request
from uuid import UUID
from app.models import Music

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
