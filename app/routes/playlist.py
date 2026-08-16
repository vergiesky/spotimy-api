from flask import Blueprint, jsonify, request
from uuid import UUID

from app.extensions import db
from app.models import Playlist, Music, PlaylistMusic
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
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    playlist_songs = (
        db.session.query(Music)
        .join(PlaylistMusic, PlaylistMusic.music_id == Music.id)
        .filter(PlaylistMusic.playlist_id == playlist.id)
        .order_by(PlaylistMusic.position.asc(), PlaylistMusic.added_at.asc())
        .all()
    )

    return jsonify({
        "playlist": playlist.to_public_dict(),
        "songs": [song.to_public_dict() for song in playlist_songs]
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
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    song = Music.query.get(music_uuid)

    if not song:
        return jsonify({"error": "Music not found"}), 404

    # mengecek apakah lagu sudah ada di playlist
    existing_song = PlaylistMusic.query.filter_by(
        playlist_id=playlist.id,
        music_id=song.id
    ).first()

    # Kalau ditemukan, berarti lagu tersebut sudah ada di playlist
    if existing_song:
        return jsonify({"error": "Music already exists in playlist"}), 409

    # mencari nilai position paling besar dari semua lagu yang ada di playlist tersebut
    # contoh:
    # Playlist:
    # Song A -> position 0
    # Song B -> position 1
    # Song C -> position 2
    # MAX(position) = 2
    last_position = (
        db.session.query(db.func.max(PlaylistMusic.position))
        .filter(PlaylistMusic.playlist_id == playlist.id)
        .scalar()
    )

    # kalau playlist masih kosong:
    # last_position = None
    # next_position = 0
    #
    # kalau sudah ada lagu:
    # last_position = 2
    # next_position = 3
    next_position = 0 if last_position is None else last_position + 1

    # membuat object PlaylistMusic baru
    # misalnya:
    # playlist_id = 10
    # music_id    = 25
    # position    = 3
    # artinya:
    # tambahkan music 25 ke playlist 10 pada urutan ke-3
    playlist_music = PlaylistMusic(
        playlist_id=playlist.id,
        music_id=song.id,
        position=next_position,
    )

    # memasukkan object PlaylistMusic yang baru dibuat ke dalam session database
    db.session.add(playlist_music)
    # commit = benar-benar menyimpan perubahan ke database
    db.session.commit()

    return jsonify({
        "message": "Music added to playlist successfully",
        "playlist": playlist.to_public_dict(),
        "music": song.to_public_dict(),
    }), 201

@playlist_bp.delete("/<playlist_id>/songs/<music_id>")
@token_required
def remove_song_from_playlist(current_user, playlist_id, music_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    try:
        music_uuid = UUID(music_id)
    except ValueError:
        return jsonify({"error": "Invalid music id"}), 400

    playlist = Playlist.query.filter_by(
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    
    song = Music.query.get(music_uuid)

    if not song:
        return jsonify({"error": "Music not found"}), 404

    if song not in playlist.songs:
        return jsonify({"error": "Music is not in playlist"}), 404

    playlist.songs.remove(song)
    db.session.commit()

    return jsonify({
        "message": "Music removed from playlist successfully",
        "playlist": playlist.to_public_dict(),
        "music": song.to_public_dict(),
    }), 200

@playlist_bp.delete("/<playlist_id>")
@token_required
def delete_playlist(current_user, playlist_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    playlist = Playlist.query.filter_by(
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    db.session.delete(playlist)
    db.session.commit()

    return jsonify({"message": "Playlist deleted successfully"}), 200

@playlist_bp.patch("/<playlist_id>")
@token_required
def update_playlist(current_user, playlist_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    playlist = Playlist.query.filter_by(
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    cover_path = data.get("cover_path")

    if name is not None:
        name = name.strip()

        if not name:
            return jsonify({"error": "Playlist name cannot be empty"}), 400

        playlist.name = name

    if cover_path is not None:
        playlist.cover_path = cover_path.strip() or None

    db.session.commit()

    return jsonify({
        "message": "Playlist updated successfully",
        "playlist": playlist.to_public_dict()
    }), 200

@playlist_bp.patch("/<playlist_id>/songs/reorder")
@token_required
def reorder_playlist_songs(current_user, playlist_id):
    try:
        playlist_uuid = UUID(playlist_id)
    except ValueError:
        return jsonify({"error": "Invalid playlist id"}), 400

    playlist = Playlist.query.filter_by(
        id=playlist_uuid,
        user_id=current_user.id
    ).first()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    data = request.get_json(silent=True) or {}
    music_ids = data.get("music_ids") or []

    if not isinstance(music_ids, list):
        return jsonify({"error": "music_ids must be a list"}), 400

    playlist_music_items = PlaylistMusic.query.filter_by(
        playlist_id=playlist.id
    ).all()

    playlist_music_by_music_id = {
        str(item.music_id): item
        for item in playlist_music_items
    }

    if set(music_ids) != set(playlist_music_by_music_id.keys()):
        return jsonify({"error": "music_ids must match all songs in the playlist"}), 400

    for position, music_id in enumerate(music_ids):
        playlist_music_by_music_id[music_id].position = position

    db.session.commit()

    playlist_songs = (
        db.session.query(Music)
        .join(PlaylistMusic, PlaylistMusic.music_id == Music.id)
        .filter(PlaylistMusic.playlist_id == playlist.id)
        .order_by(PlaylistMusic.position.asc(), PlaylistMusic.added_at.asc())
        .all()
    )

    return jsonify({
        "message": "Playlist songs reordered successfully",
        "playlist": playlist.to_public_dict(),
        "songs": [song.to_public_dict() for song in playlist_songs]
    }), 200