from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, jsonify, request, current_app

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

def create_access_token(user):
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip().lower()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_auth_dict()
    }), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username_or_email = (data.get("username_or_email") or "").strip().lower()
    password = data.get("password") or ""

    if not username_or_email or not password:
        return jsonify({"error": "Username or email and password are required"}), 400
    
    user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username, email or password"}), 401
    
    token = create_access_token(user)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_auth_dict()
    }), 200

   