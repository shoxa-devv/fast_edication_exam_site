"""
Create admin user and load initial data.
Run after migrations: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_site.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.management.commands.load_initial_data import load_data

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    print("Creating default admin user...")
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("  Admin created! (username: admin, password: admin123)")
else:
    print("  Admin user already exists.")

print("Loading initial data...")
load_data()
print("Done!")
