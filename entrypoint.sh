#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     🎓  Fast Education Exam Site         ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

echo "  🗄️  Running migrations..."
python manage.py migrate --run-syncdb 2>&1 | tail -3

echo "  👤 Setting up admin & data..."
python create_admin.py 2>&1

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │  🚀 Server running on port 8000          │"
echo "  │                                          │"
echo "  │  🌐 Site:   http://localhost:8000        │"
echo "  │  🔧 Admin:  http://localhost:8000/admin  │"
echo "  │  👤 Login:  admin / admin123             │"
echo "  └──────────────────────────────────────────┘"
echo ""

exec python manage.py runserver 0.0.0.0:8000
