FROM python:3.12-slim

# Don't buffer Python output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (curl for cloudflared)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy everything (backend and frontend)
COPY . .

# Create directories for persistence (inside backend since settings.py uses BASE_DIR)
RUN mkdir -p backend/staticfiles backend/media backend/data

# Make entrypoint executable
RUN chmod +x backend/entrypoint.sh

# Change working directory to backend to run manage.py easily
WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
