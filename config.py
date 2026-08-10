import os
from pathlib import Path

from dotenv import load_dotenv

# __file__ adalah variabel bawaan Python yang berisi lokasi file yang sedang dijalankan
# Path mengubah string tersebut menjadi objek path
# misal : Path(__file__)
# hasil: WindowsPath('D:\Project\spotimy\spotimy-flask\config.py')

# resolve() berfungsi mengubah path menjadi absolut
# parent berarti folder induk dari file tersebut
# misal:
# D:\Project\spotimy\config.py
# maka hasilnya:
# D:\Project\spotimy

# artinya: simpan folder tempat config.py berada ke dalam variabel BASE_DIR

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") or (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SECRET")
    BUCKET_NAME = os.getenv("BUCKET_NAME", "spotimy")

    SQLALCHEMY_TRACK_MODIFICATIONS = False