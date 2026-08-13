from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Playlist
from app.routes.auth import token_required

playlist_bp = Blueprint("playlist", __name__)

@playlist_bp.get("")
@token_required
def list_playlists(current_user):
    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.name.asc()).all()

    return jsonify({"playlist": [playlist.to_public_dict() for playlist in playlists]}), 200

@playlist_bp.post("")
@token_required
def create_playlist(current_user):
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    cover_path = (data.get("cover_path") or "").strip() or None

    if not name:
        return jsonify({"error": "Playlist name is required"}), 400

    playlist = Playlist(user_id=current_user.id, name=name, cover_path=cover_path)

    db.session.add(playlist)
    db.session.commit()

    return jsonify({
        "message": "Playlist created successfully",
        "playlists": playlist.to_public_dict()
    }), 201