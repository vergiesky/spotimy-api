# Spotimy API

![Version](https://img.shields.io/badge/version-v1.0.0-brightgreen.svg)

![Python](https://img.shields.io/badge/Python-3.11.9-3776AB.svg?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-3.1.3-000000.svg?logo=flask&logoColor=white) 
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1.svg?logo=postgresql&logoColor=white) ![Supabase](https://img.shields.io/badge/Supabase-2.31.0-3FCF8E.svg?logo=supabase&logoColor=white)

## About / Description

Spotimy API adalah backend untuk aplikasi music streaming Spotimy. Backend ini menangani autentikasi, pengelolaan musik, playlist, streaming audio, dan fitur admin.

## Features

- User authentication dengan JWT.
- Role-based access untuk `user`, `admin`, dan `superadmin`.
- Music library API untuk list, search, detail, dan stream URL.
- Playlist management untuk membuat dan mengelola playlist user.
- Admin music management untuk import, edit, dan hapus musik.
- Superadmin user management untuk mengelola user dan role.
- Supabase Storage integration untuk audio dan cover image.
- YouTube audio import dengan output audio-only `.m4a`.

## Installation / Setup

1. Masuk ke folder backend:

```bash
cd spotimy-api
```

2. Buat virtual environment:

```bash
python -m venv .venv
```

3. Aktifkan virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependency:

```bash
pip install -r requirements.txt
```

5. Install FFmpeg dan pastikan bisa diakses dari terminal:

```bash
ffmpeg -version
```

6. Buat file `.env` dari `.env.example`:

```bash
cp .env.example .env
```

Untuk Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

7. Isi konfigurasi `.env`:

```env
SECRET_KEY=your-secret-key

# Use either SQLALCHEMY_DATABASE_URI or DB_* values.
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost:5432/spotimy
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spotimy
DB_USER=postgres
DB_PASS=password

SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SECRET=your-supabase-service-role-key
BUCKET_NAME=spotimy
```

Gunakan salah satu konfigurasi database: `SQLALCHEMY_DATABASE_URI` atau `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`.

8. Jalankan migration database:

```bash
flask db upgrade
```

## Run

Jalankan server Flask:

```bash
python main.py
```

Secara default backend berjalan di:

```text
http://localhost:3000
```

Untuk mengetes server:

```text
GET /health
```
