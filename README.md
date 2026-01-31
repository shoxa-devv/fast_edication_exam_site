# Fast Education - English Exam Site

A complete English language exam platform with Django backend, HTML frontend, and AI detection capabilities.

## Features

- **4 Exam Categories:**
  - Grammar - Multiple choice questions
  - Translation - Translate from Uzbek to English
  - Writing - Essay writing with AI assistance detection
  - Vocabulary - Word definition questions

- **Django Admin Panel:**
  - Manage questions and categories
  - View all users and their exam history
  - Track AI usage per exam
  - View detailed exam results

- **AI Detection:**
  - Advanced AI detection using Python
  - Real-time AI usage detection
  - Detailed AI usage reports

- **Modern UI:**
  - Clean HTML/CSS/JavaScript frontend
  - Responsive design
  - Progress tracking

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

That's it! The application will:
- Run database migrations
- Create admin user (username: `admin`, password: `admin123`)
- Load initial questions
- Start Django server on http://localhost:8000

### 3. Access the Site

- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## Admin Panel

Login with:
- Username: `admin`
- Password: `admin123`

### Admin Features:
- **Questions Management**: Create, edit, delete questions for each category
- **User Management**: View all users and their exam count
- **Exam Results**: See all exam sessions with scores and AI usage
- **AI Tracking**: View detailed AI detection for each exam

## Project Structure

```
backend/
├── app.py                      # Unified run script (python app.py)
├── manage.py                   # Django management
├── create_admin.py             # Create admin user script
├── exam_site/                  # Django project
│   ├── settings.py
│   └── urls.py
├── exams/                      # Main app
│   ├── models.py              # Database models
│   ├── admin.py               # Admin panel
│   ├── views.py               # API views
│   └── ai_detector.py         # AI detection
├── static/                     # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── requirements.txt
```

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Detection**: Python (NumPy, Scikit-learn)
- **Database**: SQLite (default)

## API Endpoints

- `GET /api/health/` - Health check
- `GET /api/categories/` - Get all categories
- `GET /api/questions/?category=grammar` - Get questions
- `POST /api/detect-ai/` - Detect AI usage
- `POST /api/ai-assist/` - Get AI assistance
- `POST /api/submit-exam/` - Submit exam
- `GET /api/exam-results/<id>/` - Get results

## Development

### Manual Setup

```bash
# Run migrations
python manage.py migrate

# Create admin
python create_admin.py

# Load initial data
python manage.py load_initial_data

# Run server
python manage.py runserver
```

## Notes

- All data is stored in SQLite database (`db.sqlite3`)
- Admin panel is fully customized for exam management
- AI detection works in real-time during writing
- Results page shows AI usage if detected
