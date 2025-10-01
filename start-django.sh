#!/bin/bash

# Simple Django startup script
echo "Starting Django application..."

# Run migrations
python manage.py migrate

# Start Django development server
python manage.py runserver 0.0.0.0:8000