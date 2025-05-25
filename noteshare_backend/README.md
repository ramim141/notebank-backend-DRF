# NoteShare Backend

The **NoteShare Backend** is a Django-based REST API for a note-sharing platform. It provides functionality for user authentication, note management, ratings, likes, bookmarks, and notifications. This backend is designed to work seamlessly with a frontend application.

---

## Features

- **User Authentication**: 
  - JWT-based authentication using `rest_framework_simplejwt`.
  - Password reset functionality with email notifications.

- **Note Management**:
  - CRUD operations for notes.
  - Filtering, searching, and ordering of notes.

- **Interactions**:
  - Users can like, bookmark, and rate notes.
  - Notifications for likes and ratings.

- **API Documentation**:
  - Swagger and Redoc documentation using `drf-spectacular`.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)
- SQLite (default database)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd noteshare_backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

---

## Configuration

### Environment Variables
Use `python-decouple` to manage environment variables. Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_email@example.com
BASE_API_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:3000
```

---

## API Endpoints

### User Endpoints
- `/api/users/register/` - Register a new user.
- `/api/users/login/` - Login and get a JWT token.
- `/api/users/password-reset/` - Request a password reset email.
- `/api/users/password-reset-confirm/` - Reset the password using the token.

### Note Endpoints
- `/api/notes/` - List, create, retrieve, update, or delete notes.
- `/api/notes/<id>/toggle-like/` - Like or unlike a note.
- `/api/notes/<id>/toggle-bookmark/` - Bookmark or unbookmark a note.

### Rating Endpoints
- `/api/notes/ratings/` - Add or view ratings for notes.

### Notification Endpoints
- `/api/notes/notifications/` - View notifications.

### API Documentation
- `/api/schema/swagger-ui/` - Swagger UI.
- `/api/schema/redoc/` - Redoc documentation.

---

## Project Structure

```
noteshare_backend/
├── noteshare_backend/
│   ├── settings.py       # Project settings
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI configuration
│   ├── asgi.py           # ASGI configuration
├── users/
│   ├── models.py         # User models
│   ├── views.py          # User-related views
│   ├── serializers.py    # User serializers
│   ├── urls.py           # User-related URLs
├── notes/
│   ├── models.py         # Note models
│   ├── views.py          # Note-related views
│   ├── serializers.py    # Note serializers
│   ├── urls.py           # Note-related URLs
│   ├── signals.py        # Notification signals
```

---

## Dependencies

- **Django**: Web framework
- **Django REST Framework**: API development
- **django-filter**: Filtering support
- **django-taggit**: Tagging functionality
- **django-cors-headers**: CORS support
- **drf-spectacular**: API documentation
- **Pillow**: Image handling
- **python-decouple**: Environment variable management

---

## Development

### Running Tests
Run the following command to execute tests:
```bash
python manage.py test
```

### Linting
Use `flake8` for linting:
```bash
pip install flake8
flake8 .
```

---

## Deployment

1. Set `DEBUG=False` in `.env`.
2. Configure `ALLOWED_HOSTS` in `settings.py`.
3. Use a production-ready database (e.g., PostgreSQL).
4. Set up a web server (e.g., Gunicorn, Nginx).

---

## License

This project is licensed under the MIT License.
