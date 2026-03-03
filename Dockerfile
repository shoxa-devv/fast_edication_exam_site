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
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for persistence
RUN mkdir -p staticfiles media data

# Expose port
EXPOSE 8000

# Entrypoint script
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
