#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/.venv"
PORT=8000
CLOUDFLARED="/tmp/cloudflared"

pkill -9 -f "manage.py runserver" 2>/dev/null || true
pkill -9 -f "cloudflared" 2>/dev/null || true
sleep 1

while ss -tln 2>/dev/null | grep -q ":${PORT} "; do
    PORT=$((PORT+1))
done

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     Fast Education Exam Site             ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "  Creating virtual environment..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "  Installing dependencies..."
pip install --upgrade pip setuptools wheel 2>&1 | tail -1
pip install -r "$BACKEND_DIR/requirements.txt" 2>&1 | tail -3

cd "$BACKEND_DIR"

if [ -f db.sqlite3 ]; then
    echo "  Removing old database (schema changed)..."
    rm -f db.sqlite3
fi

echo "  Running migrations..."
python manage.py migrate --run-syncdb 2>&1 | tail -3

echo "  Setting up data..."
python create_admin.py 2>&1

# Download cloudflared if not present
if [ ! -x "$CLOUDFLARED" ]; then
    echo "  Downloading cloudflared tunnel..."
    curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$CLOUDFLARED"
    chmod +x "$CLOUDFLARED"
fi

echo ""
echo "  Starting Django server..."
python manage.py runserver "0.0.0.0:$PORT" &
DJANGO_PID=$!
sleep 2

echo "  Starting public tunnel..."
echo ""
$CLOUDFLARED tunnel --url "http://localhost:$PORT" 2>&1 &
TUNNEL_PID=$!
sleep 4

echo ""
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │                                                          │"
echo "  │  LOCAL:   http://localhost:$PORT                         │"
echo "  │  ADMIN:   http://localhost:$PORT/admin                   │"
echo "  │  LOGIN:   admin / admin123                               │"
echo "  │                                                          │"
echo "  │  PUBLIC LINK yuqorida ko'rsatilgan                       │"
echo "  │  (https://xxx.trycloudflare.com)                         │"
echo "  │                                                          │"
echo "  │  Shu linkni do'stlaringizga yuboring!                    │"
echo "  │                                                          │"
echo "  │  Press Ctrl+C to stop                                    │"
echo "  └──────────────────────────────────────────────────────────┘"
echo ""

cleanup() {
    echo ""
    echo "  Stopping..."
    kill $DJANGO_PID 2>/dev/null
    kill $TUNNEL_PID 2>/dev/null
    wait $DJANGO_PID 2>/dev/null
    wait $TUNNEL_PID 2>/dev/null
    echo "  Done!"
}
trap cleanup EXIT INT TERM

wait $DJANGO_PID $TUNNEL_PID
