#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     Fast Education Exam Site             ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

echo "  Running migrations..."
python manage.py makemigrations --noinput 2>&1 | tail -3
python manage.py migrate --run-syncdb 2>&1 | tail -3

echo "  Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tail -1

echo "  Setting up data..."
python create_admin.py 2>&1

# Setup cloudflared
CLOUDFLARED="/tmp/cloudflared"
PORT=${PORT:-8000}

if [ ! -x "$CLOUDFLARED" ]; then
    echo "  Downloading cloudflared tunnel..."
    curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$CLOUDFLARED"
    chmod +x "$CLOUDFLARED"
fi

echo ""
echo "  Starting Gunicorn server..."
# Run gunicorn in background but redirect to stdout so docker logs can see it
gunicorn exam_site.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 &
GUNICORN_PID=$!
sleep 2

echo "  Starting public tunnel..."
TUNNEL_LOG="/tmp/cloudflared_output.log"
# Start cloudflared in background
$CLOUDFLARED tunnel --url "http://localhost:$PORT" > "$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!

# Wait for URL - improve parsing to avoid 'api.trycloudflare.com'
PUBLIC_URL=""
echo "  Waiting for public URL..."
for i in $(seq 1 30); do
    sleep 1
    # Find the link that is NOT api.trycloudflare.com
    PUBLIC_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | grep -v "api.trycloudflare.com" | head -1)
    if [ -n "$PUBLIC_URL" ]; then
        break
    fi
done

if [ -z "$PUBLIC_URL" ]; then
    PUBLIC_URL="(link generated but not captured - check logs)"
    echo "  ! Cloudflare log content:"
    cat "$TUNNEL_LOG"
fi

echo ""
echo "  ┌──────────────────────────────────────────────────────────┐"
echo "  │                                                          │"
echo "  │  🌐 SAYT:    $PUBLIC_URL"
echo "  │  🔐 ADMIN:   ${PUBLIC_URL}/admin"
echo "  │  👤 LOGIN:   admin / admin123                            │"
echo "  │                                                          │"
echo "  │  Shu linkni do'stlaringizga yuboring!                    │"
echo "  │                                                          │"
echo "  └──────────────────────────────────────────────────────────┘"
echo ""

cleanup() {
    echo "  Stopping services..."
    kill $GUNICORN_PID $TUNNEL_PID 2>/dev/null
}
trap cleanup EXIT INT TERM

# Wait for gunicorn to stay running
wait $GUNICORN_PID


