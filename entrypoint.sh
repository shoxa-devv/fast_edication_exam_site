#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     🎓  Fast Education Exam Site         ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# Ensure data directory exists for SQLite
mkdir -p /app/data

echo "  🗄️  Running migrations..."
python manage.py migrate --run-syncdb 2>&1 | tail -3

echo "  📦 Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tail -1

echo "  👤 Setting up admin & data..."
python create_admin.py 2>&1

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │  🚀 Server running on port 8000          │"
echo "  │                                          │"
echo "  │  🌐 Site:   http://SERVER_IP             │"
echo "  │  🔧 Admin:  http://SERVER_IP/admin       │"
echo "  │  👤 Login:  admin / admin123             │"
echo "  └──────────────────────────────────────────┘"
echo ""

exec gunicorn exam_site.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
