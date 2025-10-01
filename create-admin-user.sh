#!/bin/bash

# WAF System Admin User Creation Script
echo "🚀 Creating WAF System Admin User..."

# Default credentials
USERNAME="admin"
EMAIL="admin@waf.local"
PASSWORD="admin123"

# Check if custom credentials are provided
if [ ! -z "$1" ]; then
    USERNAME="$1"
fi

if [ ! -z "$2" ]; then
    EMAIL="$2"
fi

if [ ! -z "$3" ]; then
    PASSWORD="$3"
fi

echo "Creating superuser with:"
echo "  Username: $USERNAME"
echo "  Email: $EMAIL"
echo "  Password: $PASSWORD"
echo ""

# Create the superuser using Django shell
docker-compose exec django python -c "
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowbiteapp.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
if User.objects.filter(username='$USERNAME').exists():
    print('Superuser \"$USERNAME\" already exists!')
else:
    User.objects.create_superuser(
        username='$USERNAME',
        email='$EMAIL',
        password='$PASSWORD'
    )
    print('Superuser \"$USERNAME\" created successfully!')
"

echo ""
echo "✅ Admin user creation completed!"
echo ""
echo "🌐 Access your admin panel at:"
echo "   http://localhost:8000/admin/"
echo ""
echo "📋 Login credentials:"
echo "   Username: $USERNAME"
echo "   Password: $PASSWORD"
echo ""
echo "💡 You can also access the main application at:"
echo "   http://localhost:8000/"
echo ""
echo "📊 Analytics dashboard at:"
echo "   http://localhost:5601"