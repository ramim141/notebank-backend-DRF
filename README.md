# 🎓 EduMetro - University Companion Platform

EduMetro is a comprehensive academic web platform designed for **Metropolitan University** students and faculty. It provides essential features like authentication, academic tracking, notes sharing, and more — all in one centralized ecosystem.

> 🧩 **Motto:** "A platform where Metropolitan University students gain all they need, when they need."

---

## 🌟 Key Features (Phase 1)

### 🔐 Authentication & User Roles
- Secure registration and login with JWT tokens
- Role-based system: `Student`, `Faculty`, `Admin`
- Email verification after registration (Gmail SMTP)
- Logout with refresh token blacklisting
- Profile info editing (Coming soon)

### 🧑‍🎓 Student Features
- View personal dashboard
- Access class routine, notices
- Download & share academic notes
- Track academic progress by semester

### 👨‍🏫 Faculty Features
- Upload routines, post notices
- Share notes
- Manage academic content

### 🛠 Admin Features
- Full control panel (CRUD on everything)
- Approve/reject uploads, monitor user activities
- Manage bus routes, faculty list, results, notices

---

## 🧰 Tech Stack

| Layer       | Tools / Frameworks                     |
|-------------|----------------------------------------|
| Backend     | Django, Django Rest Framework (DRF)    |
| Auth        | JWT (SimpleJWT)                        |
| Email       | Gmail SMTP + `django.core.mail`        |
| Env Config  | `python-decouple`, `.env`              |
| Database    | SQLite (for dev) / PostgreSQL (prod)   |
| Deployment  | Render / Heroku / Docker (optional)    |

---

## 📁 Project Structure

```
edumetro/
├── edumetro/         # Project settings
├── users/            # Custom user model, auth views
├── manage.py
├── .env
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/edumetro.git
cd edumetro
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` File

```bash
touch .env
```

Paste:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

> 🔐 **Note:** Use Gmail App Password for secure email sending.

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Start Server

```bash
python manage.py runserver
```

---

## 📬 Email Verification Workflow

- User registers with email & password
- System sends verification link via Gmail
- Email token expires after configurable time
- Login not allowed until verified

---

## 🔄 API Endpoints (Phase 1)

| Method | Endpoint                     | Description                     |
|--------|------------------------------|---------------------------------|
| POST   | `/api/auth/register/`        | Register student/faculty       |
| POST   | `/api/auth/login/`           | Login and get JWT tokens       |
| GET    | `/api/auth/verify-email/`    | Verify user email              |
| POST   | `/api/auth/logout/`          | Blacklist refresh token        |
| GET    | `/api/user/profile/`         | View profile (upcoming)        |

---

## 🔐 JWT Auth Flow

- Login returns `access` and `refresh` tokens
- Include access token in headers:

```http
Authorization: Bearer your_access_token
```

- Logout invalidates refresh token

---

## ✅ Completed Tasks

- [x] Custom User Model
- [x] Role-based Registration & Login
- [x] JWT Token Setup
- [x] Email Verification with Gmail
- [x] Secure Logout
- [x] `.env` & Gmail SMTP Integration

---

## 🧩 Upcoming Modules

| Module                | Description                                        |
|------------------------|----------------------------------------------------|
| 📅 Class Routine       | View by batch/section or faculty                   |
| 🧠 Progress Tracker    | GPA/CGPA tracking by semester                      |
| 📚 Notes Platform      | Upload/share/search/download notes                |
| 🗞️ Notice Board        | Real-time notices from admin/faculty              |
| 🚌 Bus Schedule        | Timings, map routes                               |
| 🧑‍🏫 Faculty Directory | View departments, emails, social links             |
| 🧑‍🎓 Student Directory | Internal searchable list (optional phase 2)        |

---

## 📦 Optional Advanced Features (Future)

- Dark Mode UI toggle  
- In-app chat (student ↔️ faculty)  
- Event Calendar (sync with Google Calendar)  
- Lost & Found Board  
- Course Registration Assistant  
- Polls & Surveys  
- Academic Calendar Viewer  
- Push Notifications (FCM/Websocket)  
- Mobile App (React Native / Flutter)

---

## 🧪 Testing

- Use **Postman** or **Thunder Client** to test APIs.
- Ensure email verification before login.
- Token refresh/blacklist tests for security.

---

## 📄 License

This project is built for academic and internal development purposes for Metropolitan University.  
Contact author for any production deployment, contribution, or fork use.

---

## 👨‍💻 Author

**Ramim Ahmed**  
Metropolitan University  
📧 [your_email@example.com]  
🌐 GitHub: [github.com/yourusername](https://github.com/yourusername)

---

> 🔖 Don't forget to ⭐ the repository and contribute your ideas!