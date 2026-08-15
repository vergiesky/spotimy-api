from datetime import datetime, timedelta, timezone
from functools import wraps
from uuid import UUID

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

def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.removeprefix("Bearer ").strip()

def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        token = get_bearer_token()

        if not token:
            return jsonify({"error": "Authorization token is required"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )

            user_id = UUID(payload["sub"])

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401

        except (jwt.InvalidTokenError, KeyError, ValueError):
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 401

        return view(user, *args, **kwargs)

    return wrapped

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @token_required
        def wrapped(current_user, *args, **kwargs):
            has_permission = any(current_user.has_role(role) for role in roles)

            if not has_permission:
                return jsonify({"error": "You do not have permission to access this resource"}), 403

            return view(current_user, *args, **kwargs)

        return wrapped

    return decorator

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

@auth_bp.get("/me")
@token_required
def me(current_user):
    return jsonify({"user": current_user.to_auth_dict()}), 200

@auth_bp.post("/logout")
@token_required
def logout(current_user):
    return jsonify({
        "message": "Logout successful. Delete the token on the client",
        "user": current_user.to_auth_dict()
    }), 200