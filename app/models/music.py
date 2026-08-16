from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db

class Music(db.Model):
    __tablename__ = "music"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    audio_path = db.Column(db.String(500), nullable=False)
    cover_path = db.Column(db.String(500))
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "audio_path": self.audio_path,
            "cover_path": self.cover_path,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_public_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "cover_path": self.cover_path,
        }

    def __repr__(self):
        return f"<Music {self.title} by {self.artist}>"