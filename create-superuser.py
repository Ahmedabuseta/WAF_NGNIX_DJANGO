#!/usr/bin/env python
"""
Script to create a Django superuser
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

# Create superuser
username = 'admin'
email = 'admin@waf.local'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists!")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"Superuser '{username}' created successfully!")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("\nYou can now login to the admin panel at: http://localhost:8000/admin/")