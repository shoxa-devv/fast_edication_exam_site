#!/usr/bin/env python
"""
Unified run script - starts both Django backend and serves frontend
Run with: python app.py
"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_django():
    """Run Django development server"""
    os.chdir(BASE_DIR)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_site.settings')
    
    # Run migrations first
    print("Running database migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--run-syncdb'], check=False)
    
    # Create superuser and load initial data
    print("Setting up initial data...")
    try:
        subprocess.run([sys.executable, 'create_admin.py'], check=False)
    except:
        pass
    
    print("\n" + "="*60)
    print("🚀 Starting Django Backend Server...")
    print("="*60)
    print("📍 Backend URL: http://localhost:8000")
    print("📍 Admin Panel: http://localhost:8000/admin")
    print("📍 API: http://localhost:8000/api/")
    print("="*60 + "\n")
    
    # Start Django server
    subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])


def main():
    """Main function to start everything"""
    print("\n" + "="*60)
    print("🎓 Fast Education Exam Site - Starting...")
    print("="*60 + "\n")
    
    # Check if we're in the right directory
    if not (BASE_DIR / 'manage.py').exists():
        print("❌ Error: manage.py not found. Please run from backend directory.")
        sys.exit(1)
    
    # Start Django in main thread (blocking)
    try:
        run_django()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)


if __name__ == '__main__':
    main()
