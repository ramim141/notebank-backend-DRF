# NoteShare Backend

Django REST + Channels backend for the Note Bank platform. Provides authentication, notes, ratings, bookmarks, public/user note requests, and real-time notifications via WebSockets.

## Features
- JWT auth (access + refresh)
- Notes: CRUD, filtering/search, likes, bookmarks, ratings
- Public note requests (browse + fulfill) and user note requests (create/list)
- Password reset flow (GET validate, POST confirm)
- Real-time notifications (Channels):
  - Public note request: broadcast to all users
  - Note approved: sent to uploader only
  - Comment/Rating: sent to note owner only

## Requirements
- Python 3.10+
- pip/venv
- For WebSockets in multi-process: Redis (recommended)

## Setup
```bash
cd Backend/noteshare_backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

## Environment (.env)
```
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=your_email@example.com
RENDER_EXTERNAL_HOSTNAME=
```

## Run (ASGI)
- Local single-process (no Redis):
  - In `settings.py` ensure:
    - `INSTALLED_APPS` includes `channels`
    - `ASGI_APPLICATION = 'noteshare_backend.asgi.application'`
    - `CHANNEL_LAYERS = { "default": { "BACKEND": "channels.layers.InMemoryChannelLayer" } }`
  - Start server:
    - `uvicorn noteshare_backend.asgi:application --host 127.0.0.1 --port 8000 --reload`
    - or `daphne -p 8000 noteshare_backend.asgi:application`
- Multi-process (recommended): use Redis
  - `CHANNEL_LAYERS = { "default": { "BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": { "hosts": [("127.0.0.1", 6379)] } } }`

## Key Endpoints
- Users: `/api/users/…`
- Notes: `/api/notes/`
- Public note requests:
  - `GET /api/public-note-requests/?status=PENDING`
  - `POST /api/public-note-requests/{id}/fulfill/`
- My note requests:
  - `POST/GET /api/requests/my-note-requests/` (legacy aliases provided)
- Docs: `/api/schema/swagger-ui/`, `/api/schema/redoc/`

## Notifications (Channels)
- WS route: `/ws/notifications/`
- Server emits:
  - Global broadcasts for public requests
  - User-targeted messages for approvals / comments / ratings
- If Redis is not configured and multiple processes are running, in-memory broadcasts won’t cross processes. Use a single ASGI process or Redis.

## Troubleshooting
- WebSocket not connecting: ensure ASGI server + Channels configured
- Admin approval not notifying uploader: use Redis channel layer or single-process ASGI; verify signal logs
- 405/404 on note requests: use `/api/requests/my-note-requests/` or confirm legacy routes are enabled in `notes/urls.py`
- Password reset 400: ensure frontend encodes and backend decodes uid/token; GET validate works

## Project Structure
```
noteshare_backend/
  noteshare_backend/
    settings.py   # Django + Channels config
    asgi.py       # ASGI router (http + websocket)
    urls.py       # REST routes
  notes/
    models.py     # Note, NoteRequest, Notification
    views.py      # ViewSets and list/create views
    signals.py    # Emits notifications on events
    consumers.py  # WebSocket consumer (global + per-user groups)
    urls.py       # Router + custom endpoints
  users/
    models.py, views.py, serializers.py
```

## License
MIT
