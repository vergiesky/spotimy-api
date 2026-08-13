from flask import Blueprint, jsonify, request
from uuid import UUID

from app.extensions import db
from app.models import Playlist, Music
from app.routes.auth import token_required

playlist_bp = Blueprint("playlist", __name__)

@playlist_bp.get("")
@token_required
def list_playlists(current_user):
    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.name.asc()).all()

    return jsonify({"playlists": [playlist.to_public_dict() for playlist in playlists]}), 200

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
        "playlist": playlist.to_public_dict()
    }), 201

@playlist_bp.get("/<playlist_id>")
@token_required
def get_playlist_detail(current_user, playlist_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    playlist = Playlist.query.filter_by(
        id = playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    return jsonify({
        "playlist": playlist.to_public_dict(),
        "songs": [song.to_public_dict() for song in playlist.songs]
    }), 200

@playlist_bp.post("/<playlist_id>/songs")
@token_required
def add_song_to_playlist(current_user, playlist_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    data = request.get_json(silent=True) or {}
    music_id = data.get("music_id") or ""

    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    playlist = Playlist.query.filter_by(
        id = playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    song = Music.query.get(music_uuid)

    if not song:
        return jsonify({"error": "Music not found"}), 404

    if song in playlist.songs:
        return jsonify({"error": "Music already exists in playlist"}), 409

    playlist.songs.append(song)
    db.session.commit()

    return jsonify({
        "message": "Music added to playlist successfully",
        "playlist": playlist.to_public_dict(),
        "music": song.to_public_dict(),
    }), 201
