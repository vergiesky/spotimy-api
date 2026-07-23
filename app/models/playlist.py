from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

class Playlist(db.Model):
    __tablename__ = "playlists"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    cover_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    songs = db.relationship("Music", secondary="playlist_music", backref="playlists", lazy="select")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "cover_path": self.cover_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_public_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "cover_path": self.cover_path,
            "total_songs": len(self.songs),
        }

    def __repr__(self):
        return f"<Playlist {self.name}>"

class PlaylistMusic(db.Model):
    __tablename__ = "playlist_music"

    playlist_id = db.Column(UUID(as_uuid=True), db.ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True)
    music_id = db.Column(UUID(as_uuid=True), db.ForeignKey("music.id", ondelete="CASCADE"), primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    added_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))