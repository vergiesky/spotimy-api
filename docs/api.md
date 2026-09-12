# Spotimy Flask API Documentation

Base URL:

```text
http://localhost:3000/api
```

## Authentication

Endpoint untuk register, login, cek user login, dan logout.

Semua endpoint yang membutuhkan login harus mengirim header:

```text
Authorization: Bearer <token>
```

### Register

```http
POST /auth/register
```

Request body:

```json
{
  "username": "test",
  "email": "test@example.com",
  "password": "password123"
}
```

Success response:

```json
{
  "message": "User registered successfully",
  "token": "jwt-token",
  "user": {
    "id": "user-id",
    "username": "test",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### Login

```http
POST /auth/login
```

Request body:

```json
{
  "username_or_email": "test@example.com",
  "password": "password123"
}
```

Success response:

```json
{
  "message": "Login successful",
  "token": "jwt-token",
  "user": {
    "id": "user-id",
    "username": "test",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### Get Current User

```http
GET /auth/me
```

Headers:

```text
Authorization: Bearer <token>
```

Success response:

```json
{
  "user": {
    "id": "user-id",
    "username": "test",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### Logout

```http
POST /auth/logout
```

Headers:

```text
Authorization: Bearer <token>
```

Success response:

```json
{
  "message": "Logout successful. Delete the token on the client",
  "user": {
    "id": "user-id",
    "username": "test",
    "email": "test@example.com",
    "role": "user"
  }
}
```

## Music

Endpoint untuk melihat daftar musik, detail musik, dan mengambil signed URL untuk streaming.

### List Music

```http
GET /music
```

Query parameters:

```text
search optional
page   optional, default 1
limit  optional, default 20, max 100
```

Example:

```http
GET /music?search=kano&page=1&limit=10
```

Success response:

```json
{
  "music": [
    {
      "id": "music-id",
      "title": "Music Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration": 274,
      "cover_path": "https://i.ytimg.com/..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Get Music Detail

```http
GET /music/<music_id>
```

Success response:

```json
{
  "music": {
    "id": "music-id",
    "title": "Music Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "duration": 274,
    "cover_path": "https://i.ytimg.com/..."
  }
}
```

### Get Music Stream URL

```http
GET /music/<music_id>/stream-url
```

Headers:

```text
Authorization: Bearer <token>
```

Success response:

```json
{
  "stream_url": "https://signed-url-from-supabase",
  "expires_in": 3600
}
```

Notes:

```text
stream_url digunakan oleh mobile app untuk memutar audio.
URL ini bersifat sementara dan akan expired sesuai expires_in.
```

## Playlists

Endpoint untuk membuat, melihat, mengubah, menghapus playlist, serta mengatur lagu di dalam playlist.

Semua endpoint playlist membutuhkan login.

Headers:

```text
Authorization: Bearer <token>
```

### List Playlists

```http
GET /playlists
```

Success response:

```json
{
  "playlists": [
    {
      "id": "playlist-id",
      "name": "My Playlist",
      "cover_path": "https://signed-url-from-supabase",
      "total_songs": 3
    }
  ]
}
```

### Create Playlist

```http
POST /playlists
```

Request body:

```json
{
  "name": "My Playlist",
  "cover_path": "https://example.com/cover.jpg"
}
```

Success response:

```json
{
  "message": "Playlist created successfully",
  "playlist": {
    "id": "playlist-id",
    "name": "My Playlist",
    "cover_path": "https://example.com/cover.jpg",
    "total_songs": 0
  }
}
```

### Get Playlist Detail

```http
GET /playlists/<playlist_id>
```

Success response:

```json
{
  "playlist": {
    "id": "playlist-id",
    "name": "My Playlist",
    "cover_path": "https://signed-url-from-supabase",
    "total_songs": 2
  },
  "songs": [
    {
      "id": "music-id",
      "title": "Music Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration": 274,
      "cover_path": "https://i.ytimg.com/..."
    }
  ]
}
```

### Update Playlist

```http
PATCH /playlists/<playlist_id>
```

Request body untuk mengubah nama saja:

```json
{
  "name": "Updated Playlist Name"
}
```

Request body untuk mengubah nama dan upload cover:

```text
Content-Type: multipart/form-data

name=Updated Playlist Name
cover=<image-file>
```

Cover rules:

```text
Field file harus bernama cover.
Format yang diterima: JPEG, PNG, WebP.
Ukuran maksimal: 5 MB.
Resolusi maksimal: 20 megapixels.
cover_path tidak boleh dikirim saat update playlist.
```

Success response:

```json
{
  "message": "Playlist updated successfully",
  "playlist": {
    "id": "playlist-id",
    "name": "Updated Playlist Name",
    "cover_path": "https://signed-url-from-supabase",
    "total_songs": 2
  }
}
```

### Delete Playlist

```http
DELETE /playlists/<playlist_id>
```

Success response:

```json
{
  "message": "Playlist deleted successfully"
}
```

Notes:

```text
Jika playlist memiliki cover yang tersimpan di folder playlist-covers/,
backend akan mencoba menghapus file cover tersebut dari Supabase Storage.
```

### Add Song To Playlist

```http
POST /playlists/<playlist_id>/songs
```

Request body:

```json
{
  "music_id": "music-id"
}
```

Success response:

```json
{
  "message": "Music added to playlist successfully",
  "playlist": {
    "id": "playlist-id",
    "name": "My Playlist",
    "cover_path": "https://signed-url-from-supabase",
    "total_songs": 1
  },
  "music": {
    "id": "music-id",
    "title": "Music Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "duration": 274,
    "cover_path": "https://i.ytimg.com/..."
  }
}
```

### Remove Song From Playlist

```http
DELETE /playlists/<playlist_id>/songs/<music_id>
```

Success response:

```json
{
  "message": "Music removed from playlist successfully",
  "playlist": {
    "id": "playlist-id",
    "name": "My Playlist",
    "cover_path": "https://signed-url-from-supabase",
    "total_songs": 0
  },
  "music": {
    "id": "music-id",
    "title": "Music Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "duration": 274,
    "cover_path": "https://i.ytimg.com/..."
  }
}
```

### Reorder Playlist Songs

```http
PATCH /playlists/<playlist_id>/songs/reorder
```

Request body:

```json
{
  "music_ids": [
    "music-id-1",
    "music-id-2",
    "music-id-3"
  ]
}
```

Success response:

```json
{
  "message": "Playlist songs reordered successfully",
  "playlist": {
    "id": "playlist-id",
    "name": "My Playlist",
    "cover_path": "https://signed-url-from-supabase",
    "total_songs": 3
  },
  "songs": [
    {
      "id": "music-id-1",
      "title": "Music Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration": 274,
      "cover_path": "https://i.ytimg.com/..."
    }
  ]
}
```

Notes:

```text
music_ids harus berisi semua music_id yang ada di playlist tersebut.
Urutan array music_ids menentukan posisi lagu di playlist.
```

### Playlist Cover Notes

```text
cover_path pada response playlist bisa berisi null, URL eksternal lama,
atau signed URL Supabase untuk cover yang diupload dari mobile app.
Signed URL bersifat sementara dan bisa berubah saat data playlist diminta ulang.
Client cukup memakai nilai cover_path dari response sebagai image URL.
```

## Admin Music

Endpoint untuk admin atau superadmin mengelola data musik.

Semua endpoint Admin Music membutuhkan login dan role:

```text
admin atau superadmin
```

Headers:

```text
Authorization: Bearer <token>
```

### Add Music From YouTube

```http
POST /admin/music
```

Request body:

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

Success response:

```json
{
  "message": "Music added successfully",
  "music": {
    "id": "music-id",
    "title": "Music Title",
    "artist": "Artist Name",
    "album": null,
    "duration": 274,
    "audio_path": "library/audio-file.m4a",
    "cover_path": "https://i.ytimg.com/...",
    "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "youtube_video_id": "VIDEO_ID",
    "created_by": "user-id",
    "created_at": "2026-08-16T10:00:00+00:00",
    "updated_at": "2026-08-16T10:00:00+00:00"
  }
}
```

Duplicate response:

```json
{
  "error": "Music already exists",
  "music": {
    "id": "music-id",
    "title": "Music Title",
    "artist": "Artist Name",
    "album": null,
    "duration": 274,
    "audio_path": "library/audio-file.m4a",
    "cover_path": "https://i.ytimg.com/...",
    "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "youtube_video_id": "VIDEO_ID",
    "created_by": "user-id",
    "created_at": "2026-08-16T10:00:00+00:00",
    "updated_at": "2026-08-16T10:00:00+00:00"
  }
}
```

### List Music

```http
GET /admin/music
```

Query parameters:

```text
search optional
page   optional, default 1
limit  optional, default 20, max 100
```

Example:

```http
GET /admin/music?search=kano&page=1&limit=10
```

Success response:

```json
{
  "music": [
    {
      "id": "music-id",
      "title": "Music Title",
      "artist": "Artist Name",
      "album": null,
      "duration": 274,
      "audio_path": "library/audio-file.m4a",
      "cover_path": "https://i.ytimg.com/...",
      "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "youtube_video_id": "VIDEO_ID",
      "created_by": "user-id",
      "created_at": "2026-08-16T10:00:00+00:00",
      "updated_at": "2026-08-16T10:00:00+00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Update Music

```http
PATCH /admin/music/<music_id>
```

Request body:

```json
{
  "title": "Updated Title",
  "artist": "Updated Artist",
  "album": "Updated Album",
  "duration": 240,
  "cover_path": "https://example.com/new-cover.jpg"
}
```

Success response:

```json
{
  "message": "Music updated successfully",
  "music": {
    "id": "music-id",
    "title": "Updated Title",
    "artist": "Updated Artist",
    "album": "Updated Album",
    "duration": 240,
    "audio_path": "library/audio-file.m4a",
    "cover_path": "https://example.com/new-cover.jpg",
    "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "youtube_video_id": "VIDEO_ID",
    "created_by": "user-id",
    "created_at": "2026-08-16T10:00:00+00:00",
    "updated_at": "2026-08-16T10:10:00+00:00"
  }
}
```

### Delete Music

```http
DELETE /admin/music/<music_id>
```

Success response:

```json
{
  "message": "Music deleted successfully"
}
```

## Admin Users

Endpoint untuk superadmin mengelola user.

Semua endpoint Admin Users membutuhkan login dan role:

```text
superadmin
```

Headers:

```text
Authorization: Bearer <token>
```

### List Users

```http
GET /admin/users
```

Query parameters:

```text
search optional
page   optional, default 1
limit  optional, default 20, max 100
```

Example:

```http
GET /admin/users?search=test&page=1&limit=10
```

Success response:

```json
{
  "users": [
    {
      "id": "user-id",
      "username": "test",
      "email": "test@example.com",
      "role": "user",
      "created_at": "2026-08-16T10:00:00+00:00",
      "updated_at": "2026-08-16T10:00:00+00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Update User Role

```http
PATCH /admin/users/<user_id>/role
```

Request body:

```json
{
  "role": "admin"
}
```

Valid roles:

```text
user
admin
superadmin
```

Success response:

```json
{
  "message": "User role updated successfully",
  "user": {
    "id": "user-id",
    "username": "test",
    "email": "test@example.com",
    "role": "admin",
    "created_at": "2026-08-16T10:00:00+00:00",
    "updated_at": "2026-08-16T10:10:00+00:00"
  }
}
```

Notes:

```text
Superadmin tidak bisa mengubah role dirinya sendiri.
User yang role-nya diubah harus login ulang agar token JWT membawa role terbaru.
```

### Delete User

```http
DELETE /admin/users/<user_id>
```

Success response:

```json
{
  "message": "User deleted successfully"
}
```

Notes:

```text
Superadmin tidak bisa menghapus akun dirinya sendiri.
Sistem tidak mengizinkan penghapusan superadmin terakhir.
```

## Common Error Responses

Response error menggunakan field:

```json
{
  "error": "Error message"
}
```

### 400 Bad Request

Terjadi ketika request body, query parameter, atau id tidak valid.

Example:

```json
{
  "error": "Invalid music id"
}
```

Example:

```json
{
  "error": "Upload an image using the cover field"
}
```

Example:

```json
{
  "error": "Use JPEG, PNG, or WebP"
}
```

Example:

```json
{
  "error": "Cover must be between 1 byte and 5 MB"
}
```

### 401 Unauthorized

Terjadi ketika endpoint membutuhkan token, tetapi token tidak dikirim, tidak valid, atau expired.

Example:

```json
{
  "error": "Authorization token is required"
}
```

Example:

```json
{
  "error": "Token has expired"
}
```

### 403 Forbidden

Terjadi ketika user login tetapi tidak punya role yang dibutuhkan.

Example:

```json
{
  "error": "You do not have permission to access this resource"
}
```

### 404 Not Found

Terjadi ketika data tidak ditemukan.

Example:

```json
{
  "error": "Music not found"
}
```

### 409 Conflict

Terjadi ketika data yang dibuat sudah ada.

Example:

```json
{
  "error": "Username or email already exists"
}
```

Example:

```json
{
  "error": "Music already exists in playlist"
}
```

### 415 Unsupported Media Type

Terjadi ketika endpoint menerima format request yang tidak didukung.

Example:

```json
{
  "error": "Use JSON or multipart/form-data"
}
```

### 500 Internal Server Error

Terjadi ketika ada error di server.

Example:

```json
{
  "error": "Failed to upload audio"
}
```

### 502 Bad Gateway

Terjadi ketika backend gagal membuat URL dari service eksternal.

Example:

```json
{
  "error": "Failed to create stream URL"
}
```
