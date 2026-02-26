# Netlify deployment (Fast Education)

This project is **Django backend + static SPA frontend**. Netlify serves the **static frontend** and **proxies /api/* to your Django backend** via a serverless function.

## 1. Deploy Django backend somewhere

Deploy the Django app (e.g. Railway, Render, Fly.io) and note the public URL, e.g.:
- `https://your-app.railway.app`
- `https://your-app.onrender.com`

Do **not** add `/api` or a trailing slash — the proxy adds `/api/...` itself.

## 2. Set environment variable on Netlify

1. Netlify → your site → **Site configuration** → **Environment variables**
2. Add variable:
   - **Key:** `BACKEND_URL`
   - **Value:** your Django site URL (e.g. `https://your-app.railway.app`)
3. Save. Trigger a new deploy (Deploys → Trigger deploy) so the function sees the variable.

## 3. Deploy frontend on Netlify

- **Build command:** `bash scripts/build_netlify.sh`
- **Publish directory:** `public`
- **Functions directory:** `netlify/functions` (from netlify.toml)

After deploy, the site will call `/api/...`; Netlify will proxy these requests to `BACKEND_URL/api/...`.

## If you see "Server bilan bog'lanib bo'lmadi / Ошибка соединения"

- **BACKEND_URL is not set** → Set it in Netlify environment variables and redeploy.
- **Backend is not running** → Start your Django app (e.g. on Railway/Render) and check the URL.
- **CORS** → Django must allow your Netlify domain in `CORS_ALLOWED_ORIGINS` or `CORS_ALLOW_ALL_ORIGINS` (see backend settings).

## Folder layout after build

```
public/
  index.html
  _redirects   # /* -> /index.html 200
  css/, js/, images/

netlify/functions/
  api-proxy.js  # Proxies /api/* to BACKEND_URL
```
