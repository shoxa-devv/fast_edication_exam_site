# Fast Education Exam Site - Django Backend

Django backend with admin panel for managing English exam questions and tracking student results.

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
cd ..
./run.sh
```

This will:
- Run database migrations
- Start Django server
- Create a Cloudflare tunnel and provide a **Public URL**
- Serve the frontend
- Create admin user if needed (username: `admin`, password: `admin123`)

### 3. Access the Site

Use the **Public URL** (e.g., `https://...trycloudflare.com`) displayed in the terminal:
- **Frontend**: `[Public URL]`
- **Admin Panel**: `[Public URL]/admin`
- **API**: `[Public URL]/api/`


## Admin Panel Features

### Question Management
- Create, edit, delete questions
- Organize by categories (Grammar, Translation, Writing, Vocabulary)
- Set correct answers and points
- Enable/disable questions

### User Management
- View all users
- See exam count for each user
- Filter and search users

### Exam Results
- View all exam sessions
- See scores and AI usage
- Filter by completion status
- View detailed answers and AI detection

### AI Usage Tracking
- Track AI usage per question
- View confidence scores
- See detected patterns

## Database Models

- **Category**: Exam categories (Grammar, Translation, Writing, Vocabulary)
- **Question**: Questions with options, correct answers, points
- **ExamSession**: User exam sessions
- **Answer**: User answers to questions
- **AIUsage**: AI detection records

## API Endpoints

- `GET /api/health/` - Health check
- `GET /api/categories/` - Get all categories
- `GET /api/questions/?category=grammar` - Get questions by category
- `POST /api/detect-ai/` - Detect AI usage in text
- `POST /api/ai-assist/` - Get AI writing assistance
- `POST /api/submit-exam/` - Submit exam results
- `GET /api/exam-results/<exam_id>/` - Get exam results

## Creating Admin User Manually

If admin user is not created automatically:

```bash
python create_admin.py
```

Or use Django shell:

```bash
python manage.py createsuperuser
```

## Loading Initial Data

Initial categories and sample questions are loaded automatically on first run.

To reload:

```bash
python manage.py load_initial_data
```

## Development

Run migrations manually:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
```

## Project Structure

```
backend/
├── app.py                      # Unified run script
├── manage.py                   # Django management
├── exam_site/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── exams/                      # Main app
│   ├── models.py              # Database models
│   ├── admin.py               # Admin panel customization
│   ├── views.py               # API views
│   ├── urls.py                # API URLs
│   ├── ai_detector.py         # AI detection logic
│   └── management/
│       └── commands/
│           └── load_initial_data.py
├── static/                     # Frontend files
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── requirements.txt
```
