#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     Fast Education Exam Site             ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

echo "  Running migrations..."
python manage.py migrate --run-syncdb 2>&1 | tail -3

echo "  Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tail -1

echo "  Setting up data..."
python create_admin.py 2>&1

echo ""
echo "  Server running on port ${PORT:-8000}"
echo ""

exec gunicorn exam_site.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
