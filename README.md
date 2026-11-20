# Task Manager REST API

A scalable, secure RESTful API built with **Python**, **Django**, and **Django REST Framework (DRF)**. It provides complete CRUD operations for task scheduling, priority tagging, and user-defined categories with strict token-based authentication and granular permission controls.

---

## 🚀 Key Highlights & Architectural Features

- **Decoupled RESTful Architecture:** Clean separation of concerns with Django REST Framework ViewSets and Routers.
- **Token-based Authentication:** Secure endpoints using DRF's `authtoken` architecture with user registration, login, logout, and token revocation.
- **Granular Permission Classes (`IsOwner`):** Custom permission enforcement ensuring users can strictly view, modify, or delete only their own tasks and categories (preventing unauthorized cross-tenant data access).
- **Model Serializers & Schema Validation:** Automated JSON parsing, strict input validation (e.g., preventing past due dates, title length constraints, and ownership verification on category relations).
- **Advanced Querying:** Built-in searching (`?search=`), multi-field ordering (`?ordering=due_date`), and filtering by status, priority, or category.
- **Automated Test Suite:** Comprehensive unit test coverage validating registration, authentication, permission boundaries, and error codes.
- **Postman Ready:** Ready-to-import Postman Collection v2.1 with automated token extraction.

---

## 🛠️ Tech Stack

- **Language:** Python 3.13+
- **Framework:** Django 6.x
- **API Toolkit:** Django REST Framework (DRF)
- **Database:** SQLite (default for development; easily configurable to MySQL / PostgreSQL in `settings.py`)
- **Authentication:** DRF TokenAuthentication
- **Testing:** Django Test Runner & APITestCase, Postman

---

## 📁 Project Structure

```text
Task Manager REST API/
├── accounts/                  # User management & authentication app
│   ├── models.py
│   ├── serializers.py         # Register, Login, and User serializers
│   ├── views.py               # Register, Login, Logout, Profile API views
│   └── urls.py                # /api/auth/* routes
├── tasks/                     # Task & Category core domain app
│   ├── admin.py               # Django Admin configuration
│   ├── models.py              # Category and Task database models
│   ├── permissions.py         # Custom granular permission classes (IsOwner)
│   ├── serializers.py         # Model serializers with custom validators
│   ├── views.py               # ViewSets for Category & Task with custom actions
│   ├── tests.py               # 8 automated API unit test cases
│   └── urls.py                # /api/tasks and /api/categories routes
├── taskmanager/               # Project configuration root
│   ├── settings.py            # DRF settings, installed apps, database config
│   ├── urls.py                # Main URL router & API discovery root
│   └── wsgi.py
├── postman_collection.json    # Complete Postman v2.1 collection
├── requirements.txt           # Project dependencies
├── manage.py
└── README.md
```

---

## ⚡ Quick Start / How to Run

### 1. Activate Virtual Environment
```powershell
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# On Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies (if starting fresh)
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. (Optional) Create Superuser for Django Admin
```bash
python manage.py createsuperuser
```

### 5. Start the Development Server
```bash
python manage.py runserver
```
The API will be live at `http://127.0.0.1:8000/`.

---

## 🧪 Running Automated Tests

Run the full test suite verifying endpoints, authentication, and permissions:
```bash
python manage.py test
```

---

## 📬 API Endpoints Reference

### 🔐 Authentication (`/api/auth/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user & receive Auth Token | No |
| `POST` | `/api/auth/login/` | Authenticate user & get Auth Token | No |
| `POST` | `/api/auth/logout/` | Invalidate / delete current user Token | Yes (`Token <key>`) |
| `GET` | `/api/auth/profile/` | Fetch authenticated user details | Yes (`Token <key>`) |

### 📂 Categories (`/api/categories/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/categories/` | List user's categories | Yes |
| `POST` | `/api/categories/` | Create a new user category | Yes |
| `GET` | `/api/categories/<id>/` | Retrieve specific category details | Yes (Owner only) |
| `PUT/PATCH` | `/api/categories/<id>/` | Update category | Yes (Owner only) |
| `DELETE` | `/api/categories/<id>/` | Delete category | Yes (Owner only) |

### 📝 Tasks (`/api/tasks/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/tasks/` | List tasks (Supports `?priority=`, `?status=`, `?search=`, `?ordering=`) | Yes |
| `POST` | `/api/tasks/` | Create a new task (Validates category ownership & due date) | Yes |
| `GET` | `/api/tasks/<id>/` | Retrieve single task | Yes (Owner only) |
| `PUT/PATCH` | `/api/tasks/<id>/` | Update task fields (Title, Priority, Status, etc.) | Yes (Owner only) |
| `POST` | `/api/tasks/<id>/mark-completed/` | Quick-action endpoint to mark status as `COMPLETED` | Yes (Owner only) |
| `GET` | `/api/tasks/summary/` | Get statistics (total, pending, completed, urgent tasks) | Yes |
| `DELETE` | `/api/tasks/<id>/` | Delete task | Yes (Owner only) |

---

## 📮 Testing with Postman

1. Open **Postman**.
2. Click **Import** (top left).
3. Select `postman_collection.json` located in the root of this project.
4. Run the **"Login"** request: The test script inside the collection automatically captures the token and saves it into the `{{token}}` variable.
5. All subsequent Category and Task requests will automatically use this token!
