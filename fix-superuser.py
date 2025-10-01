#!/usr/bin/env python
"""
Script to fix Django superuser for custom User model
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowbiteapp.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing admin user if it exists
if User.objects.filter(email='admin@waf.local').exists():
    User.objects.filter(email='admin@waf.local').delete()
    print("Removed existing admin user")

# Create superuser with email as username
User.objects.create_superuser(
    email='admin@waf.local',
    username='admin',
    password='admin123'
)

print("Superuser created successfully!")
print("Login credentials:")
print("  Email: admin@waf.local")
print("  Password: admin123")
print("\nYou can now login to the admin panel at: http://localhost:8000/admin/")
print("Use the EMAIL as the username field!")