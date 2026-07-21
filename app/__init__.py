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
    
    @app.get("/health")
    def health():
        return "OK", 200

    return app
