from flask import Blueprint, jsonify, request
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