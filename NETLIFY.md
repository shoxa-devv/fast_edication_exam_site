# Netlify deployment (Fast Education)

Netlify’da faqat **frontend** ishlaydi. **Backend (Django)** alohida deploy qilinadi va Netlify’dagi `BACKEND_URL` orqali ulanishi kerak.

---

## Tez yo‘l: Backend’ni Render’da ishga tushirish

1. **Render.com** ga kiring: https://dashboard.render.com  
2. **New → Blueprint**  
3. Reponi ulang (GitHub) va **render.yaml** faylini tanlang  
4. **Apply** qiling — Render Docker orqali backend’ni deploy qiladi  
5. Tugagach, **Service** sahifasida URL ko‘rinadi, masalan:  
   `https://fast-education-api.onrender.com`  
6. Shu URL ni **nusxalang** (oxirida `/` bo‘lmasin)

---

## Netlify’da BACKEND_URL o‘rnatish

1. **Netlify** → saytingiz → **Site configuration** → **Environment variables**  
2. **Add a variable** → **Key:** `BACKEND_URL`  
3. **Value:** Render’dan olgan URL (masalan: `https://fast-education-api.onrender.com`)  
4. **Save**  
5. **Deploys** → **Trigger deploy** → **Deploy site**

Shundan keyin forma ishlashi kerak.

---

## Eslatmalar

- **Render free tier:** 15 daqiqa ishlatilmasa server “uyquga” ketadi; birinchi so‘rov 1–2 daqiqa kechikishi mumkin.  
- **CORS/CSRF:** Django settings’da Netlify domeni qo‘shilgan (`*.netlify.app`, `cozy-salamander-4693b4.netlify.app`).  
- Agar xato davom etsa: Netlify’da **Deploys** da so‘nggi deploy’da **BACKEND_URL** bor-yo‘qligini tekshiring va backend URL’ni brauzerda ochib `/api/levels/` ni tekshiring.
