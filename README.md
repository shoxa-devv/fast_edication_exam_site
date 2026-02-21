# Fast Education — English Exam Site

Modern English exam platform with Django backend, Jazzmin-style admin panel, and AI copy/translation detection.

## Quick Start

```bash
./run.sh
```

That's it. Open http://localhost:8000 in your browser.

**Admin panel:** http://localhost:8000/admin  
**Login:** `admin` / `admin123`

## Features

| Feature | Description |
|---|---|
| 4 Exam Parts | Grammar, Translation, Writing, Vocabulary |
| Admin Panel | Full question CRUD, user tracking, exam results |
| AI Detection | Detects copied/translated/AI-generated text |
| Timer | Live exam timer |
| Results | Score + AI usage report at the end |

## Tech Stack

- **Backend:** Django 4.2, DRF
- **Frontend:** Vanilla HTML / CSS / JS (served by Django)
- **AI Detection:** Python (NumPy, pattern matching)
- **Database:** SQLite

## Project Structure

```
├── run.sh                  ← one command to start everything
├── backend/
│   ├── manage.py
│   ├── create_admin.py
│   ├── requirements.txt
│   ├── exam_site/          ← Django settings & URLs
│   ├── exams/              ← models, admin, views, AI detector
│   └── static/             ← frontend (HTML, CSS, JS)
└── .venv/                  ← auto-created by run.sh
```
