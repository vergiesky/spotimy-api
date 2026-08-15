from flask import Flask
from app.extensions import db, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extension
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from app import models

    # Blueprint auth
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Blueprint music
    from app.routes.music import music_bp
    app.register_blueprint(music_bp, url_prefix="/api/music")

    # Blueprint playlist
    from app.routes.playlist import playlist_bp
    app.register_blueprint(playlist_bp, url_prefix="/api/playlists")

    # Blueprint admin
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    
    @app.get("/health")
    def health():
        return "OK", 200

    return app
