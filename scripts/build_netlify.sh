#!/usr/bin/env bash
# Netlify build: export static frontend from Django app to public/
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC="$ROOT/backend/static"
PUBLIC="$ROOT/public"

echo "Building static site for Netlify..."
rm -rf "$PUBLIC"
mkdir -p "$PUBLIC"/{css,js,images/levels}

cp -r "$STATIC/css/"* "$PUBLIC/css/" 2>/dev/null || true
cp -r "$STATIC/js/"* "$PUBLIC/js/" 2>/dev/null || true
cp -r "$STATIC/images/"* "$PUBLIC/images/" 2>/dev/null || true

# Rewrite index.html: remove Django template tags, use static paths
sed -e "s|{% load static %}||g" \
    -e "s|{% static 'css/style.css' %}|/css/style.css|g" \
    -e "s|{% static 'js/app.js' %}|/js/app.js|g" \
    -e "s|{% static 'images/favicon.png' %}|/images/favicon.png|g" \
    -e "s|{% static 'images/logo.png' %}|/images/logo.png|g" \
    -e "s|{% static 'images/levels/\([^']*\)' %}|/images/levels/\1|g" \
    "$STATIC/index.html" > "$PUBLIC/index.html"

# SPA fallback: /api/* -> proxy, everything else -> index.html
# Order matters: first matching rule wins
printf '%s\n' '/api/*  /.netlify/functions/api-proxy?path=:splat  200' '/*  /index.html  200' > "$PUBLIC/_redirects"

echo "Build complete: $PUBLIC"
ls -la "$PUBLIC"
