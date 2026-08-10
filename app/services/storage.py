from flask import current_app
from supabase import create_client

def get_supabase_client():
    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_KEY")

    if not url or not key:
        return None

    return create_client(url, key)

def create_signed_url(path, expires_in=3600):
    supabase = get_supabase_client()

    if not supabase:
        return None

    bucket_name = current_app.config.get("BUCKET_NAME", "spotimy")

    response = supabase.storage.from_(bucket_name).create_signed_url(path, expires_in)

    if isinstance(response, dict):
        return response.get("signedURL") or response.get("signed_url")

    return None