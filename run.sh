#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/.venv"
PORT=8000

# Kill old Django processes
pkill -9 -f "manage.py runserver" 2>/dev/null || true
sleep 2

# Find free port
while ss -tln 2>/dev/null | grep -q ":${PORT} "; do
    PORT=$((PORT+1))
done

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     🎓  Fast Education Exam Site         ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo "  📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "  📦 Installing dependencies..."
pip install --quiet --upgrade pip setuptools wheel 2>/dev/null
pip install --quiet -r "$BACKEND_DIR/requirements.txt" 2>/dev/null

cd "$BACKEND_DIR"

echo "  🗄️  Migrating database..."
python manage.py migrate --run-syncdb 2>&1 | tail -1

echo "  👤 Setting up data..."
python create_admin.py 2>&1

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │  🚀 Server running on port $PORT"
echo "  │"
echo "  │  🌐 Site:   http://localhost:$PORT"
echo "  │  🔧 Admin:  http://localhost:$PORT/admin"
echo "  │  👤 Login:  admin / admin123"
echo "  │"
echo "  │  Press Ctrl+C to stop"
echo "  └──────────────────────────────────────────┘"
echo ""

exec python manage.py runserver "0.0.0.0:$PORT"
